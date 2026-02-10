#!/usr/bin/env python3
"""
ChromaSpec - Color Palette Analyzer

This is a legacy entry point that redirects to the new modular CLI.
For direct usage, import from chromaspec.cli instead.

Usage:
    python chromaspec.py <input_file> [output.pdf]
    python chromaspec.py --help
"""

import sys

# Redirect to new CLI
from chromaspec.cli import main

if __name__ == "__main__":
    sys.exit(main())
