#!/bin/bash

# Build MkDocs Documentation
# This script builds the static documentation site

echo "🏗️  Building MkDocs documentation..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "⚠️  MkDocs not found. Installing..."
    pip install -r requirements.txt
fi

# Clean previous build
if [ -d "site" ]; then
    echo "🗑️  Removing previous build..."
    rm -rf site
fi

# Build documentation
echo "📦 Building site..."
mkdocs build --strict

# Check build status
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Documentation built successfully!"
    echo "📁 Output directory: site/"
    echo ""
    echo "To deploy to GitHub Pages, run:"
    echo "  mkdocs gh-deploy"
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
