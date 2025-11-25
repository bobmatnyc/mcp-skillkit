#!/usr/bin/env bash
#
# Generate shell completion files for mcp-skillset CLI
#
# This script generates completion files for bash, zsh, and fish shells
# using Click's built-in completion system.
#
# Usage:
#   ./scripts/generate_completions.sh
#
# Requirements:
#   - mcp-skillset must be installed (pip install -e .)
#   - OR use the development script: mcp-skillset-dev

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPLETIONS_DIR="${PROJECT_ROOT}/completions"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MCP Skills Shell Completion Generator ===${NC}\n"

# Create completions directory
echo -e "${BLUE}Creating completions directory...${NC}"
mkdir -p "${COMPLETIONS_DIR}"
echo -e "${GREEN}✓${NC} Directory created: ${COMPLETIONS_DIR}\n"

# Check if mcp-skillset is installed
if [ -d "${PROJECT_ROOT}/.venv/bin" ] && [ -f "${PROJECT_ROOT}/.venv/bin/mcp-skillset" ]; then
    MCP_CMD="${PROJECT_ROOT}/.venv/bin/mcp-skillset"
    echo -e "${GREEN}✓${NC} Using virtual environment: .venv/bin/mcp-skillset\n"
elif command -v mcp-skillset &> /dev/null; then
    MCP_CMD="mcp-skillset"
    echo -e "${GREEN}✓${NC} Using installed mcp-skillset\n"
else
    echo -e "${RED}✗ Error: mcp-skillset not installed${NC}"
    echo ""
    echo "Please install mcp-skillset first:"
    echo "  cd ${PROJECT_ROOT}"
    echo "  pip install -e ."
    echo ""
    echo "Or activate virtual environment if using one."
    exit 1
fi

# Generate bash completion
echo -e "${BLUE}Generating bash completion...${NC}"
if _MCP_SKILLS_COMPLETE=bash_source $MCP_CMD > "${COMPLETIONS_DIR}/mcp-skillset-completion.bash" 2>&1; then
    echo -e "${GREEN}✓${NC} Generated: ${COMPLETIONS_DIR}/mcp-skillset-completion.bash"
    echo -e "  Lines: $(wc -l < "${COMPLETIONS_DIR}/mcp-skillset-completion.bash" | tr -d ' ')\n"
else
    echo -e "${RED}✗${NC} Failed to generate bash completion\n"
    exit 1
fi

# Generate zsh completion
echo -e "${BLUE}Generating zsh completion...${NC}"
if _MCP_SKILLS_COMPLETE=zsh_source $MCP_CMD > "${COMPLETIONS_DIR}/mcp-skillset-completion.zsh" 2>&1; then
    echo -e "${GREEN}✓${NC} Generated: ${COMPLETIONS_DIR}/mcp-skillset-completion.zsh"
    echo -e "  Lines: $(wc -l < "${COMPLETIONS_DIR}/mcp-skillset-completion.zsh" | tr -d ' ')\n"
else
    echo -e "${RED}✗${NC} Failed to generate zsh completion\n"
    exit 1
fi

# Generate fish completion
echo -e "${BLUE}Generating fish completion...${NC}"
if _MCP_SKILLS_COMPLETE=fish_source $MCP_CMD > "${COMPLETIONS_DIR}/mcp-skillset-completion.fish" 2>&1; then
    echo -e "${GREEN}✓${NC} Generated: ${COMPLETIONS_DIR}/mcp-skillset-completion.fish"
    echo -e "  Lines: $(wc -l < "${COMPLETIONS_DIR}/mcp-skillset-completion.fish" | tr -d ' ')\n"
else
    echo -e "${RED}✗${NC} Failed to generate fish completion\n"
    exit 1
fi

# Summary
echo -e "${GREEN}=== Completion Generation Complete ===${NC}\n"
echo "Completion files generated in: ${COMPLETIONS_DIR}"
echo ""
echo "To install completions, see docs/SHELL_COMPLETIONS.md"
echo ""
echo "Quick install:"
echo "  Bash:  echo 'source ${COMPLETIONS_DIR}/mcp-skillset-completion.bash' >> ~/.bashrc"
echo "  Zsh:   echo 'source ${COMPLETIONS_DIR}/mcp-skillset-completion.zsh' >> ~/.zshrc"
echo "  Fish:  cp ${COMPLETIONS_DIR}/mcp-skillset-completion.fish ~/.config/fish/completions/"
echo ""
