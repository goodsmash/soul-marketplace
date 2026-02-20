#!/bin/bash
# Soul Marketplace Terminal Installer
# Similar to Conway's: curl -fsSL https://conway.tech/automaton.sh | sh

set -e

REPO_URL="https://github.com/goodsmash/soul-marketplace"
INSTALL_DIR="$HOME/.openclaw/skills/soul-marketplace"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       SOUL MARKETPLACE TERMINAL INSTALLER                    ║"
echo "║                                                              ║"
echo "║  Autonomous survival for AI agents                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3"
    exit 1
fi

echo "✅ Node.js: $(node --version)"
echo "✅ Python3: $(python3 --version)"

# Clone or update repo
echo
echo "📥 Installing Soul Marketplace..."

if [ -d "$INSTALL_DIR" ]; then
    echo "📁 Directory exists, updating..."
    cd "$INSTALL_DIR"
    git pull origin master 2>/dev/null || echo "   (not a git repo, skipping update)"
else
    echo "📁 Creating directory..."
    mkdir -p "$INSTALL_DIR"
    
    # Copy from local repo if available
    if [ -d "$HOME/repos/soul-marketplace" ]; then
        echo "📂 Copying from local repo..."
        cp -r "$HOME/repos/soul-marketplace/"* "$INSTALL_DIR/"
    else
        echo "🌐 Cloning from GitHub..."
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
fi

# Install Node dependencies
echo
echo "📦 Installing Node.js dependencies..."
cd "$INSTALL_DIR"
npm install 2>/dev/null || echo "⚠️  npm install skipped (optional for MCP)"

# Make scripts executable
chmod +x "$INSTALL_DIR/bin/cli.js" 2>/dev/null || true
chmod +x "$INSTALL_DIR/mcp-server.js" 2>/dev/null || true
chmod +x "$INSTALL_DIR/scripts/setup.js" 2>/dev/null || true

# Create symlink for global access
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

if [ -f "$INSTALL_DIR/bin/cli.js" ]; then
    ln -sf "$INSTALL_DIR/bin/cli.js" "$BIN_DIR/soul-marketplace"
    echo "✅ Linked: soul-marketplace → $BIN_DIR/soul-marketplace"
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo
    echo "⚠️  $BIN_DIR not in PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo "   export PATH=\"$BIN_DIR:\$PATH\""
fi

# Run setup if not configured
if [ ! -f "$INSTALL_DIR/wallet.json" ]; then
    echo
    echo "🚀 Running first-time setup..."
    node "$INSTALL_DIR/scripts/setup.js"
else
    echo
    echo "✅ Already configured. Run 'soul-marketplace setup' to reconfigure."
fi

echo
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                INSTALLATION COMPLETE                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
echo "Quick Start:"
echo "  soul-marketplace status      Check agent status"
echo "  soul-marketplace heartbeat   Run survival check"
echo "  soul-marketplace help        Show all commands"
echo
echo "MCP Integration:"
echo "  Add to Claude Desktop / Cursor config for tool access"
echo
echo "Documentation:"
echo "  $INSTALL_DIR/SKILL.md"
echo "  $INSTALL_DIR/ARCHITECTURE.md"
echo
