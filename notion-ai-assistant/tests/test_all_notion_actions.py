#!/usr/bin/env python3
"""Test all 20 Notion actions to ensure they're properly accessible"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from composio import ComposioToolSet, Action

# Load environment variables
load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def test_all_notion_actions():
    """Test that all 20 Notion actions are accessible."""
    print("🔍 Testing all 20 Notion actions...")
    print("=" * 60)
    
    # List of all 20 Notion actions
    notion_actions = [
        ("NOTION_ADD_PAGE_CONTENT", "Add content to a Notion page"),
        ("NOTION_APPEND_BLOCK_CHILDREN", "Append blocks as children"),
        ("NOTION_ARCHIVE_NOTION_PAGE", "Archive a Notion page"),
        ("NOTION_CREATE_COMMENT", "Create a comment"),
        ("NOTION_CREATE_DATABASE", "Create a new database"),
        ("NOTION_CREATE_NOTION_PAGE", "Create a new Notion page"),
        ("NOTION_DELETE_BLOCK", "Delete a block"),
        ("NOTION_DUPLICATE_PAGE", "Duplicate a page"),
        ("NOTION_FETCH_COMMENTS", "Fetch comments"),
        ("NOTION_FETCH_DATA", "Fetch data"),
        ("NOTION_FETCH_DATABASE", "Fetch database info"),
        ("NOTION_FETCH_NOTION_BLOCK", "Fetch a Notion block"),
        ("NOTION_FETCH_NOTION_CHILD_BLOCK", "Fetch child blocks"),
        ("NOTION_FETCH_ROW", "Fetch a database row"),
        ("NOTION_GET_ABOUT_ME", "Get info about current user"),
        ("NOTION_GET_ABOUT_USER", "Get info about a user"),
        ("NOTION_GET_PAGE_PROPERTY_ACTION", "Get page properties"),
        ("NOTION_INSERT_ROW_DATABASE", "Insert a row in database"),
        ("NOTION_LIST_USERS", "List all users"),
        ("NOTION_NOTION_UPDATE_BLOCK", "Update a block")
    ]
    
    # Check each action
    successful = 0
    failed = []
    
    for action_name, description in notion_actions:
        try:
            # Check if the action exists as an attribute of Action class
            action = getattr(Action, action_name, None)
            if action is not None:
                print(f"✅ {action_name:<35} - {description}")
                successful += 1
            else:
                print(f"❌ {action_name:<35} - NOT FOUND")
                failed.append(action_name)
        except Exception as e:
            print(f"❌ {action_name:<35} - ERROR: {str(e)}")
            failed.append(action_name)
    
    # Summary
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  ✅ Successful: {successful}/20")
    print(f"  ❌ Failed: {len(failed)}/20")
    
    if failed:
        print(f"\n❌ Failed actions:")
        for action in failed:
            print(f"  - {action}")
    
    # Try to initialize ComposioToolSet with the actions
    if successful > 0:
        print("\n🧪 Testing ComposioToolSet initialization...")
        try:
            composio_key = os.getenv("COMPOSIO_TOKEN")
            if composio_key:
                composio_toolset = ComposioToolSet(api_key=composio_key)
                print("✅ ComposioToolSet initialized successfully")
                
                # Try to get tools for the successful actions
                print("\n🔧 Testing tool generation for successful actions...")
                test_actions = []
                for action_name, _ in notion_actions:
                    action = getattr(Action, action_name, None)
                    if action is not None:
                        test_actions.append(action)
                        if len(test_actions) >= 3:  # Test with first 3 actions
                            break
                
                try:
                    tools = composio_toolset.get_tools(actions=test_actions)
                    print(f"✅ Successfully generated tools for {len(test_actions)} actions")
                    print(f"   Generated {len(tools)} tool(s)")
                except Exception as e:
                    print(f"⚠️  Tool generation failed: {str(e)}")
                    print("   Note: This might be expected if actions need specific setup")
                    
            else:
                print("⚠️  COMPOSIO_TOKEN not found in environment")
        except Exception as e:
            print(f"❌ ComposioToolSet initialization failed: {str(e)}")
    
    return successful == 20


if __name__ == "__main__":
    print("🚀 Testing All Notion Actions in Composio")
    print("=" * 60)
    
    # Run the test
    all_working = test_all_notion_actions()
    
    print("\n" + "=" * 60)
    if all_working:
        print("✅ All 20 Notion actions are properly accessible!")
    else:
        print("⚠️  Some Notion actions are not accessible. Check the output above.")