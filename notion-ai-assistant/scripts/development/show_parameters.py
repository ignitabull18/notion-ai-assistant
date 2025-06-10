#!/usr/bin/env python3
"""Show full parameters for problematic actions"""

import os
import json
from dotenv import load_dotenv
from composio_agno import ComposioToolSet

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def show_parameters():
    composio_token = os.getenv("COMPOSIO_TOKEN")
    if not composio_token:
        print("❌ COMPOSIO_TOKEN not found")
        return
    
    try:
        toolset = ComposioToolSet(api_key=composio_token)
        
        problem_actions = ["NOTION_CREATE_NOTION_PAGE", "NOTION_INSERT_ROW_DATABASE"]
        
        for action_name in problem_actions:
            print(f"\n🔧 Action: {action_name}")
            print("="*50)
            
            try:
                action = toolset.get_action(action_name)
                
                # Show the parameters
                if hasattr(action, 'parameters'):
                    print("Raw parameters object:")
                    print(f"Type: {type(action.parameters)}")
                    
                    # Try to convert to dict
                    if hasattr(action.parameters, 'model_dump'):
                        params_dict = action.parameters.model_dump()
                        print("Parameters as dict:")
                        print(json.dumps(params_dict, indent=2))
                    elif hasattr(action.parameters, 'dict'):
                        params_dict = action.parameters.dict()
                        print("Parameters as dict:")
                        print(json.dumps(params_dict, indent=2))
                    else:
                        print("Available attributes:")
                        for attr in dir(action.parameters):
                            if not attr.startswith('_'):
                                print(f"  - {attr}")
                        params_dict = None
                    
                    # Show what fields are available
                    if params_dict and 'properties' in params_dict:
                        print("\nAvailable fields:")
                        for field_name, field_info in params_dict['properties'].items():
                            required = field_name in params_dict.get('required', [])
                            default = field_info.get('default', 'No default')
                            description = field_info.get('description', 'No description')
                            print(f"  - {field_name} ({'required' if required else 'optional'})")
                            print(f"    Type: {field_info.get('type', 'unknown')}")
                            print(f"    Default: {default}")
                            print(f"    Description: {description[:100]}...")
                            print()
                
            except Exception as e:
                print(f"❌ Error getting action {action_name}: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_parameters()