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
            "examples",
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
            "examples",
            "Show comprehensive usage examples",
            "examples",
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

    def show_examples(self) -> None:
        """Display comprehensive examples for all MCP tools."""
        console.print(
            "\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]"
        )
        console.print(
            "[bold cyan]           🐄 MuKa Farm Data Analysis - Examples              [/bold cyan]"
        )
        console.print(
            "[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n"
        )

        # 1. Data Loading & Status
        console.print(
            Panel(
                "[bold yellow]1. Data Loading & Status Commands[/bold yellow]\n\n"
                "[cyan]info[/cyan]\n"
                "  → Show current data status (loaded, classified, counts)\n"
                "  → Automatically run at startup\n\n"
                "[cyan]load[/cyan]\n"
                "  → Reload data from CSV (usually not needed - auto-loaded)\n"
                "  → Example: load\n\n"
                "[cyan]classify[/cyan]\n"
                "  → Re-run classification (usually not needed - auto-classified)\n"
                "  → Example: classify",
                title="💾 Data Management",
                border_style="yellow",
            )
        )

        # 2. Querying Farms
        console.print(
            Panel(
                "[bold yellow]2. Query Farms with Filters[/bold yellow]\n\n"
                "[cyan]query[/cyan] - Filter farms by various criteria\n\n"
                "[green]Example 1:[/green] All Muku farms\n"
                "  → query group=Muku\n\n"
                "[green]Example 2:[/green] Large dairy farms (>100 animals)\n"
                "  → query group=Milchvieh min_animals=100\n\n"
                "[green]Example 3:[/green] Medium-sized farms (50-100 animals)\n"
                "  → query min_animals=50 max_animals=100\n\n"
                "[green]Example 4:[/green] Specific farm by TVD ID\n"
                "  → query tvd=123456\n"
                "  Get details for one specific farm\n\n"
                "[green]Example 5:[/green] Farms from specific year\n"
                "  → query year=2024\n"
                "  Filter by data collection year\n\n"
                "[green]Example 6:[/green] Combine multiple filters\n"
                "  → query group=Muku min_animals=50 year=2024\n"
                "  Get Muku farms with 50+ animals from 2024\n\n"
                "[dim]Available groups:[/dim] Muku, Muku_Amme, Milchvieh, BKMmZ, BKMoZ, IKM\n"
                "[dim]Returns:[/dim] Up to 100 farms (use limit parameter for more)",
                title="🔍 Query & Filter",
                border_style="green",
            )
        )

        # 3. Farm Details
        console.print(
            Panel(
                "[bold yellow]3. Get Detailed Farm Information[/bold yellow]\n\n"
                "[cyan]farm tvd=<TVD_ID>[/cyan]\n\n"
                "[green]Example:[/green] Full details for a specific farm\n"
                "  → farm tvd=123456\n"
                "  Get complete information for one farm\n\n"
                "[green]Tip:[/green] Use query to find TVD IDs first:\n"
                "  → query group=Muku limit=5\n"
                "  → farm tvd=<id_from_query>\n\n"
                "[dim]Returns comprehensive data:[/dim]\n"
                "  • TVD ID, year, and assigned group\n"
                "  • 6 binary classification indicators\n"
                "  • Animal counts (total, dairy, females, calves)\n"
                "  • Calf movements (arrivals <85d, leavings <51d)\n"
                "  • Proportions (dairy days, slaughter rates)\n"
                "  • All fields used for classification",
                title="🏢 Farm Details",
                border_style="blue",
            )
        )

        # 4. Statistical Analysis
        console.print(
            Panel(
                "[bold yellow]4. Statistical Analysis[/bold yellow]\n\n"
                "[cyan]stats[/cyan] - Calculate comprehensive statistics\n\n"
                "[green]Example 1:[/green] All groups statistics\n"
                "  → stats\n\n"
                "[green]Example 2:[/green] Dairy farms only\n"
                "  → stats group=Milchvieh\n\n"
                "[green]Example 3:[/green] Muku farms statistics\n"
                "  → stats group=Muku\n\n"
                "[dim]Returns:[/dim] min, max, mean, median for all numeric fields",
                title="📊 Statistics",
                border_style="magenta",
            )
        )

        # 5. Group Comparison
        console.print(
            Panel(
                "[bold yellow]5. Compare Farm Groups[/bold yellow]\n\n"
                "[cyan]compare[/cyan] - Side-by-side group comparison\n\n"
                "[green]Example 1:[/green] Compare all groups\n"
                "  → compare\n"
                "  Shows summary statistics for all 6 farm groups\n\n"
                "[green]Example 2:[/green] Compare specific groups\n"
                "  → compare groups=Muku,Milchvieh\n"
                "  → compare groups=BKMmZ,BKMoZ,IKM\n"
                "  Compare just the groups you're interested in\n\n"
                "[green]Example 3:[/green] Compare with specific metrics\n"
                "  → compare metrics=n_animals_total,n_females_age3_dairy\n"
                "  Focus on particular fields only\n\n"
                "[dim]Shows:[/dim] Group, count, avg/median animals, dairy cattle, calf movements",
                title="⚖️  Group Comparison",
                border_style="cyan",
            )
        )

        # 6. Natural Language Questions
        console.print(
            Panel(
                "[bold yellow]6. Ask Natural Language Questions[/bold yellow]\n\n"
                "[cyan]question <your question>[/cyan]\n\n"
                "[green]Example 1:[/green] Count farms\n"
                "  → question How many dairy farms are there?\n\n"
                "[green]Example 2:[/green] Percentages\n"
                "  → question What percentage of farms are Muku?\n\n"
                "[green]Example 3:[/green] Averages\n"
                "  → question What is the average animal count?\n\n"
                "[green]Example 4:[/green] Group comparisons\n"
                "  → question Which group has the highest average animals?\n\n"
                "[green]Example 5:[/green] Outliers\n"
                "  → question Are there farms with unusual animal counts?\n\n"
                "[dim]The system will parse your question and provide relevant answers[/dim]",
                title="💬 Natural Language Queries",
                border_style="yellow",
            )
        )

        # 7. Data Insights
        console.print(
            Panel(
                "[bold yellow]7. Generate Data Insights[/bold yellow]\n\n"
                "[cyan]insights[/cyan] - Automated pattern detection\n\n"
                "[green]Example 1:[/green] General insights\n"
                "  → insights\n"
                "  → insights focus=general\n\n"
                "[green]Example 2:[/green] Find outliers\n"
                "  → insights focus=outliers\n\n"
                "[green]Example 3:[/green] Data distribution\n"
                "  → insights focus=distribution\n\n"
                "[green]Example 4:[/green] Group-specific insights\n"
                "  → insights group=Milchvieh\n\n"
                "[dim]Focus options:[/dim] general, outliers, trends, distribution",
                title="💡 Insights",
                border_style="green",
            )
        )

        # 8. Custom Metrics
        console.print(
            Panel(
                "[bold yellow]8. Calculate Custom Metrics[/bold yellow]\n\n"
                "[cyan]metric expression=<pandas_expression>[/cyan]\n\n"
                "[green]Example 1:[/green] Sum all animals\n"
                "  → metric expression=n_animals_total.sum()\n\n"
                "[green]Example 2:[/green] Average animals per farm\n"
                "  → metric expression=n_animals_total.mean()\n\n"
                "[green]Example 3:[/green] Count large farms (>100 animals)\n"
                "  → metric expression=(n_animals_total>100).sum()\n\n"
                "[green]Example 4:[/green] Farms in range (50-100 animals)\n"
                "  → metric expression=n_animals_total.between(50,100).sum()\n\n"
                "[green]Example 5:[/green] Statistical summary\n"
                "  → metric expression=n_animals_total.describe()\n\n"
                "[green]Example 6:[/green] Complex conditions\n"
                "  → metric expression=((n_animals_total>20)&(n_animals_total<=50)).sum()\n\n"
                "[dim]Use pandas-style expressions with column names[/dim]",
                title="🧮 Custom Calculations",
                border_style="magenta",
            )
        )

        # 9. Aggregations
        console.print(
            Panel(
                "[bold yellow]9. Aggregate Data by Fields[/bold yellow]\n\n"
                "[cyan]aggregate group_by=<fields> aggregate=<dict>[/cyan]\n\n"
                "[green]Example 1:[/green] Total animals by group\n"
                "  → aggregate group_by=group aggregate={'n_animals_total':'sum'}\n"
                "  Sum of all animals per farm group\n\n"
                "[green]Example 2:[/green] Average animals by year\n"
                "  → aggregate group_by=year aggregate={'n_animals_total':'mean'}\n"
                "  Average farm size per year\n\n"
                "[green]Example 3:[/green] Multiple aggregations\n"
                "  → aggregate group_by=group aggregate={'n_animals_total':'sum','n_females_age3_dairy':'mean'}\n"
                "  Combine different operations\n\n"
                "[green]Example 4:[/green] Group by multiple fields\n"
                "  → aggregate group_by=group,year aggregate={'n_animals_total':'count'}\n"
                "  Count farms by group and year\n\n"
                "[dim]Operations:[/dim] sum, mean, median, min, max, count\n"
                "[dim]Note:[/dim] Requires Python dict syntax for aggregate parameter",
                title="📈 Aggregations",
                border_style="blue",
            )
        )

        # 10. Export
        console.print(
            Panel(
                "[bold yellow]10. Export Results[/bold yellow]\n\n"
                "[cyan]export <filename>[/cyan]\n\n"
                "[green]Example 1:[/green] Default export\n"
                "  → export\n"
                "  Saves to: output/analysis_summary.xlsx\n\n"
                "[green]Example 2:[/green] Custom filename\n"
                "  → export my_analysis.xlsx\n\n"
                "[dim]Exports include:[/dim]\n"
                "  • Summary statistics by group\n"
                "  • Detailed farm-level data\n"
                "  • Group counts and distributions\n"
                "  • Multiple sheets for easy navigation",
                title="💾 Export",
                border_style="cyan",
            )
        )

        # Tips & Best Practices
        console.print(
            Panel(
                "[bold yellow]💡 Tips & Best Practices[/bold yellow]\n\n"
                "[green]1.[/green] Start with [cyan]info[/cyan] to check data status\n"
                "[green]2.[/green] Use [cyan]stats[/cyan] to understand overall patterns\n"
                "[green]3.[/green] Try [cyan]question[/cyan] for quick answers in natural language\n"
                "[green]4.[/green] Use [cyan]query[/cyan] to filter and explore specific farms\n"
                "[green]5.[/green] Use [cyan]metric[/cyan] for custom pandas calculations\n"
                "[green]6.[/green] Use [cyan]insights[/cyan] to discover patterns automatically\n"
                "[green]7.[/green] Export results with [cyan]export[/cyan] for further analysis\n"
                "[green]8.[/green] Type [cyan]help[/cyan] anytime for command overview\n\n"
                "[dim]Tab completion available for commands and parameters![/dim]",
                title="🎯 Tips",
                border_style="yellow",
            )
        )

        # Available Farm Groups
        console.print(
            Panel(
                "[bold yellow]📋 Available Farm Groups[/bold yellow]\n\n"
                "[cyan]Muku[/cyan]          - Mother cow farms\n"
                "[cyan]Muku_Amme[/cyan]     - Mother cow farms with nurse cows\n"
                "[cyan]Milchvieh[/cyan]     - Dairy farms\n"
                "[cyan]BKMmZ[/cyan]         - Combined dairy with breeding\n"
                "[cyan]BKMoZ[/cyan]         - Combined dairy without breeding\n"
                "[cyan]IKM[/cyan]           - Intensive calf rearing\n\n"
                "[dim]Use these group names in query, stats, and insights commands[/dim]",
                title="🏷️  Farm Classifications",
                border_style="blue",
            )
        )

        console.print(
            "\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]"
        )
        console.print(
            "[dim]Type any command to try it out! Use [cyan]help[/cyan] for quick reference.[/dim]\n"
        )

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
                # Join list of insights into formatted string
                insights_text = "\n".join(f"• {insight}" for insight in result["insights"])
                console.print(
                    Panel(
                        insights_text,
                        title="💡 Data Insights",
                        style="magenta",
                    )
                )
                if "focus" in result:
                    console.print(f"[dim]Focus: {result['focus']}[/dim]")

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

                if cmd == "examples":
                    self.show_examples()
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
