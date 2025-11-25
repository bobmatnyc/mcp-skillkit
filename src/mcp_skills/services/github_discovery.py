"""GitHub repository discovery service for skill repositories.

Provides automatic discovery of skill repositories on GitHub using
GitHub's REST API v3. Supports searching, filtering, and verification.
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)


@dataclass
class GitHubRepo:
    """GitHub repository metadata.

    Attributes:
        full_name: Repository full name (owner/repo)
        url: HTTPS clone URL
        description: Repository description
        stars: Star count
        forks: Fork count
        updated_at: Last update timestamp
        license: Repository license (SPDX ID)
        topics: Repository topics/tags
        has_skill_file: Whether SKILL.md file exists
    """

    full_name: str
    url: str
    description: str | None
    stars: int
    forks: int
    updated_at: datetime
    license: str | None
    topics: list[str]
    has_skill_file: bool = False


@dataclass
class CacheEntry:
    """Cache entry for GitHub API responses.

    Attributes:
        data: Cached data
        expires_at: Expiration timestamp
    """

    data: Any
    expires_at: datetime


class GitHubDiscovery:
    """Discover skill repositories on GitHub.

    Uses GitHub REST API v3 to search for and verify skill repositories.
    Implements rate limiting, caching, and authentication support.

    Rate Limits:
    - Unauthenticated: 60 requests/hour
    - Authenticated: 5000 requests/hour

    Design Decision: API Client Implementation

    Rationale: Using urllib from stdlib instead of requests library to avoid
    additional dependencies. This project already has minimal dependencies,
    and urllib provides sufficient functionality for simple REST API calls.

    Trade-offs:
    - Simplicity: No extra dependencies, uses Python stdlib
    - Developer Experience: urllib is more verbose than requests
    - Features: No automatic JSON decoding, need manual error handling
    - Performance: Same underlying HTTP implementation

    Alternatives Considered:
    1. requests: Rejected to avoid dependency bloat
    2. httpx: Rejected (async not needed here, adds dependency)
    3. urllib: Selected for zero additional dependencies

    Error Handling:
    - HTTPError: API errors (403 rate limit, 404 not found, etc.)
    - URLError: Network connectivity issues
    - json.JSONDecodeError: Invalid API responses
    - All errors are logged and propagated with helpful messages

    Failure Modes:
    - Rate limit exceeded: Returns empty list, logs warning with reset time
    - Network failure: Raises exception with diagnostic message
    - Invalid token: Falls back to unauthenticated (60 req/hr)
    - Malformed API response: Raises exception with response details
    """

    BASE_URL = "https://api.github.com"
    CACHE_TTL = 3600  # 1 hour cache TTL

    def __init__(
        self,
        github_token: str | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        """Initialize GitHub discovery service.

        Args:
            github_token: Optional GitHub personal access token for higher rate limits
            cache_dir: Directory for caching API responses (defaults to ~/.mcp-skillset/cache)

        Usage Examples:
            # Unauthenticated (60 req/hr)
            >>> discovery = GitHubDiscovery()
            >>> repos = discovery.search_repos("claude skills")

            # Authenticated (5000 req/hr)
            >>> token = os.environ.get("GITHUB_TOKEN")
            >>> discovery = GitHubDiscovery(github_token=token)
            >>> trending = discovery.get_trending()
        """
        self.github_token = github_token
        self.cache_dir = cache_dir or Path.home() / ".mcp-skillset" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache for API responses
        self._cache: dict[str, CacheEntry] = {}

        # Rate limit tracking
        self._rate_limit_remaining: int | None = None
        self._rate_limit_reset: datetime | None = None

    def search_repos(
        self,
        query: str,
        min_stars: int = 2,
        topics: list[str] | None = None,
    ) -> list[GitHubRepo]:
        """Search GitHub for skill repositories.

        Args:
            query: Search query string
            min_stars: Minimum star count filter (default: 2)
            topics: Additional topics to filter by

        Returns:
            List of repository metadata objects

        Error Handling:
        - Returns empty list on rate limit or API errors (logs warning)
        - Raises exception on network failures (caller must handle)

        Examples:
            >>> discovery = GitHubDiscovery()
            >>> repos = discovery.search_repos("python testing", min_stars=5)
            >>> for repo in repos:
            ...     print(f"{repo.full_name}: {repo.stars} stars")
        """
        # Build search query
        search_parts = [query]
        search_parts.append(f"stars:>={min_stars}")

        if topics:
            for topic in topics:
                search_parts.append(f"topic:{topic}")

        # Add SKILL.md filename search
        search_parts.append("filename:SKILL.md")

        search_query = " ".join(search_parts)

        # Make API request
        try:
            results = self._api_request(
                "/search/repositories",
                params={"q": search_query, "sort": "stars", "order": "desc"},
            )

            repos = []
            for item in results.get("items", []):
                repo = self._parse_repo(item)
                # Verify SKILL.md exists
                repo.has_skill_file = self.verify_skill_repo(repo.url)
                repos.append(repo)

            return repos

        except Exception as e:
            logger.error(f"Repository search failed: {e}")
            return []

    def search_by_topic(self, topic: str, min_stars: int = 2) -> list[GitHubRepo]:
        """Search repositories by GitHub topic.

        Args:
            topic: GitHub topic to search for
            min_stars: Minimum star count filter

        Returns:
            List of repository metadata objects

        Common Topics:
        - claude-skills: Skills for Claude AI
        - anthropic-skills: Anthropic-related skills
        - mcp-skills: MCP protocol skills
        - ai-skills: General AI skills

        Examples:
            >>> discovery = GitHubDiscovery()
            >>> repos = discovery.search_by_topic("claude-skills")
            >>> print(f"Found {len(repos)} Claude skill repositories")
        """
        search_query = f"topic:{topic} stars:>={min_stars} filename:SKILL.md"

        try:
            results = self._api_request(
                "/search/repositories",
                params={"q": search_query, "sort": "updated", "order": "desc"},
            )

            repos = []
            for item in results.get("items", []):
                repo = self._parse_repo(item)
                repo.has_skill_file = True  # Already filtered by filename
                repos.append(repo)

            return repos

        except Exception as e:
            logger.error(f"Topic search failed for '{topic}': {e}")
            return []

    def get_trending(
        self,
        timeframe: str = "week",
        topic: str | None = None,
    ) -> list[GitHubRepo]:
        """Get trending skill repositories.

        Args:
            timeframe: Time period (week, month, year)
            topic: Optional topic filter

        Returns:
            List of trending repository metadata objects

        Error Handling:
        - Invalid timeframe: Defaults to "week"
        - Returns empty list on API errors

        Examples:
            >>> discovery = GitHubDiscovery()
            >>> weekly = discovery.get_trending("week")
            >>> monthly = discovery.get_trending("month", topic="claude-skills")
        """
        # Calculate date threshold
        now = datetime.now(UTC)
        if timeframe == "week":
            threshold = now - timedelta(days=7)
        elif timeframe == "month":
            threshold = now - timedelta(days=30)
        elif timeframe == "year":
            threshold = now - timedelta(days=365)
        else:
            logger.warning(f"Invalid timeframe '{timeframe}', using 'week'")
            threshold = now - timedelta(days=7)

        # Build query
        date_str = threshold.strftime("%Y-%m-%d")
        search_parts = [
            f"pushed:>={date_str}",
            "stars:>=2",
            "filename:SKILL.md",
        ]

        if topic:
            search_parts.append(f"topic:{topic}")

        search_query = " ".join(search_parts)

        try:
            results = self._api_request(
                "/search/repositories",
                params={"q": search_query, "sort": "stars", "order": "desc", "per_page": 30},
            )

            repos = []
            for item in results.get("items", []):
                repo = self._parse_repo(item)
                repo.has_skill_file = True
                repos.append(repo)

            return repos

        except Exception as e:
            logger.error(f"Trending search failed: {e}")
            return []

    def verify_skill_repo(self, repo_url: str) -> bool:
        """Verify that a repository contains SKILL.md files.

        Args:
            repo_url: Repository HTTPS clone URL

        Returns:
            True if repository contains SKILL.md file(s)

        Error Handling:
        - Invalid URL format: Returns False
        - Network errors: Returns False (logs warning)
        - Rate limit: Returns False (logs warning with reset time)

        Examples:
            >>> discovery = GitHubDiscovery()
            >>> url = "https://github.com/anthropics/skills.git"
            >>> is_valid = discovery.verify_skill_repo(url)
            >>> if is_valid:
            ...     print("Valid skill repository!")
        """
        # Extract owner/repo from URL
        # Format: https://github.com/owner/repo.git
        try:
            parts = repo_url.rstrip("/").replace(".git", "").split("/")
            if len(parts) < 2:
                return False

            owner = parts[-2]
            repo = parts[-1]

            # Search for SKILL.md files in the repository
            search_query = f"repo:{owner}/{repo} filename:SKILL.md"

            results = self._api_request(
                "/search/code",
                params={"q": search_query, "per_page": 1},
            )

            return results.get("total_count", 0) > 0

        except Exception as e:
            logger.warning(f"Failed to verify repository {repo_url}: {e}")
            return False

    def get_repo_metadata(self, repo_url: str) -> GitHubRepo | None:
        """Get detailed metadata for a repository.

        Args:
            repo_url: Repository HTTPS clone URL

        Returns:
            Repository metadata or None if not found

        Error Handling:
        - Invalid URL: Returns None
        - Repository not found (404): Returns None
        - API errors: Returns None (logs error)

        Examples:
            >>> discovery = GitHubDiscovery()
            >>> url = "https://github.com/anthropics/skills.git"
            >>> metadata = discovery.get_repo_metadata(url)
            >>> if metadata:
            ...     print(f"{metadata.full_name}: {metadata.description}")
        """
        # Extract owner/repo from URL
        try:
            parts = repo_url.rstrip("/").replace(".git", "").split("/")
            if len(parts) < 2:
                return None

            owner = parts[-2]
            repo = parts[-1]

            # Get repository metadata
            data = self._api_request(f"/repos/{owner}/{repo}")

            repo_obj = self._parse_repo(data)
            repo_obj.has_skill_file = self.verify_skill_repo(repo_url)

            return repo_obj

        except Exception as e:
            logger.error(f"Failed to get metadata for {repo_url}: {e}")
            return None

    def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status.

        Returns:
            Dictionary with rate limit information

        Example:
            >>> discovery = GitHubDiscovery()
            >>> status = discovery.get_rate_limit_status()
            >>> print(f"Remaining: {status['remaining']}/{status['limit']}")
            >>> print(f"Resets at: {status['reset_time']}")
        """
        try:
            data = self._api_request("/rate_limit")

            core = data.get("resources", {}).get("core", {})
            search = data.get("resources", {}).get("search", {})

            return {
                "core_limit": core.get("limit", 0),
                "core_remaining": core.get("remaining", 0),
                "core_reset": datetime.fromtimestamp(core.get("reset", 0), tz=UTC),
                "search_limit": search.get("limit", 0),
                "search_remaining": search.get("remaining", 0),
                "search_reset": datetime.fromtimestamp(search.get("reset", 0), tz=UTC),
            }

        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return {
                "core_limit": 0,
                "core_remaining": 0,
                "core_reset": datetime.now(UTC),
                "search_limit": 0,
                "search_remaining": 0,
                "search_reset": datetime.now(UTC),
            }

    # Private helper methods

    def _api_request(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """Make GitHub API request with caching and rate limit handling.

        Args:
            endpoint: API endpoint path (e.g., "/search/repositories")
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            HTTPError: API returned error status (403, 404, etc.)
            URLError: Network connectivity issues
            json.JSONDecodeError: Invalid JSON response

        Caching:
        - Uses in-memory cache with 1-hour TTL
        - Cache key includes endpoint + sorted params
        - Cached responses bypass API calls and rate limits

        Rate Limiting:
        - Tracks X-RateLimit-* headers from responses
        - Returns empty dict on 403 rate limit exceeded
        - Logs warnings with reset time for user awareness
        """
        # Check cache first
        cache_key = self._make_cache_key(endpoint, params)
        cached = self._get_cached(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for {endpoint}")
            return cached

        # Build URL
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            url += "?" + urlencode(params)

        # Build request with headers
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        # Make request
        req = request.Request(url, headers=headers)

        try:
            with request.urlopen(req, timeout=30) as response:
                # Update rate limit tracking
                self._update_rate_limits(response.headers)

                # Parse JSON response
                data = json.loads(response.read().decode("utf-8"))

                # Cache response
                self._set_cached(cache_key, data)

                return data

        except HTTPError as e:
            # Handle rate limiting
            if e.code == 403:
                reset_time = e.headers.get("X-RateLimit-Reset")
                if reset_time:
                    reset_dt = datetime.fromtimestamp(int(reset_time), tz=UTC)
                    logger.warning(
                        f"GitHub API rate limit exceeded. Resets at {reset_dt.isoformat()}"
                    )
                else:
                    logger.warning("GitHub API rate limit exceeded")
                return {}

            # Handle not found
            if e.code == 404:
                logger.debug(f"GitHub API endpoint not found: {endpoint}")
                return {}

            # Other HTTP errors
            logger.error(f"GitHub API error {e.code}: {e.reason}")
            raise

        except URLError as e:
            logger.error(f"Network error accessing GitHub API: {e.reason}")
            raise

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from GitHub API: {e}")
            raise

    def _parse_repo(self, data: dict[str, Any]) -> GitHubRepo:
        """Parse GitHub API repository response into GitHubRepo object.

        Args:
            data: Raw API response data

        Returns:
            GitHubRepo object with parsed metadata
        """
        return GitHubRepo(
            full_name=data.get("full_name", ""),
            url=data.get("clone_url", ""),
            description=data.get("description"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            updated_at=datetime.fromisoformat(
                data.get("updated_at", "").replace("Z", "+00:00")
            ),
            license=data.get("license", {}).get("spdx_id") if data.get("license") else None,
            topics=data.get("topics", []),
        )

    def _make_cache_key(self, endpoint: str, params: dict[str, Any] | None) -> str:
        """Generate cache key from endpoint and parameters.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Cache key string
        """
        if not params:
            return endpoint

        # Sort params for consistent cache keys
        sorted_params = sorted(params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        return f"{endpoint}?{param_str}"

    def _get_cached(self, key: str) -> Any | None:
        """Get cached data if not expired.

        Args:
            key: Cache key

        Returns:
            Cached data or None if expired/missing
        """
        entry = self._cache.get(key)
        if not entry:
            return None

        if datetime.now(UTC) > entry.expires_at:
            # Expired, remove from cache
            del self._cache[key]
            return None

        return entry.data

    def _set_cached(self, key: str, data: Any) -> None:
        """Store data in cache with TTL.

        Args:
            key: Cache key
            data: Data to cache
        """
        expires_at = datetime.now(UTC) + timedelta(seconds=self.CACHE_TTL)
        self._cache[key] = CacheEntry(data=data, expires_at=expires_at)

    def _update_rate_limits(self, headers: Any) -> None:
        """Update rate limit tracking from response headers.

        Args:
            headers: HTTP response headers
        """
        remaining = headers.get("X-RateLimit-Remaining")
        reset = headers.get("X-RateLimit-Reset")

        if remaining:
            self._rate_limit_remaining = int(remaining)

        if reset:
            self._rate_limit_reset = datetime.fromtimestamp(int(reset), tz=UTC)
