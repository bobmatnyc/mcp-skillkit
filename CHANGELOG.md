# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Agent installation now integrated into `setup` command as Step 6 - automatically detects and configures Claude Desktop, Claude Code, and Auggie
- `--skip-agents` flag for `setup` command to skip automatic agent installation

### Changed
- `setup` command now provides complete one-command installation experience, matching mcp-ticketer's setup workflow
- Setup process now includes 6 steps instead of 5, with agent installation as the final step
- Updated documentation to reflect new integrated setup experience

## [0.6.3] - 2025-11-28

### Changed
- Verified MCP server installer for Claude Desktop, Claude Code, and Auggie
- Comprehensive installer validation with timestamped backups
- Security scan: 0 vulnerabilities, 29/29 security tests passing

### Fixed
- Cross-platform path detection improvements
- Atomic configuration updates with automatic rollback

## [0.5.0] - 2025-11-24

### Added

#### Security Features
- Multi-layer security validation system for skill loading
- Prompt injection detection with threat classification (BLOCKED, DANGEROUS, SUSPICIOUS)
- Repository trust levels (TRUSTED, VERIFIED, UNTRUSTED)
- Content sanitization with skill boundary markers
- Size limit enforcement for DoS prevention
- Comprehensive security validator with regex pattern matching
- SECURITY.md with complete threat model and security policy
- Security test suite with 29 comprehensive tests

#### CLI Commands
- `show`: Alias for `info` command for improved user experience
- `demo`: Interactive skill demonstration with auto-generated example prompts
- Updated `setup` command to highlight new demo functionality

#### Service Enhancements
- SkillManager security integration with configurable validation
- Verified repository management (add/remove trusted repos)
- Fixed trust level detection for repository identification

### Changed
- Setup wizard now recommends `demo` command as first step
- Skill loading now validates content security before use
- README updated with security section and trust level documentation

### Fixed
- Fixed 15 SKILL.md files with validation errors
- Corrected repository trust level matching

## [0.1.0] - 2025-11-23

### Added

#### Core Features
- Initial release of mcp-skillset - dynamic RAG-powered skills for code assistants
- FastMCP-based MCP server with 5 core tools for skill discovery and management
- 11 comprehensive CLI commands for skill and repository management
- Hybrid RAG system combining ChromaDB vector search and NetworkX knowledge graph
- Automatic toolchain detection supporting 24+ frameworks across 5 languages
- SQLite-based metadata storage with automatic JSON migration
- Complete integration test suite covering end-to-end workflows

#### MCP Tools
- `search_skills`: Natural language semantic search over skill descriptions
- `get_skill`: Retrieve full skill instructions and metadata by ID
- `recommend_skills`: Context-aware skill recommendations based on project toolchain
- `list_categories`: Browse skills by category and domain
- `reindex_skills`: Trigger manual reindexing of skill repositories

#### CLI Commands
- `setup`: Interactive setup wizard with toolchain detection and validation
- `search`: Search skills with natural language queries
- `list`: List all available skills with filtering options
- `info`: Display detailed information about specific skills
- `recommend`: Get personalized skill recommendations for current project
- `health`: System health check and diagnostics
- `stats`: Display usage statistics and repository metrics
- `repo add/list/update/remove`: Full repository management capabilities
- `index`: Manual reindexing with incremental update support
- `config`: Display and validate configuration settings

#### Language and Framework Support
- **Languages**: Python, TypeScript, JavaScript, Rust, Go
- **Python Frameworks**: FastAPI, Django, Flask, Pytest, Poetry, uv
- **JavaScript/TypeScript**: React, Next.js, Express, Vite, Node.js
- **Rust**: Cargo, Tokio, Actix
- **Go**: Go modules, Gin, Echo
- **Build Tools**: npm, yarn, pnpm, cargo, go mod, poetry, uv

#### RAG System
- Vector search with sentence-transformers (all-MiniLM-L6-v2 embeddings)
- Knowledge graph for skill relationships and dependencies
- Hybrid scoring: 70% vector similarity + 30% graph connectivity
- Confidence score normalization for toolchain detection
- Persistent ChromaDB vector store with incremental updates

#### Storage and Indexing
- SQLite metadata database for O(1) repository lookups
- Automatic migration from legacy JSON storage format
- Repository metadata tracking (URL, priority, auto-update settings)
- Indexed skill categories and toolchain associations

### Performance
- Complete integration test suite runs in <10 seconds
- O(1) indexed repository lookups via SQLite
- Efficient incremental reindexing for large skill collections
- Fast semantic search with cached embeddings

### Testing
- 48 total tests (37 unit + 11 integration tests)
- Test coverage: 85-96% across all modules
- End-to-end workflow validation
- Repository management integration tests
- Toolchain detection accuracy tests

### Documentation
- Comprehensive README with quick start guide
- Architecture documentation in docs/architecture/
- Skills resources catalog in docs/skills/RESOURCES.md
- API documentation for MCP tools
- CLI command reference with examples

### Developer Experience
- Zero-config setup with `mcp-skillset setup`
- Rich terminal UI with progress indicators
- Detailed error messages and troubleshooting hints
- Development mode with auto-reload support
- Makefile with common development tasks

### Configuration
- Global configuration in `~/.mcp-skillset/config.yaml`
- Project-local configuration with `.mcp-skillset.yaml`
- Environment variable overrides
- Configurable repository priorities
- Auto-update settings per repository

### Known Limitations
- Vector store requires ~100MB disk space for medium-sized skill collections
- Initial indexing takes 5-15 seconds depending on repository size
- ChromaDB currently requires local filesystem access
- Knowledge graph stored in memory (future: persistent backend option)

### Migration Notes
- Automatic migration from JSON to SQLite metadata storage
- Legacy JSON files preserved as backup in `~/.mcp-skillset/metadata.json.backup`
- No user action required for migration

## [Unreleased]

### Planned Features
- Qdrant vector store backend support
- Neo4j knowledge graph backend support
- HTTP transport mode for MCP server
- Skill usage analytics and recommendations tuning
- Custom skill repository authentication
- Skill versioning and update tracking
- Offline mode with cached skill bundles

---

[0.5.0]: https://github.com/bobmatnyc/mcp-skillset/releases/tag/v0.5.0
[0.1.0]: https://github.com/bobmatnyc/mcp-skillset/releases/tag/v0.1.0
