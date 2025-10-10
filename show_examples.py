#!/usr/bin/env python3
"""
Script to display MCP client examples without interactive mode.
"""

from rich.console import Console

# Import the client class to access show_examples
from interactive_mcp_client import MCPClient

console = Console()


def main() -> None:
    """Display examples."""
    client = MCPClient()
    client.show_examples()


if __name__ == "__main__":
    main()
