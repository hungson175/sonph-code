#!/bin/bash
# Install script for sonph-code command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"

echo "🔧 Installing 'sonph-code' command globally..."

# Check if we have write permission to /usr/local/bin
if [ -w "$INSTALL_DIR" ]; then
    # Create symlink to the main launcher
    ln -sf "$SCRIPT_DIR/sonph-code" "$INSTALL_DIR/sonph-code"
    echo "✅ sonph-code installed to $INSTALL_DIR/sonph-code"
    echo "🚀 You can now run 'sonph-code' from any directory!"
else
    echo "❌ No write permission to $INSTALL_DIR"
    echo "💡 Try running with sudo: sudo ./install-sonph-code.sh"
    echo "💡 Or manually add to your PATH:"
    echo "   export PATH=\"$SCRIPT_DIR:\$PATH\""
    echo "   # Add this line to your ~/.bashrc or ~/.zshrc"
fi

echo ""
echo "📖 Usage:"
echo "  sonph-code                    # Run in current directory"
echo "  sonph-code /path/to/project   # Run in specified directory"
echo "  sonph-code --help             # Show help"
echo ""
echo "💡 Use /model command inside the tool to switch LLM providers"