# Skills Repository Resources

Comprehensive index of skill repositories compatible with mcp-skillset. This index is derived from extensive research documented in [skills-research.md](../research/skills-research.md).

## Table of Contents

- [Official Collections](#official-collections)
- [Community Collections](#community-collections)
- [Coding Skills Repositories](#coding-skills-repositories)
- [Toolchain-Specific Skills](#toolchain-specific-skills)
- [Operations & DevOps Skills](#operations--devops-skills)
- [MCP Servers as Skills](#mcp-servers-as-skills)
- [Collection Criteria](#collection-criteria)
- [Integration Guide](#integration-guide)
- [Verification Status](#verification-status)

---

## Official Collections

### anthropics/skills - Official Anthropic Repository
**The official repository for Claude Skills with production-grade implementations**

- **Repository**: https://github.com/anthropics/skills
- **License**: Apache 2.0 (example skills); Source-available (document skills)
- **Stars**: ~17,900+
- **Status**: ✅ Actively maintained by Anthropic
- **Priority**: 1 (Highest)

**Example Skills (Apache 2.0)**:
- **algorithmic-art** - Generate p5.js art with seeded randomness, flow fields, particle systems
- **canvas-design** - Design visual art in PNG and PDF formats using design philosophies
- **artifacts-builder** - Build complex HTML artifacts using React, Tailwind CSS, shadcn/ui
- **mcp-server** - Guide for creating high-quality MCP servers for API integration
- **webapp-testing** - Test local applications using Playwright for UI verification
- **brand-guidelines** - Apply Anthropic's official brand colors and typography
- **skill-creator** - Interactive tool that guides you through building new skills
- **template-skill** - Basic template to use as starting point for new skills

**Document Skills (Source-Available, Pre-included with Claude)**:
- **docx** - Create, edit, analyze Word documents with tracked changes and formatting preservation
- **pdf** - Comprehensive PDF manipulation toolkit for extraction, creation, merging, splitting
- **pptx** - Create, edit, analyze PowerPoint presentations with layouts, charts, templates
- **xlsx** - Create, edit, analyze Excel spreadsheets with formulas, formatting, data analysis

**Installation**: `/plugin marketplace add anthropics/skills`

---

## Community Collections

### obra/superpowers - Battle-Tested Development Workflows
**Systematic development workflows from real-world experience**

- **Repository**: https://github.com/obra/superpowers
- **License**: MIT
- **Last Updated**: October 2025
- **Status**: ✅ Active
- **Priority**: 2

**Core Skills**:
- **Testing**: test-driven-development, condition-based-waiting, testing-anti-patterns
- **Debugging**: systematic-debugging, root-cause-tracing, verification-before-completion, defense-in-depth
- **Collaboration**: brainstorming, writing-plans, executing-plans, dispatching-parallel-agents
- **Development**: using-git-worktrees, finishing-a-development-branch, subagent-driven-development
- **Meta**: writing-skills, sharing-skills, testing-skills-with-subagents

**Custom Slash Commands**: /superpowers:brainstorm, /superpowers:write-plan, /superpowers:execute-plan

**Installation**: `/plugin marketplace add obra/superpowers-marketplace`
**Companion**: https://github.com/obra/superpowers-lab (experimental skills)

### bobmatnyc/claude-mpm-skills - Project Management Integration
**Skills for Claude MPM integration with ticket tracking and project management**

- **Repository**: https://github.com/bobmatnyc/claude-mpm-skills
- **License**: MIT
- **Status**: ✅ Active
- **Priority**: 3

**Categories**:
- Project management and tracking
- Issue/ticket integration
- Workflow automation
- Documentation generation

### alirezarezvani/claude-skills - Production Team Skills
**Production-ready skill packages with comprehensive Python CLI tools**

- **Repository**: https://github.com/alirezarezvani/claude-skills
- **License**: MIT
- **Last Updated**: November 2025
- **Status**: ✅ Active
- **Priority**: 3

**42 Production Skills Including**:

**Marketing (3 skills)**:
- content-creator: Brand voice analyzer, SEO optimizer, social media frameworks
- marketing-demand-acquisition: CAC calculator, full-funnel strategy
- marketing-strategy-pmm: Positioning, GTM strategy, competitive intelligence

**Executive Advisory (2 skills)**:
- ceo-advisor: Strategy analyzer, financial scenario modeling, board governance
- cto-advisor: Tech debt analyzer, team scaling calculator, architecture decisions

**Product Team (5 skills)**:
- product-manager-toolkit: RICE prioritizer, customer interview analyzer, PRD templates
- agile-product-owner: User story generator, sprint planner
- ux-researcher-designer: Persona generator, journey mapper

**Engineering Team - Core (9 skills)**:
- Software Architect, Frontend Engineer, Backend Engineer, Fullstack Engineer
- QA Testing Engineer, DevOps Engineer, SecOps Engineer, Code Reviewer, Security Engineer

**Engineering Team - AI/ML/Data (5 skills)**:
- Data Scientist, Data Engineer, ML/AI Engineer, Prompt Engineer, Computer Vision Engineer

**Regulatory Affairs & Quality (12 skills)**:
- Quality Manager, QMS ISO 13485 Specialist, CAPA Officer, Documentation Manager
- Risk Management Specialist, Information Security Manager, MDR/FDA Specialists

**Features**:
- 97+ Python CLI analysis tools included
- Documented ROI: 40%+ time savings, 30%+ quality improvements
- Estimated value: $1.7M+/month per organization

**Related**: https://github.com/alirezarezvani/claude-code-skill-factory (generation toolkit)

### travisvn/awesome-claude-skills - Comprehensive Guide
**Most comprehensive guide with detailed documentation and comparison matrices**

- **Repository**: https://github.com/travisvn/awesome-claude-skills
- **Stars**: ~2,000+
- **License**: Apache 2.0
- **Last Updated**: November 2025
- **Status**: ✅ Active

**Features**:
- Comprehensive curated list of official and community skills
- Extensive Skills vs MCP vs System Prompts comparison
- Security guidelines and best practices
- FAQ and troubleshooting guide
- Progressive disclosure architecture explained
- Community verification system

### BehiSecc/awesome-claude-skills - Categorized Collection
**Well-organized categorized collection with practical focus**

- **Repository**: https://github.com/BehiSecc/awesome-claude-skills
- **Stars**: ~3,800+
- **License**: Open source
- **Last Updated**: 2025
- **Status**: ✅ Active

**Categories**:
- Document Skills (docx, pdf, pptx, xlsx)
- Development & Code Tools (TDD, git-worktrees, AWS, pypict testing)
- Data & Analysis (CSV analysis, root-cause-tracing)
- Scientific & Research Tools (26 databases, 58 packages including PubMed, PubChem, UniProt, ChEMBL, AlphaFold)
- Writing & Research (article extraction, brainstorming)
- Media & Content (YouTube transcripts, EPUB, image enhancer)
- Security & Web Testing (ffuf, webapp-testing, systematic debugging)
- Utility & Automation (file organizer, invoice organizer)

### ComposioHQ/awesome-claude-skills - Production-Focused
**Production-focused collection emphasizing real-world productivity**

- **Repository**: https://github.com/ComposioHQ/awesome-claude-skills
- **License**: Apache 2.0
- **Status**: ✅ Active

**Highlights**:
- Official document skills integration
- Business & marketing skills (competitive ads, domain brainstormer, lead research)
- Security & forensics (computer forensics, threat hunting with Sigma rules, metadata extraction)
- Integration with Composio platform (500+ apps)
- Skills API documentation and examples

---

## Coding Skills Repositories

### Code Generation and Refactoring

**Code Refactoring Skill**
- **URL**: https://claude-plugins.dev/skills/@dasien/RemoteCredentialRequestPOC/code-refactoring
- Improve code structure and readability without changing external behavior

### Testing Frameworks

**test-driven-development** (obra/superpowers)
- **URL**: https://github.com/obra/superpowers/tree/main/skills/test-driven-development
- RED-GREEN-REFACTOR cycle enforcement. Mandatory use before implementation code

**webapp-testing** (Official Anthropic)
- **URL**: https://github.com/anthropics/skills/tree/main/webapp-testing
- Test local web applications using Playwright for UI verification

**playwright-skill** (Community Enhanced)
- **URL**: https://github.com/lackeyjb/playwright-skill
- **License**: MIT
- Model-invoked Playwright automation where Claude writes custom automation code on-the-fly

**pypict-claude-skill**
- **URL**: https://github.com/omkamal/pypict-claude-skill
- Design comprehensive test cases using PICT (Pairwise Independent Combinatorial Testing)

**test-fixing**
- **URL**: https://github.com/mhattingpete/claude-skills-marketplace/tree/main/engineering-workflow-plugin/skills/test-fixing
- Detect failing tests and propose patches with systematic error grouping

### Linting and Code Quality

**clj-kondo**
- **URL**: https://claude-plugins.dev/skills/@hugoduncan/library-skills/clj-kondo
- Comprehensive guide to using clj-kondo for Clojure code linting

**move-code-quality-skill**
- **URL**: https://github.com/1NickPappas/move-code-quality-skill
- Analyzes Move language packages against official Move Book Code Quality Checklist

**cclint - Claude Code Linter**
- **URL**: https://github.com/carlrannaberg/cclint
- Comprehensive linting tool for Claude Code projects with agent/subagent linting

### Debugging and Error Analysis

**systematic-debugging** (obra/superpowers)
- **URL**: https://github.com/obra/superpowers/tree/main/skills/systematic-debugging
- Four-phase debugging framework ensuring root cause investigation before fixes

**root-cause-tracing** (obra/superpowers)
- Use when errors occur deep in execution to trace back to the original trigger

**verification-before-completion** (obra/superpowers)
- Ensure issues are actually fixed before claiming completion with mandatory evidence validation

### Documentation Generation

**skill-creator** (Official Anthropic)
- **URL**: https://github.com/anthropics/skills/tree/main/skill-creator
- Interactive skill creation tool with guided Q&A, template generation

**claude-auto-documenter-v2**
- **URL**: https://github.com/Puneet8800/claude-auto-documenter-v2
- Production-ready MCP server for automatic documentation generation

**metaskills/skill-builder**
- **URL**: https://github.com/metaskills/skill-builder
- **Author**: Ken Collins (AWS Serverless Hero)
- Meta-skill for creating, editing, converting skills

### Data Processing

**csv-data-summarizer-claude-skill**
- **URL**: https://github.com/coffeefuelbump/csv-data-summarizer-claude-skill
- Automatically analyzes CSV files with column analysis, distribution analysis

**scientific-packages** (K-Dense-AI)
- **URL**: https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-packages
- 58 specialized Python packages for bioinformatics, cheminformatics, machine learning

**scientific-databases** (K-Dense-AI)
- **URL**: https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/scientific-databases
- Access to 26 scientific databases (PubMed, PubChem, UniProt, ChEMBL, AlphaFold DB)

**article-extractor**
- **URL**: https://github.com/michalparkola/tapestry-skills-for-claude-code/tree/main/article-extractor
- Extract full article text and metadata from web pages

---

## Toolchain-Specific Skills

### Python Skills

**hoelzro/dotfiles - python-style**
- **URL**: https://claude-plugins.dev/skills/@hoelzro/dotfiles/python-style
- Python coding conventions and best practices including using `uv run`

**google-adk-python** (via mrgoonie/claudekit-skills)
- **URL**: https://github.com/mrgoonie/claudekit-skills
- Google's Agent Development Kit for building AI agents with tool integration

### TypeScript/JavaScript Skills

**Nice-Wolf-Studio/claude-skills-threejs-ecs-ts**
- **URL**: https://github.com/Nice-Wolf-Studio/claude-skills-threejs-ecs-ts
- **License**: MIT
- TypeScript + Three.js + Entity Component Systems for mobile-optimized games

**diet103/claude-code-infrastructure-showcase**
- **URL**: https://github.com/diet103/claude-code-infrastructure-showcase
- Auto-activating skills, backend development guidelines with 12 resource files

**mrgoonie/claudekit-skills - TypeScript/JavaScript**
- **URL**: https://github.com/mrgoonie/claudekit-skills
- **better-auth**: Comprehensive TypeScript authentication framework
- **web-frameworks**: Next.js, Turborepo
- **ui-styling**: shadcn/ui, Tailwind CSS
- **frontend-development**: React/TypeScript guidelines

**ruvnet/claude-flow - TypeScript**
- **URL**: https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-TypeScript
- **Stars**: 10k+
- TypeScript best practices with strict type checking coordination

### Go Language Skills

**BradPerbs/claude-go**
- **URL**: https://github.com/BradPerbs/claude-go
- GoLang Wrapper for Claude 3 API

**ruvnet/claude-flow - Go**
- **URL**: https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-Go
- Go concurrency patterns, microservices and CLI tools

### Rust Skills

**Microsoft Pragmatic Rust Guidelines Skill**
- **Article**: https://medium.com/rustaceans/teaching-claude-to-write-better-rust-automating-microsofts-guidelines-with-skills-3207a797b9f8
- **Author**: Enzo Lombardi
- AI-optimized version of Microsoft's Rust guidelines

**ruvnet/claude-flow - Rust**
- **URL**: https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-Rust
- Memory-safe coordination with Cargo parallel compilation

### Java Skills

**anthropic-sdk-java** (Official)
- Official Java client library for the Anthropic API

**ruvnet/claude-flow - Java**
- **URL**: https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-Java
- Maven/Gradle ecosystem coordination, Spring Boot operations

---

## Operations & DevOps Skills

### CI/CD Pipeline Skills

**djacobsmeyer/claude-skills-engineering**
- **URL**: https://github.com/djacobsmeyer/claude-skills-engineering
- **License**: MIT
- **Created**: 2025-11-14

**DevOps Capabilities**:
- CI/CD Pipeline Builder (GitHub Actions, GitLab CI, CircleCI)
- Docker Workflow (Container management, Dockerfile generation)
- Git worktree management
- Automated code review
- Test generation (unit, integration, E2E)

**wshobson/agents - CI/CD Plugin**
- **URL**: https://github.com/wshobson/agents
- **License**: MIT
- **Status**: Updated for Sonnet 4.5 & Haiku 4.5

**Comprehensive system**:
- 85 specialized AI agents
- 47 agent skills
- 44 development tools in 63 focused plugins
- 4 specialized CI/CD skills

**ruvnet/claude-flow - CI/CD Module**
- **URL**: https://github.com/ruvnet/claude-flow/wiki/CLAUDE-MD-CICD
- **Ranked**: #1 in agent-based frameworks
- Complete CI/CD pipeline setup with GitHub Actions, Docker, Kubernetes

### Cloud Platform Integration

**zxkane/aws-skills**
- **URL**: https://github.com/zxkane/aws-skills
- **License**: MIT

**AWS Capabilities**:
- **aws-cdk-development**: AWS CDK best practices, infrastructure as code
- **aws-cost-operations**: Cost optimization with 7 integrated MCP servers
- **aws-serverless-eda**: Serverless and event-driven architecture

**Supported Services**: Lambda, S3, EC2, CloudFormation, CDK, Step Functions, EventBridge

### Container and Kubernetes Management

**Docker MCP Toolkit** (Official Docker)
- **URL**: https://www.docker.com/blog/connect-mcp-servers-to-claude-desktop-with-mcp-toolkit
- Secure containerized MCP server execution
- GitHub integration, Kubernetes management

**RchGrav/claudebox**
- **URL**: https://github.com/RchGrav/claudebox
- **License**: MIT
- Ultimate Claude Code Docker Development Environment

**VishalJ99/claude-docker**
- **URL**: https://github.com/VishalJ99/claude-docker
- Docker container for running Claude Code with full permissions

**Kubernetes Servers** (Multiple implementations):
1. **mcp-server-kubernetes** - https://github.com/strowk/mcp-k8s-go
2. **k8m** - https://github.com/weibaohui/k8m (Multi-cluster with UI)
3. **mkp** - https://github.com/StacklokLabs/mkp (Native Go)
4. **blankcut/kubernetes-claude** - https://playbooks.com/mcp/blankcut-kubernetes-claude

### Infrastructure as Code

**hashicorp/terraform-mcp-server** (Official)
- **URL**: https://github.com/hashicorp/terraform-mcp-server
- **Version**: 0.2.3
- Terraform Registry API integration
- HCP Terraform & Terraform Enterprise support

**ahmedasmar/devops-claude-skills - IaC Terraform**
- **URL**: https://claude-plugins.dev/skills/@ahmedasmar/devops-claude-skills/skills
- Terraform configurations, module development, state management

**Pulumi Server** (Official)
- **URL**: https://github.com/pulumi/mcp-server
- Deploy and manage cloud infrastructure

### Security Scanning

**claude-code-security-review** (Official Anthropic)
- **URL**: https://github.com/anthropics/claude-code (feature)
- **Status**: Official Anthropic release (August 2025)
- **License**: Team/Enterprise

**Security Capabilities**:
- Automated security scanning on pull requests
- Detects 10 major vulnerability categories (SQL injection, XSS, auth flaws, etc.)
- GitHub Actions integration
- `/security-review` terminal command

**Snyk MCP Server** (Official)
- **URL**: https://snyk.io/articles/claude-desktop-and-snyk-mcp
- **Status**: Official Snyk (CLI v1.1298.0+)

**Security Capabilities**:
- 11 security scanning tools (SAST, dependency scanning, container, IaC)
- Auto-fix vulnerabilities via natural language
- Real-time vulnerability detection

**GitGuardian Server** (Official)
- **URL**: https://github.com/GitGuardian/gg-mcp
- Secret scanning with 500+ secret detectors

**CrowdStrike Falcon Server** (Official)
- **URL**: https://github.com/CrowdStrike/falcon-mcp
- Detections, incidents, threat intelligence

---

## MCP Servers as Skills

MCP servers can provide skill-like capabilities through their tools and resources. The following servers are particularly useful for extending skill capabilities:

### Version Control

**GitHub Official MCP Server**
- **URL**: https://github.com/github/github-mcp-server
- **License**: MIT
- Repository management, Issue & PR automation, CI/CD intelligence, Code security

**GitLab Server**
- **URL**: https://github.com/modelcontextprotocol/servers/tree/main/src/gitlab
- **License**: MIT
- GitLab platform integration for project management

**Git MCP Server** (Community - Enhanced)
- **URL**: https://github.com/cyanheads/git-mcp-server
- Comprehensive Git operations including worktree management

### Database Integration

**PostgreSQL Server**
- **URL**: https://github.com/modelcontextprotocol/servers/tree/main/src/postgres
- Schema inspection, query capabilities

**SQLite Server**
- **URL**: https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite
- Database interaction and business intelligence

**MongoDB Servers**
- https://github.com/kiliczsh/mcp-mongo-server
- https://github.com/furey/mongodb-lens (Full featured)

### Browser Automation

**Playwright Server** (Official Microsoft)
- **URL**: https://github.com/microsoft/playwright-mcp
- Browser automation, testing, web scraping

**Puppeteer Server**
- **URL**: https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer
- Browser automation, web scraping

### Search and Documentation

**Brave Search Server** (Official)
- **URL**: https://github.com/brave/brave-search-mcp-server
- Web and local search using Brave's Search API

**Context7 Server**
- Up-to-date, version-specific documentation for coding

**Microsoft Learn Docs Server** (Official)
- **URL**: https://github.com/microsoftdocs/mcp
- Access to Microsoft's official documentation

---

## Collection Criteria

For a repository to be included in this index:

### Format Requirements
1. **YAML Frontmatter**: Skills must include YAML metadata
2. **Markdown Body**: Instructions in clear markdown format
3. **Progressive Disclosure**: Metadata (~100 tokens), full content (<5k tokens)

### Quality Standards
1. **Documentation**: Clear usage instructions and examples
2. **Maintenance**: Recent activity and active maintenance
3. **Testing**: Skills are tested and verified working
4. **Licensing**: Compatible open-source license (MIT, Apache 2.0, etc.)

### Metadata Requirements
```yaml
---
name: skill-name
description: Brief skill description
category: testing|debugging|documentation|etc
toolchain: Python|TypeScript|Rust|Go|etc (optional)
frameworks: [Flask, pytest, etc] (optional)
---
```

---

## Integration Guide

### Adding a Repository to mcp-skillset

**Command Line**:
```bash
# Add a repository
mcp-skillset repo add https://github.com/anthropics/skills --priority 100

# Add with specific configuration
mcp-skillset repo add https://github.com/obra/superpowers --priority 90 --auto-update

# List all repositories
mcp-skillset repo list

# Update all repositories
mcp-skillset repo update
```

**Configuration File** (`~/.mcp-skillset/config.yaml`):
```yaml
repositories:
  - url: https://github.com/anthropics/skills.git
    priority: 100
    auto_update: true

  - url: https://github.com/obra/superpowers.git
    priority: 90
    auto_update: true

  - url: https://github.com/bobmatnyc/claude-mpm-skills.git
    priority: 80
    auto_update: true
```

### Priority System

Collections are assigned priority levels for conflict resolution:

- **Priority 100**: Official Anthropic repositories (highest precedence)
- **Priority 90**: Highly trusted community collections (obra/superpowers)
- **Priority 80**: Verified community collections
- **Priority 70**: Specialized or domain-specific skills
- **Priority 50**: Experimental or personal collections

**When multiple collections provide the same skill, the higher priority version is used.**

### Skill Discovery Process

mcp-skillset automatically discovers and indexes skills from all configured repositories:

1. **Clone**: Git repositories cloned into `~/.mcp-skillset/repos/{collection-name}/`
2. **Parse**: YAML frontmatter and markdown content extracted
3. **Index**: Vector embeddings and knowledge graph relationships created
4. **Serve**: Skills exposed via MCP protocol to code assistants
5. **Load**: Dynamic loading on-demand for memory efficiency

### Toolchain Detection

mcp-skillset automatically detects your project's toolchain:

- **Languages**: Python, TypeScript, JavaScript, Rust, Go, Java, etc.
- **Frameworks**: Flask, Django, React, Next.js, etc.
- **Build Tools**: pip, npm, cargo, maven, gradle, etc.

Based on detection, relevant skills are automatically recommended.

---

## Verification Status

| Repository | Skills Count | Verified | Last Updated | Priority |
|------------|--------------|----------|--------------|----------|
| anthropics/skills | ~15 | ✅ | 2025-11 | 100 |
| obra/superpowers | ~20 | ✅ | 2025-10 | 90 |
| bobmatnyc/claude-mpm-skills | ~69 | ✅ | 2025-11 | 80 |
| alirezarezvani/claude-skills | 42 | ✅ | 2025-11 | 80 |
| travisvn/awesome-claude-skills | Curated List | ✅ | 2025-11 | N/A |
| BehiSecc/awesome-claude-skills | Curated List | ✅ | 2025 | N/A |
| ComposioHQ/awesome-claude-skills | Varied | ✅ | 2025 | N/A |
| K-Dense-AI/claude-scientific-skills | 84 | ⏳ | 2025 | 70 |
| djacobsmeyer/claude-skills-engineering | ~10 | ⏳ | 2025-11 | 70 |
| wshobson/agents | 85 agents | ✅ | 2025 | 70 |
| ruvnet/claude-flow | Framework | ✅ | 2025 | 70 |

**Legend**:
- ✅ = Fully verified and tested
- ⏳ = Pending verification
- ❌ = Issues found

---

## Discovery Platforms

### Skills Marketplaces

**SkillsMP.com**
- **URL**: https://skillsmp.com
- Searchable marketplace of 13,000+ Claude Code skills from GitHub with installation commands

**Claude Plugins Dev**
- **URL**: https://claude-plugins.dev
- Plugin and skill discovery platform

### MCP Server Registries

**MCP Registry** (Official)
- **URL**: https://registry.modelcontextprotocol.io
- Browse and discover MCP servers

**MCP Servers Directory**
- **URL**: https://mcpservers.org
- Community-maintained directory

**Awesome MCP Servers**
- **URL**: https://github.com/appcypher/awesome-mcp-servers
- Curated list of 380+ MCP servers

---

## Contributing

To propose a new skill collection:

1. **Open an issue**: https://github.com/bobmatnyc/mcp-skillset/issues
2. **Provide details**:
   - Repository URL
   - Skills count and categories
   - License information
   - Sample skills
3. **Demonstrate quality**:
   - Show active maintenance
   - Provide documentation
   - Include tests or examples

---

## Additional Resources

### Official Documentation
- **MCP Specification**: https://modelcontextprotocol.io
- **Anthropic Skills Blog**: https://www.anthropic.com/news/skills
- **Claude Documentation**: https://docs.anthropic.com

### Research
- **Skills Research**: [skills-research.md](../research/skills-research.md) - Comprehensive research on 69+ skills and repositories

### Architecture
- **Architecture Documentation**: [architecture/README.md](../architecture/README.md) - Detailed mcp-skillset architecture

---

**Last Updated**: 2025-11-21
**Maintained by**: mcp-skillset project
**Contribute**: https://github.com/bobmatnyc/mcp-skillset
**Research Source**: Based on [skills-research.md](../research/skills-research.md)
