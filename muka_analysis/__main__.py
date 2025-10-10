"""
Entry point for running muka_analysis as a module.

This allows running the package with: python -m muka_analysis
"""

from muka_analysis.cli import app

if __name__ == "__main__":
    app()
