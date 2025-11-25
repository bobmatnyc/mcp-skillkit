"""Prompt enrichment service for injecting relevant skill instructions.

Design Decision: Keyword-Based Skill Discovery

Rationale: Extract meaningful keywords from user prompts to search for relevant
skills, then format enriched prompts with instructions. This provides context-aware
assistance by automatically finding and injecting skill knowledge.

Architecture:
- Keyword Extraction: Stop word removal + technical term identification
- Skill Search: Integration with existing SkillManager search
- Prompt Formatting: Simple vs. detailed output formats
- Output Options: stdout, file, clipboard

Trade-offs:
- Simplicity: Basic keyword extraction vs. NLP-based entity recognition
- Performance: Fast keyword matching vs. slower semantic analysis
- Accuracy: May miss some context vs. perfect understanding

Extension Points:
- Advanced NLP for better keyword extraction (spaCy, NLTK)
- Semantic search integration with vector embeddings
- Custom prompt templates per use case
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from mcp_skills.models.skill import Skill


if TYPE_CHECKING:
    from mcp_skills.services.skill_manager import SkillManager


logger = logging.getLogger(__name__)


# Common English stop words to filter out
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "will",
    "with",
    "this",
    "can",
    "should",
    "would",
    "could",
    "i",
    "we",
    "you",
    "they",
    "what",
    "which",
    "who",
    "when",
    "where",
    "why",
    "how",
}

# Technical terms and action verbs to prioritize
TECHNICAL_TERMS = {
    "api",
    "endpoint",
    "test",
    "testing",
    "debug",
    "debugging",
    "code",
    "coding",
    "deploy",
    "deployment",
    "build",
    "compile",
    "run",
    "execute",
    "validate",
    "validation",
    "auth",
    "authentication",
    "database",
    "db",
    "server",
    "client",
    "frontend",
    "backend",
    "rest",
    "graphql",
    "async",
    "sync",
    "python",
    "javascript",
    "typescript",
    "java",
    "rust",
    "go",
    "ruby",
    "php",
    "fastapi",
    "flask",
    "django",
    "react",
    "vue",
    "angular",
    "pytest",
    "jest",
    "unit",
    "integration",
    "e2e",
}

ACTION_VERBS = {
    "create",
    "build",
    "implement",
    "add",
    "write",
    "develop",
    "fix",
    "refactor",
    "optimize",
    "improve",
    "test",
    "deploy",
    "configure",
    "setup",
    "install",
    "update",
    "delete",
    "remove",
    "validate",
    "verify",
    "check",
    "analyze",
    "debug",
    "review",
    "document",
}


@dataclass
class EnrichedPrompt:
    """Result of prompt enrichment.

    Attributes:
        original_prompt: Original user prompt
        keywords: Extracted keywords used for search
        skills_found: List of relevant skills discovered
        enriched_text: Formatted enriched prompt
        detailed: Whether detailed format was used
    """

    original_prompt: str
    keywords: list[str]
    skills_found: list[Skill]
    enriched_text: str
    detailed: bool


class PromptEnricher:
    """Enhance user prompts by injecting relevant skill instructions.

    Workflow:
    1. Extract keywords from user prompt
    2. Search for relevant skills using keywords
    3. Format enriched prompt with skill instructions
    4. Output to stdout, file, or clipboard

    Example:
        >>> enricher = PromptEnricher(skill_manager)
        >>> result = enricher.enrich(
        ...     "Create a FastAPI endpoint with validation",
        ...     max_skills=3,
        ...     threshold=0.7
        ... )
        >>> print(result.enriched_text)
    """

    def __init__(self, skill_manager: "SkillManager") -> None:
        """Initialize prompt enricher.

        Args:
            skill_manager: SkillManager instance for searching skills
        """
        self.skill_manager = skill_manager

    def extract_keywords(self, prompt: str) -> list[str]:
        """Extract meaningful keywords from prompt.

        Extraction Strategy:
        1. Convert to lowercase
        2. Remove stop words
        3. Prioritize technical terms and action verbs
        4. Extract quoted phrases as single keywords
        5. Keep compound terms (e.g., "user input")

        Args:
            prompt: User prompt text

        Returns:
            List of extracted keywords sorted by relevance

        Performance:
        - Time Complexity: O(n) where n = number of words
        - Space Complexity: O(k) where k = number of keywords

        Example:
            >>> enricher.extract_keywords("Create FastAPI endpoint with validation")
            ['fastapi', 'endpoint', 'validation', 'create']
        """
        keywords: list[str] = []

        # Extract quoted phrases first (preserve as single keyword)
        quoted_pattern = r'"([^"]+)"'
        quoted_matches = re.findall(quoted_pattern, prompt)
        for phrase in quoted_matches:
            keywords.append(phrase.lower().strip())

        # Remove quoted sections from prompt for further processing
        prompt_without_quotes = re.sub(quoted_pattern, "", prompt)

        # Tokenize remaining text (split on whitespace and common punctuation)
        words = re.findall(r"\b\w+\b", prompt_without_quotes.lower())

        # Build keyword list with prioritization
        prioritized: list[str] = []
        regular: list[str] = []

        for word in words:
            # Skip stop words and very short words
            if word in STOP_WORDS or len(word) < 2:
                continue

            # Prioritize technical terms and action verbs
            if word in TECHNICAL_TERMS or word in ACTION_VERBS:
                if word not in prioritized:
                    prioritized.append(word)
            elif word not in regular:
                regular.append(word)

        # Combine: quoted phrases, prioritized terms, then regular keywords
        keywords.extend(prioritized)
        keywords.extend(regular)

        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        logger.debug(f"Extracted {len(unique_keywords)} keywords from prompt")
        return unique_keywords

    def search_skills(self, keywords: list[str], max_skills: int = 3) -> list[Skill]:
        """Search for relevant skills using keywords.

        Uses SkillManager.search_skills() with keyword-based query.

        Args:
            keywords: List of extracted keywords
            max_skills: Maximum number of skills to return

        Returns:
            List of relevant Skill objects

        Performance Note:
        - Delegates to SkillManager which does O(n*m) text matching
        - Results are already sorted by relevance score

        Example:
            >>> skills = enricher.search_skills(['fastapi', 'validation'], max_skills=3)
            >>> len(skills)
            3
        """
        if not keywords:
            logger.warning("No keywords provided for skill search")
            return []

        # Join keywords into search query
        query = " ".join(keywords)

        logger.debug(f"Searching skills with query: {query}")

        # Use SkillManager's search (already implements relevance scoring)
        skills = self.skill_manager.search_skills(query, limit=max_skills)

        logger.info(f"Found {len(skills)} relevant skills")
        return skills

    def format_simple(self, prompt: str, skills: list[Skill]) -> str:
        """Format enriched prompt in simple mode (brief instructions).

        Format:
        ```
        [Original Prompt]

        ---
        Relevant Skills:

        1. [Skill Name]
        [Skill Instructions - truncated to 200 chars]

        2. [Skill Name]
        [Skill Instructions - truncated to 200 chars]
        ```

        Args:
            prompt: Original user prompt
            skills: List of relevant skills

        Returns:
            Formatted enriched prompt string
        """
        lines = [prompt, "", "---", "Relevant Skills:", ""]

        for i, skill in enumerate(skills, 1):
            lines.append(f"{i}. {skill.name}")

            # Truncate instructions to 200 chars
            instructions = skill.instructions[:200]
            if len(skill.instructions) > 200:
                instructions += "..."

            lines.append(instructions)
            lines.append("")  # Blank line between skills

        return "\n".join(lines)

    def format_detailed(self, prompt: str, skills: list[Skill]) -> str:
        """Format enriched prompt in detailed mode (full instructions).

        Format:
        ```
        [Original Prompt]

        ---
        Context from MCP SkillSet:

        ## [Skill 1 Name]
        Category: [category]
        [Full instructions]

        ## [Skill 2 Name]
        Category: [category]
        [Full instructions]
        ```

        Args:
            prompt: Original user prompt
            skills: List of relevant skills

        Returns:
            Formatted enriched prompt string with full details
        """
        lines = [prompt, "", "---", "Context from MCP SkillSet:", ""]

        for skill in skills:
            lines.append(f"## {skill.name}")
            lines.append(f"Category: {skill.category}")
            lines.append("")
            lines.append(skill.instructions)
            lines.append("")  # Blank line between skills

        return "\n".join(lines)

    def enrich(
        self,
        prompt: str,
        max_skills: int = 3,
        detailed: bool = False,
    ) -> EnrichedPrompt:
        """Enrich a prompt with relevant skill instructions.

        Complete workflow:
        1. Extract keywords from prompt
        2. Search for relevant skills
        3. Format enriched prompt (simple or detailed)

        Args:
            prompt: Original user prompt
            max_skills: Maximum number of skills to include
            detailed: Use detailed format (full instructions)

        Returns:
            EnrichedPrompt with all enrichment data

        Error Handling:
        - Empty prompt: Return original prompt unchanged
        - No skills found: Return prompt with notice
        - Search failure: Log error, return original prompt

        Example:
            >>> result = enricher.enrich(
            ...     "Create REST API with auth",
            ...     max_skills=3,
            ...     detailed=False
            ... )
            >>> print(result.enriched_text)
        """
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided")
            return EnrichedPrompt(
                original_prompt=prompt,
                keywords=[],
                skills_found=[],
                enriched_text=prompt,
                detailed=detailed,
            )

        try:
            # Step 1: Extract keywords
            keywords = self.extract_keywords(prompt)

            if not keywords:
                logger.info("No keywords extracted from prompt")
                return EnrichedPrompt(
                    original_prompt=prompt,
                    keywords=[],
                    skills_found=[],
                    enriched_text=prompt,
                    detailed=detailed,
                )

            # Step 2: Search for skills
            skills = self.search_skills(keywords, max_skills)

            if not skills:
                logger.info("No relevant skills found")
                # Return prompt with notice
                enriched = f"{prompt}\n\n---\nNo relevant skills found. Try different keywords."
                return EnrichedPrompt(
                    original_prompt=prompt,
                    keywords=keywords,
                    skills_found=[],
                    enriched_text=enriched,
                    detailed=detailed,
                )

            # Step 3: Format enriched prompt
            if detailed:
                enriched_text = self.format_detailed(prompt, skills)
            else:
                enriched_text = self.format_simple(prompt, skills)

            return EnrichedPrompt(
                original_prompt=prompt,
                keywords=keywords,
                skills_found=skills,
                enriched_text=enriched_text,
                detailed=detailed,
            )

        except Exception as e:
            logger.error(f"Failed to enrich prompt: {e}")
            # Return original prompt on error
            return EnrichedPrompt(
                original_prompt=prompt,
                keywords=[],
                skills_found=[],
                enriched_text=prompt,
                detailed=detailed,
            )

    def save_to_file(self, enriched_text: str, output_path: Path) -> None:
        """Save enriched prompt to file.

        Args:
            enriched_text: Enriched prompt text
            output_path: Path to output file

        Raises:
            OSError: If file write fails

        Example:
            >>> enricher.save_to_file(result.enriched_text, Path("prompt.md"))
        """
        try:
            output_path.write_text(enriched_text, encoding="utf-8")
            logger.info(f"Saved enriched prompt to {output_path}")
        except OSError as e:
            logger.error(f"Failed to save to {output_path}: {e}")
            raise

    def copy_to_clipboard(self, enriched_text: str) -> bool:
        """Copy enriched prompt to system clipboard.

        Requires pyperclip package.

        Args:
            enriched_text: Enriched prompt text

        Returns:
            True if successful, False if pyperclip unavailable or error

        Error Handling:
        - pyperclip not installed: Return False, log warning
        - Clipboard access error: Return False, log error

        Example:
            >>> success = enricher.copy_to_clipboard(result.enriched_text)
            >>> if success:
            ...     print("Copied to clipboard!")
        """
        try:
            import pyperclip

            pyperclip.copy(enriched_text)
            logger.info("Copied enriched prompt to clipboard")
            return True
        except ImportError:
            logger.warning("pyperclip not installed - clipboard copy unavailable")
            return False
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            return False
