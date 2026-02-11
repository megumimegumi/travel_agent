#!/bin/bash
# Local Node.js Installer
# Installs a standalone Node.js binary to .node_runtime/

NODE_VERSION="v20.11.0"
NODE_DIST="node-$NODE_VERSION-linux-x64"
INSTALL_DIR="$(pwd)/.node_runtime"
BIN_DIR="$INSTALL_DIR/bin"

# If node is already in path and working, skip
if command -v node &> /dev/null; then
    echo "✅ Node.js ($(node -v)) is already available in environment."
    return 0 2>/dev/null || exit 0
fi

# Check if we already have the local install
if [ -x "$BIN_DIR/node" ]; then
    echo "✅ Using local Node.js from $INSTALL_DIR"
    export PATH="$BIN_DIR:$PATH"
    return 0 2>/dev/null || exit 0
fi

echo "📦 Node.js not found. Installing local copy ($NODE_VERSION)..."

# Download
echo "   Downloading..."
curl -s -L -o node.tar.xz "https://nodejs.org/dist/$NODE_VERSION/$NODE_DIST.tar.xz"

# Extract
echo "   Extracting..."
mkdir -p "$INSTALL_DIR"
tar -xf node.tar.xz -C "$INSTALL_DIR" --strip-components=1

# Cleanup
rm node.tar.xz

# Export Path
export PATH="$BIN_DIR:$PATH"

echo "✅ Node.js installed locally!"
echo "   Node: $(node -v)"
echo "   Npm:  $(npm -v)"
