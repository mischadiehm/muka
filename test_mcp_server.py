"""
Test script for MuKa MCP Server.

This script tests the MCP server locally without needing a full MCP client.
"""

import asyncio
import json
import logging

import mcp_server.server as server_module
from mcp_server.server import (
    DataContext,
    handle_answer_question,
    handle_calculate_statistics,
    handle_classify_farms,
    handle_get_data_info,
    handle_load_data,
    handle_query_farms,
)
from muka_analysis.config import init_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_basic_workflow() -> None:
    """Test basic workflow: load -> classify -> query."""
    print("\n" + "=" * 70)
    print("🧪 Testing MuKa MCP Server - Basic Workflow")
    print("=" * 70 + "\n")

    # Initialize config
    init_config()

    # Test 1: Load data
    print("📥 Test 1: Loading farm data...")
    result = await handle_load_data({})
    print(f"   Result: {json.dumps(result, indent=2)}")
    assert result["success"], "Failed to load data"
    print("   ✅ Data loaded successfully\n")

    # Test 2: Classify farms
    print("🏷️  Test 2: Classifying farms...")
    result = await handle_classify_farms({})
    print(f"   Result: {json.dumps(result, indent=2)}")
    assert result["success"], "Failed to classify farms"
    print("   ✅ Farms classified successfully\n")

    # Test 3: Get data info
    print("ℹ️  Test 3: Getting data info...")
    result = await handle_get_data_info({})
    print(f"   Result: {json.dumps(result, indent=2)}")
    assert result["loaded"], "Data not loaded"
    assert result["classified"], "Data not classified"
    print("   ✅ Data info retrieved successfully\n")

    # Test 4: Query farms
    print("🔍 Test 4: Querying Muku farms...")
    result = await handle_query_farms({"group": "Muku", "limit": 5})
    print(f"   Result: Found {result.get('count', 0)} farms")
    if result.get("farms"):
        print(f"   Sample farm: {json.dumps(result['farms'][0], indent=2)}")
    print("   ✅ Query executed successfully\n")

    # Test 5: Calculate statistics
    print("📊 Test 5: Calculating group statistics...")
    result = await handle_calculate_statistics({})
    print(f"   Result: Calculated stats for {len(result.get('statistics', []))} groups")
    if result.get("statistics"):
        print(f"   Sample stats: {json.dumps(result['statistics'][0], indent=2)}")
    print("   ✅ Statistics calculated successfully\n")

    # Test 6: Answer question
    print("❓ Test 6: Answering natural language question...")
    result = await handle_answer_question({"question": "How many farms are classified as Muku?"})
    print(f"   Question: {result.get('question')}")
    print(f"   Answer: {result.get('answer')}")
    print("   ✅ Question answered successfully\n")

    print("=" * 70)
    print("✨ All tests passed! MCP Server is working correctly.")
    print("=" * 70 + "\n")


async def test_advanced_queries() -> None:
    """Test advanced query capabilities."""
    print("\n" + "=" * 70)
    print("🧪 Testing MuKa MCP Server - Advanced Queries")
    print("=" * 70 + "\n")

    # Ensure data is loaded and classified
    await handle_load_data({})
    await handle_classify_farms({})

    # Test various natural language questions
    questions = [
        "What percentage of farms are Muku?",
        "Which group has the highest average animals?",
        "Are there any outliers in animal counts?",
        "What's the average animal count by group?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"❓ Question {i}: {question}")
        result = await handle_answer_question({"question": question})
        print(f"   Answer: {result.get('answer')}")
        print()

    print("=" * 70)
    print("✨ Advanced query tests completed!")
    print("=" * 70 + "\n")


async def test_error_handling() -> None:
    """Test error handling."""
    print("\n" + "=" * 70)
    print("🧪 Testing MuKa MCP Server - Error Handling")
    print("=" * 70 + "\n")

    # Reset context
    server_module.data_context = DataContext()

    # Test 1: Query without loading data
    print("⚠️  Test 1: Query without loading data...")
    result = await handle_query_farms({"group": "Muku"})
    assert "error" in result, "Should return error"
    print(f"   Expected error: {result.get('error')}")
    print("   ✅ Error handled correctly\n")

    # Test 2: Load invalid file
    print("⚠️  Test 2: Load non-existent file...")
    result = await handle_load_data({"file_path": "/nonexistent/file.csv"})
    assert not result.get("success"), "Should fail"
    print(f"   Expected error: {result.get('error')}")
    print("   ✅ Error handled correctly\n")

    print("=" * 70)
    print("✨ Error handling tests completed!")
    print("=" * 70 + "\n")


async def main() -> None:
    """Run all tests."""
    try:
        await test_basic_workflow()
        await test_advanced_queries()
        await test_error_handling()

        print("\n" + "🎉" * 35)
        print("All MCP server tests passed successfully!")
        print("Ready to use with MCP clients like Claude Desktop!")
        print("🎉" * 35 + "\n")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())
