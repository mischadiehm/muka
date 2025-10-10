#!/usr/bin/env python3
"""
Quick launcher script for MuKa MCP Server.

This script provides an easy way to start the MCP server for testing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.server import main

if __name__ == "__main__":
    print("🚀 Starting MuKa Analysis MCP Server...")
    print("📡 Server communicates via stdio (standard input/output)")
    print("💡 Use with an MCP client like Claude Desktop")
    print("-" * 60)
    main()
