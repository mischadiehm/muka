#!/usr/bin/env python3
"""
Test script to verify the examples command works correctly.
"""

import sys
import asyncio
from pathlib import Path

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

from interactive_mcp_client import MCPClient
from rich.console import Console

console = Console()


async def test_examples() -> None:
    """Test that the examples command works."""
    console.print("[bold cyan]Testing MCP Client Examples Command[/bold cyan]\n")
    
    try:
        # Create client (will auto-load data)
        client = MCPClient()
        
        # Show examples
        console.print("[green]✓[/green] Client initialized successfully\n")
        console.print("[yellow]Displaying examples...[/yellow]\n")
        
        client.show_examples()
        
        console.print("\n[green]✓[/green] Examples displayed successfully!")
        console.print("\n[bold cyan]Test Summary:[/bold cyan]")
        console.print("✓ Client initialization: PASSED")
        console.print("✓ Examples display: PASSED")
        console.print("\n[bold green]All tests passed! ✓[/bold green]")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        return False


async def main() -> None:
    """Run the test."""
    success = await test_examples()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
