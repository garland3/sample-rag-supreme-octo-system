#!/bin/bash
"""
Build script for ai-search-supreme-octo package.

This script helps build the package for PyPI distribution.
"""

set -e

echo "🔧 Building ai-search-supreme-octo package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip setuptools wheel build twine

# Build the package
echo "🏗️  Building package..."
python -m build

# Check the package
echo "🔍 Checking package..."
python -m twine check dist/*

echo "✅ Package built successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Test the package locally:"
echo "   pip install dist/ai_search_supreme_octo-*.whl"
echo ""
echo "2. Upload to Test PyPI (optional):"
echo "   python -m twine upload --repository testpypi dist/*"
echo ""
echo "3. Upload to PyPI:"
echo "   python -m twine upload dist/*"
echo ""
echo "📁 Built files are in the 'dist/' directory."
