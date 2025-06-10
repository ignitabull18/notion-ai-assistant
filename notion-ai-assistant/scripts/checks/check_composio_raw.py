#!/usr/bin/env python3
"""Check raw Composio for action information"""

import os
from dotenv import load_dotenv
from composio_agno import ComposioToolSet

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def check_raw_composio():
    composio_token = os.getenv("COMPOSIO_TOKEN")
    if not composio_token:
        print("❌ COMPOSIO_TOKEN not found")
        return
    
    try:
        toolset = ComposioToolSet(api_key=composio_token)
        
        # Try different methods to get action info
        print("Available methods on ComposioToolSet:")
        methods = [m for m in dir(toolset) if not m.startswith('_') and 'action' in m.lower()]
        for method in methods:
            print(f"  - {method}")
        
        # Try to get action schema
        if hasattr(toolset, 'get_action_schemas'):
            try:
                schemas = toolset.get_action_schemas(app="notion")
                print(f"\n✅ Got action schemas: {len(schemas)}")
            except Exception as e:
                print(f"❌ get_action_schemas failed: {e}")
        
        # Try client methods
        if hasattr(toolset, 'client'):
            print(f"\nClient type: {type(toolset.client)}")
            client_methods = [m for m in dir(toolset.client) if not m.startswith('_')]
            print("Client methods:", client_methods[:10])  # First 10
            
            # Try to get actions directly from client
            if hasattr(toolset.client, 'actions'):
                try:
                    actions = toolset.client.actions.get(app_names=["notion"])
                    print(f"\n✅ Got {len(actions)} actions from client")
                    
                    # Look for our problem action
                    for action in actions:
                        if hasattr(action, 'name') and action.name == "NOTION_CREATE_NOTION_PAGE":
                            print(f"\nFound NOTION_CREATE_NOTION_PAGE:")
                            for attr in dir(action):
                                if not attr.startswith('_'):
                                    print(f"  {attr}: {getattr(action, attr, 'N/A')}")
                            break
                            
                except Exception as e:
                    print(f"❌ Client actions failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_raw_composio()