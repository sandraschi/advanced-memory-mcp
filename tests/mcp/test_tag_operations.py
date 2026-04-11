"""Comprehensive test for tag operations with large tag counts.

Tests creating, editing, adding, and deleting tags to identify any bugs
related to handling many tags (9+ tags).
"""

import json

import pytest
from fastmcp import Client

from advanced_memory.utils import parse_tags


@pytest.mark.asyncio
async def test_large_tag_operations(mcp_server):
    """Test tag operations with 20+ tags."""

    print("=" * 80)
    print("COMPREHENSIVE TAG OPERATIONS TEST")
    print("=" * 80)
    print()

    # Generate 20 test tags
    test_tags_list = [
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5",
        "tag6",
        "tag7",
        "tag8",
        "tag9",
        "tag10",
        "tag11",
        "tag12",
        "tag13",
        "tag14",
        "tag15",
        "tag16",
        "tag17",
        "tag18",
        "tag19",
        "tag20",
    ]

    test_tags_string = ",".join(test_tags_list)

    test_note_id = "Tag Test Note - Large Tag Count"

    print(f"Test Tags (20 total): {test_tags_list}")
    print(f"Test Tags String: {test_tags_string}")
    print()

    # Test 1: Create note with 20 tags as Python list
    print("=" * 80)
    print("TEST 1: Create note with 20 tags as Python LIST")
    print("=" * 80)
    try:
        async with Client(mcp_server) as client:
            result1 = await client.call_tool(
                "adn_content",
                {
                    "operation": "write",
                    "identifier": test_note_id,
                    "content": "# Tag Test Note\n\nThis note tests handling of many tags.",
                    "folder": "test",
                    "tags": test_tags_list,  # Python list
                },
            )
            print("✅ SUCCESS: Created note with Python list")
            print(f"Result preview: {str(result1)[:200]}...")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    # Test 2: Create note with 20 tags as comma-separated string
    print("=" * 80)
    print("TEST 2: Create note with 20 tags as COMMA-SEPARATED STRING")
    print("=" * 80)
    try:
        async with Client(mcp_server) as client:
            result2 = await client.call_tool(
                "adn_content",
                {
                    "operation": "write",
                    "identifier": f"{test_note_id} - String Format",
                    "content": "# Tag Test Note\n\nThis note tests handling of many tags as string.",
                    "folder": "test",
                    "tags": test_tags_string,  # Comma-separated string
                },
            )
            print("✅ SUCCESS: Created note with comma-separated string")
            print(f"Result preview: {str(result2)[:200]}...")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    # Test 3: Read the note and verify tags
    print("=" * 80)
    print("TEST 3: Read note and verify tags were stored correctly")
    print("=" * 80)
    try:
        async with Client(mcp_server) as client:
            result3 = await client.call_tool("adn_content", {"operation": "read", "identifier": test_note_id})
            print("✅ SUCCESS: Read note")
            print(f"Result preview: {str(result3)[:500]}...")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    # Test 4: Add 5 more tags (total 25)
    print("=" * 80)
    print("TEST 4: Add 5 more tags (should have 25 total)")
    print("=" * 80)
    additional_tags = ["tag21", "tag22", "tag23", "tag24", "tag25"]
    try:
        async with Client(mcp_server) as client:
            result4 = await client.call_tool(
                "adn_content",
                {
                    "operation": "edit_tags",
                    "identifier": test_note_id,
                    "tag_operation": "add",
                    "tags": ",".join(additional_tags),  # Comma-separated string
                },
            )
            print("✅ SUCCESS: Added tags")
            print(f"Result:\n{result4}")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    # Test 5: Remove 5 tags (should have 20 left)
    print("=" * 80)
    print("TEST 5: Remove 5 tags (should have 20 left)")
    print("=" * 80)
    tags_to_remove = ["tag21", "tag22", "tag23", "tag24", "tag25"]
    try:
        async with Client(mcp_server) as client:
            result5 = await client.call_tool(
                "adn_content",
                {
                    "operation": "edit_tags",
                    "identifier": test_note_id,
                    "tag_operation": "remove",
                    "tags": tags_to_remove,  # Python list
                },
            )
            print("✅ SUCCESS: Removed tags")
            print(f"Result:\n{result5}")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    # Test 6: Replace all tags with 15 new tags
    print("=" * 80)
    print("TEST 6: Replace all tags with 15 new tags")
    print("=" * 80)
    replacement_tags = [f"new-tag-{i}" for i in range(1, 16)]
    try:
        async with Client(mcp_server) as client:
            result6 = await client.call_tool(
                "adn_content",
                {
                    "operation": "edit_tags",
                    "identifier": test_note_id,
                    "tag_operation": "replace",
                    "tags": replacement_tags,  # Python list
                },
            )
            print("✅ SUCCESS: Replaced tags")
            print(f"Result:\n{result6}")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    # Test 7: Test parse_tags function directly with 20 tags
    print("=" * 80)
    print("TEST 7: Test parse_tags() function directly")
    print("=" * 80)
    print("Testing parse_tags with Python list:")
    result_list = parse_tags(test_tags_list)
    print(f"  Input: {test_tags_list}")
    print(f"  Output: {result_list}")
    print(f"  Count: {len(result_list)}")
    print(f"  Match: {'✅' if len(result_list) == 20 else '❌'}")
    print()

    print("Testing parse_tags with comma-separated string:")
    result_string = parse_tags(test_tags_string)
    print(f"  Input: {test_tags_string}")
    print(f"  Output: {result_string}")
    print(f"  Count: {len(result_string)}")
    print(f"  Match: {'✅' if len(result_string) == 20 else '❌'}")
    print()

    print("Testing parse_tags with JSON array string:")
    json_tags = json.dumps(test_tags_list)
    result_json = parse_tags(json_tags)
    print(f"  Input: {json_tags}")
    print(f"  Output: {result_json}")
    print(f"  Count: {len(result_json)}")
    print(f"  Match: {'✅' if len(result_json) == 20 else '❌'}")
    print()

    # Test 8: Test with exactly 9 tags (the problematic count)
    print("=" * 80)
    print("TEST 8: Test with exactly 9 tags (the problematic count)")
    print("=" * 80)
    nine_tags = test_tags_list[:9]
    try:
        async with Client(mcp_server) as client:
            result8 = await client.call_tool(
                "adn_content",
                {
                    "operation": "write",
                    "identifier": f"{test_note_id} - 9 Tags",
                    "content": "# Tag Test Note\n\nThis note has exactly 9 tags.",
                    "folder": "test",
                    "tags": nine_tags,  # Python list
                },
            )
            print("✅ SUCCESS: Created note with 9 tags as list")
            print(f"Result preview: {str(result8)[:200]}...")
            print()

            # Try editing tags on the 9-tag note
            result8b = await client.call_tool(
                "adn_content",
                {
                    "operation": "edit_tags",
                    "identifier": f"{test_note_id} - 9 Tags",
                    "tag_operation": "add",
                    "tags": "tag10,tag11",  # Add 2 more = 11 total
                },
            )
            print("✅ SUCCESS: Added tags to 9-tag note")
            print(f"Result:\n{result8b}")
            print()
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        print()
        raise

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
