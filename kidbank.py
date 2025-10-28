#!/usr/bin/env python3
"""Main entry point for Kidbank application."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kidbank.app import KidbankApp


def main():
    """Run the Kidbank application."""
    app = KidbankApp()
    app.run()


if __name__ == "__main__":
    main()
