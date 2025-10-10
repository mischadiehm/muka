"""
Example usage of MuKa MCP Server tools.

This script demonstrates how to use the MCP server tools programmatically
for data analysis workflows.
"""

import asyncio
import json
from pathlib import Path

from mcp_server.server import (
    handle_answer_question,
    handle_calculate_statistics,
    handle_classify_farms,
    handle_compare_groups,
    handle_export,
    handle_load_data,
    handle_query_farms,
)
from muka_analysis.config import init_config


async def example_workflow() -> None:
    """
    Example workflow: Load -> Classify -> Analyze -> Export.

    This demonstrates a complete analysis workflow using the MCP server tools.
    """
    print("=" * 70)
    print("MuKa MCP Server - Example Workflow")
    print("=" * 70 + "\n")

    # Initialize configuration
    init_config()

    # Step 1: Load data
    print("📥 Step 1: Loading farm data...")
    result = await handle_load_data({})
    print(f"   Loaded {result['rows']} rows from {result['file']}\n")

    # Step 2: Classify farms
    print("🏷️  Step 2: Classifying farms into groups...")
    result = await handle_classify_farms({})
    print(f"   Classified {result['classified_farms']}/{result['total_farms']} farms")
    print(f"   Groups: {json.dumps(result['group_counts'], indent=2)}\n")

    # Step 3: Query specific farms
    print("🔍 Step 3: Querying dairy farms with >100 animals...")
    result = await handle_query_farms({"group": "Milchvieh", "min_animals": 100, "limit": 10})
    print(f"   Found {result['count']} matching farms")
    if result.get("farms"):
        print(
            f"   Sample farm: TVD {result['farms'][0]['tvd']} "
            f"with {result['farms'][0]['n_animals_total']} animals\n"
        )

    # Step 4: Calculate statistics
    print("📊 Step 4: Calculating group statistics...")
    result = await handle_calculate_statistics({"group": "Milchvieh"})
    if result.get("statistics"):
        stats = result["statistics"][0]
        print(f"   Count: {stats['count']}")
        print(f"   Avg animals: {stats.get('n_animals_total_mean', 0):.1f}")
        print(f"   Avg dairy cattle: {stats.get('n_females_age3_dairy_mean', 0):.1f}\n")

    # Step 5: Compare groups
    print("⚖️  Step 5: Comparing Dairy vs Muku farms...")
    result = await handle_compare_groups(
        {"groups": ["Milchvieh", "Muku"], "metrics": ["n_animals_total", "n_females_age3_dairy"]}
    )
    if result.get("comparison"):
        for group_stats in result["comparison"]:
            print(
                f"   {group_stats['classification_pattern']}: "
                f"{group_stats['count']} farms, "
                f"avg {group_stats.get('n_animals_total_mean', 0):.1f} animals\n"
            )

    # Step 6: Answer natural language question
    print("❓ Step 6: Answering natural language question...")
    question = "Which group has the highest average animals?"
    result = await handle_answer_question({"question": question})
    print(f"   Q: {question}")
    print(f"   A: {result['answer']}\n")

    # Step 7: Export results
    print("💾 Step 7: Exporting analysis to Excel...")
    output_file = Path("output/mcp_example_analysis.xlsx")
    result = await handle_export({"file_path": str(output_file)})
    if result.get("success"):
        print(f"   Exported to: {result['file']}\n")

    print("=" * 70)
    print("✅ Workflow completed successfully!")
    print("=" * 70)


async def example_natural_language_queries() -> None:
    """
    Example of natural language question answering.

    This demonstrates the flexibility of the answer_question tool.
    """
    print("\n" + "=" * 70)
    print("Natural Language Query Examples")
    print("=" * 70 + "\n")

    # Ensure data is loaded
    await handle_load_data({})
    await handle_classify_farms({})

    questions = [
        "How many farms are there in total?",
        "What percentage of farms are Muku?",
        "Which group has the highest average animals?",
        "Are there any outliers in animal counts?",
        "What's the average animal count by group?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"{i}. Q: {question}")
        result = await handle_answer_question({"question": question})
        print(f"   A: {result['answer']}\n")

    print("=" * 70)


async def example_custom_analysis() -> None:
    """
    Example of custom data analysis.

    This shows how to perform specific analytical tasks.
    """
    print("\n" + "=" * 70)
    print("Custom Analysis Examples")
    print("=" * 70 + "\n")

    # Ensure data is loaded
    await handle_load_data({})
    await handle_classify_farms({})

    # Example 1: Find farms with high dairy cattle
    print("🔎 Finding farms with >50 dairy cattle...")
    result = await handle_query_farms({"min_animals": 50, "limit": 5})
    print(f"   Found {result['count']} farms\n")

    # Example 2: Get statistics for all groups
    print("📈 Statistics for all farm groups...")
    result = await handle_calculate_statistics({})
    if result.get("statistics"):
        print(f"   Calculated stats for {len(result['statistics'])} groups")
        for stats in result["statistics"][:3]:  # Show first 3
            print(f"   - {stats['classification_pattern']}: " f"{stats['count']} farms\n")

    print("=" * 70)


async def main() -> None:
    """Run all examples."""
    try:
        # Main workflow
        await example_workflow()

        # Natural language queries
        await example_natural_language_queries()

        # Custom analysis
        await example_custom_analysis()

        print("\n🎉 All examples completed successfully!\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())
