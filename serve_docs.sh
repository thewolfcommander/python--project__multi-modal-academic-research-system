#!/bin/bash

# Serve MkDocs Documentation
# This script starts the MkDocs development server with live reload

echo "🚀 Starting MkDocs documentation server..."
echo "📖 Documentation will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
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

# Serve documentation
mkdocs serve --dev-addr=127.0.0.1:8000

