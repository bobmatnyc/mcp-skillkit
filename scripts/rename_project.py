#!/usr/bin/env python3
"""Script to rename mcp-skillset to mcp-skillset across the entire project.

This script performs intelligent find-and-replace operations across:
- Python source files
- Configuration files (TOML, YAML, JSON)
- Documentation (Markdown, RST)
- Shell scripts and Makefiles
- Test files

It handles different casing variations:
- mcp-skillset → mcp-skillset
- mcp_skillset → mcp_skillset
- MCP Skillset → MCP Skillset
- MCP SkillSet → MCP SkillSet
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directories to exclude from renaming
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "*.egg-info",
    "node_modules",
}

# File patterns to process
INCLUDE_PATTERNS = [
    "*.py",
    "*.toml",
    "*.yaml",
    "*.yml",
    "*.json",
    "*.md",
    "*.rst",
    "*.txt",
    "*.sh",
    "*.bash",
    "*.zsh",
    "*.fish",
    "Makefile",
    "*.mk",
]

# Replacement mappings (old → new)
REPLACEMENTS = [
    (r"mcp-skillset", "mcp-skillset"),
    (r"mcp_skillset", "mcp_skillset"),
    (r"MCP Skillset", "MCP Skillset"),
    (r"MCP SkillSet", "MCP SkillSet"),
    (r"SkillSet", "SkillSet"),
    (r"skillset", "skillset"),
]


def should_process_file(file_path: Path) -> bool:
    """Check if file should be processed for renaming.

    Args:
        file_path: Path to file to check

    Returns:
        True if file should be processed, False otherwise
    """
    # Skip if in excluded directory
    for exclude in EXCLUDE_DIRS:
        if exclude in file_path.parts:
            return False

    # Check if matches include patterns
    for pattern in INCLUDE_PATTERNS:
        if file_path.match(pattern):
            return True

    return False


def process_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """Process a single file, applying all replacements.

    Args:
        file_path: Path to file to process
        dry_run: If True, show what would be changed without modifying files

    Returns:
        Tuple of (was_modified, num_replacements)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        # Skip binary files or files we can't read
        return False, 0

    original_content = content
    total_replacements = 0

    # Apply all replacements
    for old, new in REPLACEMENTS:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            total_replacements += count

    # Check if file was modified
    if content != original_content:
        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        return True, total_replacements

    return False, 0


def find_files_to_process() -> List[Path]:
    """Find all files that should be processed.

    Returns:
        List of file paths to process
    """
    files = []

    for pattern in INCLUDE_PATTERNS:
        for file_path in PROJECT_ROOT.rglob(pattern):
            if file_path.is_file() and should_process_file(file_path):
                files.append(file_path)

    return sorted(files)


def main():
    """Main entry point for the rename script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Rename mcp-skillset to mcp-skillset across the project"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    args = parser.parse_args()

    print("🔍 Finding files to process...")
    files = find_files_to_process()
    print(f"Found {len(files)} files to process\n")

    if args.dry_run:
        print("🔬 DRY RUN MODE - No files will be modified\n")

    modified_files = []
    total_replacements = 0

    for file_path in files:
        relative_path = file_path.relative_to(PROJECT_ROOT)
        was_modified, num_replacements = process_file(file_path, dry_run=args.dry_run)

        if was_modified:
            modified_files.append(relative_path)
            total_replacements += num_replacements
            status = "Would modify" if args.dry_run else "Modified"
            print(f"{status}: {relative_path} ({num_replacements} replacements)")

    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(files)}")
    print(f"   Files modified: {len(modified_files)}")
    print(f"   Total replacements: {total_replacements}")

    if args.dry_run:
        print(f"\n✅ Dry run complete. Run without --dry-run to apply changes.")
    else:
        print(f"\n✅ Rename complete!")


if __name__ == "__main__":
    main()
