#!/usr/bin/env python3
"""Get action schemas with correct method calls"""

import os
import json
from dotenv import load_dotenv
from composio_agno import ComposioToolSet

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def get_action_schemas():
    composio_token = os.getenv("COMPOSIO_TOKEN")
    if not composio_token:
        print("❌ COMPOSIO_TOKEN not found")
        return
    
    try:
        toolset = ComposioToolSet(api_key=composio_token)
        
        # Try get_action_schemas with correct parameter
        try:
            schemas = toolset.get_action_schemas(apps=["notion"])
            print(f"✅ Got {len(schemas)} action schemas")
            
            # Look for our problematic actions
            problem_actions = ["NOTION_CREATE_NOTION_PAGE", "NOTION_INSERT_ROW_DATABASE"]
            
            for action_name, schema in schemas.items():
                if action_name in problem_actions:
                    print(f"\n🔧 Schema for {action_name}:")
                    print(json.dumps(schema, indent=2))
                    print("\n" + "="*50)
                    
        except Exception as e:
            print(f"❌ get_action_schemas failed: {e}")
        
        # Try getting individual action
        try:
            action = toolset.get_action("NOTION_CREATE_NOTION_PAGE")
            print(f"\n✅ Got individual action: {type(action)}")
            
            # Explore the action object
            for attr in dir(action):
                if not attr.startswith('_') and not callable(getattr(action, attr, None)):
                    value = getattr(action, attr, None)
                    if value is not None:
                        print(f"  {attr}: {str(value)[:100]}")
                        
        except Exception as e:
            print(f"❌ get_action failed: {e}")
        
        # Try client.actions without parameters
        try:
            actions = toolset.client.actions.get()
            print(f"\n✅ Got {len(actions)} actions from client")
            
            # Find Notion actions
            notion_actions = [a for a in actions if 'notion' in a.app_name.lower()]
            print(f"Found {len(notion_actions)} Notion actions")
            
            for action in notion_actions[:2]:  # First 2
                print(f"\nAction: {action.name}")
                if hasattr(action, 'parameters'):
                    print(f"Parameters: {action.parameters}")
                if hasattr(action, 'input_params'):
                    print(f"Input params: {action.input_params}")
                    
        except Exception as e:
            print(f"❌ Client actions get failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_action_schemas()