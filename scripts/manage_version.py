#!/usr/bin/env python3
"""Version management script for mcp-skills.

Handles version bumping and synchronization across VERSION files.
"""

import argparse
import sys
from pathlib import Path


def get_current_version() -> str:
    """Read current version from VERSION file.

    Returns:
        Current version string
    """
    version_file = Path(__file__).parent.parent / "VERSION"
    if not version_file.exists():
        return "0.1.0"
    return version_file.read_text().strip()


def update_version_files(new_version: str) -> None:
    """Update all VERSION files with new version.

    Args:
        new_version: New version string (e.g., "0.2.0")
    """
    project_root = Path(__file__).parent.parent

    # Update root VERSION
    (project_root / "VERSION").write_text(new_version + "\n")

    # Update package VERSION
    package_version = project_root / "src" / "mcp_skills" / "VERSION"
    if package_version.exists():
        package_version.write_text(new_version + "\n")

    print(f"✅ Updated VERSION files to {new_version}")


def bump_version(part: str) -> str:
    """Bump version number.

    Args:
        part: Version part to bump (major, minor, patch)

    Returns:
        New version string
    """
    current = get_current_version()
    major, minor, patch = map(int, current.split("."))

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid version part: {part}")

    return f"{major}.{minor}.{patch}"


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description="Version management for mcp-skills")
    parser.add_argument(
        "action",
        choices=["show", "bump", "set"],
        help="Action to perform",
    )
    parser.add_argument(
        "part",
        nargs="?",
        help="Version part to bump (major, minor, patch) or version to set",
    )

    args = parser.parse_args()

    if args.action == "show":
        print(get_current_version())

    elif args.action == "bump":
        if not args.part or args.part not in ["major", "minor", "patch"]:
            print("Error: Must specify version part (major, minor, patch)")
            return 1
        new_version = bump_version(args.part)
        update_version_files(new_version)
        print(f"🎉 Bumped version to {new_version}")

    elif args.action == "set":
        if not args.part:
            print("Error: Must specify version (e.g., 0.2.0)")
            return 1
        update_version_files(args.part)
        print(f"🎉 Set version to {args.part}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
