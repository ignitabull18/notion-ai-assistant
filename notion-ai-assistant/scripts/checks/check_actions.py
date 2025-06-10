#!/usr/bin/env python3
"""Check available Notion actions in Composio"""

import os
from dotenv import load_dotenv
from composio import ComposioToolSet, Action

# Load environment variables
load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def check_notion_actions():
    """Check what Notion actions are available."""
    print("🔍 Checking available Notion actions...")
    
    try:
        # Get all action names that contain NOTION
        all_actions = [action for action in dir(Action) if 'NOTION' in action]
        
        print(f"Found {len(all_actions)} Notion-related actions:")
        for action in sorted(all_actions):
            print(f"  - {action}")
        
        return all_actions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def test_with_correct_action():
    """Test with a correct action name."""
    print("\n🧪 Testing with correct action names...")
    
    try:
        composio_client = ComposioToolSet(api_key=os.getenv("COMPOSIO_TOKEN"))
        
        # Try different possible action names
        possible_actions = [
            "NOTION_LIST_DATABASES",
            "LISTNOTIONPAGES", 
            "LIST_NOTION_DATABASES",
            "NOTION_DATABASE_LIST",
            "NOTION_SEARCH",
            "SEARCH_NOTION",
            "NOTION_CREATE_PAGE",
            "CREATE_NOTION_PAGE"
        ]
        
        for action_name in possible_actions:
            try:
                action = getattr(Action, action_name, None)
                if action:
                    print(f"✅ Found action: {action_name}")
                    # Try to execute it
                    result = composio_client.execute_action(
                        action=action,
                        params={}
                    )
                    print(f"  Result: {str(result)[:100]}...")
                    return action_name
                else:
                    print(f"❌ Action not found: {action_name}")
            except Exception as e:
                print(f"⚠️ Error with {action_name}: {str(e)[:100]}...")
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    print("🔍 Checking Composio Notion Actions")
    print("=" * 50)
    
    # Check what actions exist
    actions = check_notion_actions()
    
    # Test with correct action
    working_action = test_with_correct_action()
    
    print("\n" + "=" * 50)
    if working_action:
        print(f"✅ Found working action: {working_action}")
    else:
        print("❌ No working Notion actions found")