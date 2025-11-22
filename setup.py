"""Setup script for backward compatibility.

Modern Python packages use pyproject.toml, but this file
provides backward compatibility for older pip versions.
"""

from setuptools import setup

# Read version
with open("VERSION") as f:
    version = f.read().strip()

# All configuration in pyproject.toml
setup(
    name="mcp-skills",
    version=version,
)
