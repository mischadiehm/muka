#!/usr/bin/env python3
"""
Interactive MCP Client for MuKa Farm Data Analysis.

Simple command-line client to test the MCP server locally.
Just run and start asking questions!
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

try:
    from prompt_toolkit.completion import Completer, Completion
except ImportError:
    # Fallback if prompt_toolkit is not installed
    Completer = object  # type: ignore
    Completion = object  # type: ignore

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mcp_server.server import (
    DataContext,
    handle_aggregate,
    handle_answer_question,
    handle_calculate_statistics,
    handle_classify_farms,
    handle_compare_groups,
    handle_custom_metric,
    handle_export,
    handle_get_data_info,
    handle_get_farm_details,
    handle_get_insights,
    handle_load_data,
    handle_query_farms,
)
from muka_analysis.config import init_config

console = Console()


class MukaCompleter(Completer):
    """Custom completer for MuKa commands with parameter completion."""

    def __init__(self) -> None:
        """Initialize the completer with commands and parameters."""
        self.commands = [
            "info",
            "load",
            "classify",
            "query",
            "stats",
            "question",
            "insights",
            "farm",
            "compare",
            "aggregate",
            "metric",
            "export",
            "help",
            "quit",
            "exit",
            "clear",
        ]

        self.command_params = {
            "query": ["group=", "tvd=", "year=", "min_animals=", "max_animals="],
            "stats": ["group="],
            "insights": [
                "focus=outliers",
                "focus=trends",
                "focus=distribution",
                "focus=general",
                "group=",
            ],
            "farm": ["tvd="],
            "aggregate": ["group_by=", "aggregate="],
            "metric": ["expression=", "filter=", "group_by="],
        }

        self.group_values = [
            "Muku",
            "Muku_Amme",
            "Milchvieh",
            "BKMmZ",
            "BKMoZ",
            "IKM",
        ]

    def get_completions(self, document, complete_event):
        """Get completions for the current input."""
        text = document.text_before_cursor
        words = text.split()

        # If no words yet, suggest commands
        if not words:
            for cmd in self.commands:
                yield Completion(cmd, start_position=0, display=cmd)
            return

        # First word - command completion
        if len(words) == 1 and not text.endswith(" "):
            word = words[0].lower()
            for cmd in self.commands:
                if cmd.startswith(word):
                    yield Completion(cmd, start_position=-len(word), display=cmd)
            return

        # Get the command (first word)
        command = words[0].lower()

        # Special handling for 'question' command - no parameter completion
        if command == "question":
            return

        # Parameter completion for other commands
        if command in self.command_params:
            current_input = text.split(maxsplit=1)[1] if len(text.split(maxsplit=1)) > 1 else ""
            last_word = words[-1] if words else ""

            # If typing a parameter
            for param in self.command_params[command]:
                if param.startswith(last_word):
                    yield Completion(
                        param,
                        start_position=-len(last_word),
                        display=param,
                    )

            # If parameter is complete and it's 'group=', suggest values
            if last_word.startswith("group=") and "=" in last_word:
                prefix = last_word.split("=")[0] + "="
                current_value = last_word.split("=")[1] if "=" in last_word else ""
                for group in self.group_values:
                    if group.lower().startswith(current_value.lower()):
                        yield Completion(
                            prefix + group,
                            start_position=-len(last_word),
                            display=group,
                        )


class MCPClient:
    """Simple MCP client for interactive testing."""

    def __init__(self) -> None:
        """Initialize the MCP client."""
        # Import the global data context from the server
        from mcp_server import server as server_module

        # Auto-load data into the global context that handlers use
        server_module.data_context._auto_load_data()

        # Use the same global context so handlers work correctly
        self.context = server_module.data_context

        self.handlers = {
            "load": handle_load_data,
            "classify": handle_classify_farms,
            "info": handle_get_data_info,
            "query": handle_query_farms,
            "stats": handle_calculate_statistics,
            "question": handle_answer_question,
            "insights": handle_get_insights,
            "farm": handle_get_farm_details,
            "compare": handle_compare_groups,
            "aggregate": handle_aggregate,
            "metric": handle_custom_metric,
            "export": handle_export,
        }

    def show_help(self) -> None:
        """Display available commands."""
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Example", style="yellow")

        table.add_row(
            "info",
            "Show current data status",
            "info",
        )
        table.add_row(
            "load",
            "Reload farm data from CSV (optional)",
            "load",
        )
        table.add_row(
            "classify",
            "Re-classify farms (optional)",
            "classify",
        )
        table.add_row(
            "query",
            "Query farms with filters",
            "query group=Muku",
        )
        table.add_row(
            "stats",
            "Calculate group statistics",
            "stats group=Milchvieh",
        )
        table.add_row(
            "question",
            "Ask a natural language question",
            "question How many dairy farms are there?",
        )
        table.add_row(
            "insights",
            "Get data insights",
            "insights focus=outliers",
        )
        table.add_row(
            "farm",
            "Get details for specific farm",
            "farm tvd=12345",
        )
        table.add_row(
            "compare",
            "Compare groups",
            "compare",
        )
        table.add_row(
            "export",
            "Export analysis to Excel",
            "export output.xlsx",
        )
        table.add_row(
            "help",
            "Show this help",
            "help",
        )
        table.add_row(
            "quit",
            "Exit the client",
            "quit",
        )

        console.print(table)

    def parse_command(self, command: str) -> tuple[str, Dict[str, Any]]:
        """
        Parse command and extract parameters.

        Args:
            command: User command string

        Returns:
            Tuple of (command_name, parameters)
        """
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        params: Dict[str, Any] = {}

        if len(parts) > 1:
            args = parts[1]

            # Special handling for 'question' command
            if cmd == "question":
                params["question"] = args
            # Special handling for 'export' command
            elif cmd == "export":
                params["file_path"] = args
            # Parse key=value pairs
            elif "=" in args:
                for pair in args.split():
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        # Try to convert to appropriate type
                        if value.isdigit():
                            params[key] = int(value)
                        elif value.lower() in ("true", "false"):
                            params[key] = value.lower() == "true"
                        else:
                            params[key] = value
            else:
                # Assume it's a single parameter value
                params["value"] = args

        return cmd, params

    async def execute_command(self, cmd: str, params: Dict[str, Any]) -> None:
        """
        Execute a command.

        Args:
            cmd: Command name
            params: Command parameters
        """
        if cmd not in self.handlers:
            console.print(f"[red]Unknown command: {cmd}[/red]")
            console.print("[yellow]Type 'help' for available commands[/yellow]")
            return

        try:
            handler = self.handlers[cmd]
            console.print(f"[cyan]Executing: {cmd}...[/cyan]")

            result = await handler(params)

            # Display result
            if isinstance(result, dict):
                self._display_result(cmd, result)
            else:
                console.print(result)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            logging.exception("Command execution failed")

    def _display_result(self, cmd: str, result: Dict[str, Any]) -> None:
        """
        Display command result in a nice format.

        Args:
            cmd: Command name
            result: Result dictionary
        """
        # Success/error status
        if "success" in result:
            status = "✅ Success" if result["success"] else "❌ Failed"
            console.print(f"\n{status}\n")

        # Handle different result types
        if cmd == "load":
            if result.get("success"):
                console.print(
                    Panel(
                        f"Loaded {result.get('rows', 0)} rows\n"
                        f"Columns: {result.get('columns', 0)}",
                        title="Data Loaded",
                        style="green",
                    )
                )

        elif cmd == "classify":
            if result.get("success") and "groups" in result:
                table = Table(title="Classification Results")
                table.add_column("Group", style="cyan")
                table.add_column("Count", style="yellow", justify="right")

                for group, count in result["groups"].items():
                    table.add_row(group, str(count))

                console.print(table)

        elif cmd == "query":
            if "farms" in result:
                farms = result["farms"]
                console.print(f"\n[green]Found {len(farms)} farms[/green]")

                if farms:
                    # Show first few farms
                    table = Table(title="Query Results (first 5)")
                    table.add_column("TVD", style="cyan")
                    table.add_column("Group", style="yellow")
                    table.add_column("Total Animals", justify="right")

                    for farm in farms[:5]:
                        table.add_row(
                            str(farm.get("tvd", "N/A")),
                            farm.get("group", "N/A"),
                            str(farm.get("n_animals_total", "N/A")),
                        )

                    console.print(table)
                    if len(farms) > 5:
                        console.print(f"[dim]... and {len(farms) - 5} more[/dim]")

        elif cmd == "stats":
            if "statistics" in result:
                console.print(
                    Panel(
                        json.dumps(result["statistics"], indent=2),
                        title="Statistics",
                        style="blue",
                    )
                )

        elif cmd == "question":
            if "answer" in result:
                console.print(
                    Panel(
                        result["answer"],
                        title="Answer",
                        style="green",
                    )
                )
            if "data" in result:
                console.print("\n[dim]Supporting data:[/dim]")
                console.print(json.dumps(result["data"], indent=2))

        elif cmd == "insights":
            if "insights" in result:
                console.print(
                    Panel(
                        result["insights"],
                        title="Data Insights",
                        style="magenta",
                    )
                )

        elif cmd == "info":
            console.print(
                Panel(
                    json.dumps(result, indent=2),
                    title="Data Information",
                    style="blue",
                )
            )

        else:
            # Default: pretty print JSON
            console.print(
                Panel(
                    json.dumps(result, indent=2),
                    title=f"{cmd.title()} Result",
                    style="blue",
                )
            )

    async def run(self) -> None:
        """Run the interactive client."""
        console.print(
            Panel.fit(
                "[bold cyan]🐄 MuKa Farm Data Analysis - Interactive MCP Client[/bold cyan]\n"
                "[yellow]Type 'help' for commands, 'quit' to exit[/yellow]\n"
                "[dim]Press Tab for command completion, Ctrl+C to cancel[/dim]",
                border_style="cyan",
            )
        )

        # Initialize configuration
        init_config()
        console.print("[green]✓[/green] Configuration loaded")

        # Show data status
        if self.context.data_loaded:
            summary = self.context.get_data_summary()
            if self.context.classified:
                console.print(
                    f"[green]✓[/green] Auto-loaded {summary.get('total_rows', 0)} farms "
                    f"({len(summary.get('group_counts', {}))} groups)\n"
                )
            else:
                console.print(
                    f"[green]✓[/green] Auto-loaded {summary.get('total_rows', 0)} rows "
                    f"(not yet classified)\n"
                )
        else:
            console.print("[yellow]⚠[/yellow] No data auto-loaded, use 'load' command\n")

        # Create prompt session with history and completion
        history_file = Path.home() / ".muka_history"

        try:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            from prompt_toolkit.styles import Style as PromptStyle

            prompt_style = PromptStyle.from_dict(
                {
                    "prompt": "cyan bold",
                }
            )

            session = PromptSession(
                history=FileHistory(str(history_file)),
                completer=MukaCompleter(),
                complete_while_typing=True,
                style=prompt_style,
            )
            use_prompt_toolkit = True
        except ImportError:
            use_prompt_toolkit = False
            console.print(
                "[yellow]Note: Install prompt_toolkit for tab completion: uv add prompt_toolkit[/yellow]\n"
            )
            session = None

        while True:
            try:
                # Get user input with tab completion and history
                if use_prompt_toolkit and session:
                    command = await session.prompt_async("muka> ")
                else:
                    # Fallback to simple input
                    from rich.prompt import Prompt

                    command = Prompt.ask("\n[bold cyan]muka>[/bold cyan]")

                if not command.strip():
                    continue

                cmd, params = self.parse_command(command)

                # Handle special commands
                if cmd in ("quit", "exit", "q"):
                    console.print("[yellow]Goodbye! 👋[/yellow]")
                    break

                if cmd == "help":
                    self.show_help()
                    continue

                if cmd == "clear":
                    console.clear()
                    console.print(
                        Panel.fit(
                            "[bold cyan]🐄 MuKa Farm Data Analysis[/bold cyan]",
                            border_style="cyan",
                        )
                    )
                    continue

                # Execute command
                await self.execute_command(cmd, params)

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'quit' to exit[/yellow]")
            except EOFError:
                console.print("\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logging.exception("Client error")


async def main() -> None:
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,  # Only show warnings and errors
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    client = MCPClient()
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
