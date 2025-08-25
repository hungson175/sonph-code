#!/bin/bash
# Install script for sonph-code

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/usr/local/bin"

echo "🔧 Installing sonph-code globally..."

# Check if we have write permission to /usr/local/bin
if [ -w "$INSTALL_DIR" ]; then
    # Create symlink
    ln -sf "$SCRIPT_DIR/sonph-code.sh" "$INSTALL_DIR/sonph-code"
    echo "✅ sonph-code installed to $INSTALL_DIR/sonph-code"
    echo "🚀 You can now run 'sonph-code' from any directory!"
else
    echo "❌ No write permission to $INSTALL_DIR"
    echo "💡 Try running with sudo: sudo ./install.sh"
    echo "💡 Or manually add to your PATH:"
    echo "   export PATH=\"$SCRIPT_DIR:\$PATH\""
    echo "   # Add this line to your ~/.bashrc or ~/.zshrc"
fi

echo ""
echo "📖 Usage:"
echo "  sonph-code           # Run in current directory"
echo "  sonph-code /path/to/project  # Run in specified directory"