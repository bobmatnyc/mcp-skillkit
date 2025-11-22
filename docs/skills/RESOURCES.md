# Skill Repository Resources

This document tracks known skill repositories and resources for mcp-skills indexing.

## Official Repositories

### anthropics/skills
**URL**: https://github.com/anthropics/skills
**License**: Apache 2.0 (example skills); Source-available (document skills)
**Priority**: 100 (Highest)

**Notable Skills**:
- algorithmic-art - p5.js art generation
- canvas-design - Visual art in PNG/PDF
- artifacts-builder - React/Tailwind artifacts
- mcp-server - MCP server creation guide
- webapp-testing - Playwright UI testing
- skill-creator - Interactive skill builder

### obra/superpowers
**URL**: https://github.com/obra/superpowers
**License**: MIT
**Priority**: 90

**Notable Skills**:
- test-driven-development - RED-GREEN-REFACTOR cycle
- systematic-debugging - Four-phase debugging framework
- root-cause-tracing - Error root cause analysis
- brainstorming - Structured ideation
- using-git-worktrees - Parallel development workflows

## Community Collections

### bobmatnyc/claude-mpm-skills
**URL**: https://github.com/bobmatnyc/claude-mpm-skills
**License**: MIT
**Priority**: 80

Skills for Claude MPM integration and project management.

### alirezarezvani/claude-skills
**URL**: https://github.com/alirezarezvani/claude-skills
**License**: MIT
**Priority**: 70

**Notable Skills**:
- 42 production-ready skills
- Marketing, Product, Engineering, QA
- 97+ Python CLI tools included

## Specialized Collections

### K-Dense-AI/claude-scientific-skills
**URL**: https://github.com/K-Dense-AI/claude-scientific-skills
**License**: Open Source

**Scientific Packages**: 58 specialized Python packages
**Scientific Databases**: 26 databases (PubMed, PubChem, UniProt, etc.)

### djacobsmeyer/claude-skills-engineering
**URL**: https://github.com/djacobsmeyer/claude-skills-engineering
**License**: MIT

**DevOps Skills**: CI/CD, Docker, Git worktrees

## Configuration

To add a repository to mcp-skills:

```bash
mcp-skills repo add <url> --priority <0-100>
```

Or edit `~/.mcp-skills/config.yaml`:

```yaml
repositories:
  - url: https://github.com/user/repo.git
    priority: 75
    auto_update: true
```

## Priority Guidelines

- **100**: Official Anthropic repositories
- **80-99**: High-quality community collections
- **50-79**: Specialized or domain-specific skills
- **0-49**: Experimental or personal collections

## License Compliance

All repositories listed here are open source with permissive licenses (MIT, Apache 2.0, etc.). Always verify license compatibility before commercial use.

---

**Last Updated**: 2025-01-21
