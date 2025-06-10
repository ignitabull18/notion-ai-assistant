#!/usr/bin/env python3
"""Inspect Composio tool schemas to see what parameters are available"""

import os
import json
from dotenv import load_dotenv
from composio_agno import ComposioToolSet, App

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def inspect_tool_schemas():
    composio_token = os.getenv("COMPOSIO_TOKEN")
    if not composio_token:
        print("❌ COMPOSIO_TOKEN not found")
        return
    
    try:
        toolset = ComposioToolSet(api_key=composio_token)
        
        # Get tools for Notion
        tools = toolset.get_tools(apps=[App.NOTION])
        print(f"✅ Found {len(tools)} Notion tools\n")
        
        # Inspect a few key tools
        key_tools = ["NOTION_CREATE_NOTION_PAGE", "NOTION_INSERT_ROW_DATABASE", "NOTION_ADD_PAGE_CONTENT"]
        
        # Look for problematic tools specifically
        problem_tools = ["NOTION_CREATE_NOTION_PAGE", "NOTION_INSERT_ROW_DATABASE"]
        
        for tool in tools:
            if tool.name in problem_tools:
                print(f"🔧 Tool: {tool.name}")
                
                # Check the functions attribute
                if hasattr(tool, 'functions'):
                    for func_name, func in tool.functions.items():
                        print(f"\nFunction: {func_name}")
                        print(f"Function type: {type(func)}")
                        
                        # Try to get parameters
                        if hasattr(func, 'parameters'):
                            print("Parameters:")
                            try:
                                if hasattr(func.parameters, 'model_json_schema'):
                                    schema = func.parameters.model_json_schema()
                                    print(json.dumps(schema, indent=2))
                                else:
                                    print(f"  {func.parameters}")
                            except Exception as e:
                                print(f"  Error getting parameters: {e}")
                        
                        # Check for other schema attributes
                        for attr in ['args_schema', 'signature', '__annotations__']:
                            if hasattr(func, attr):
                                print(f"{attr}: {getattr(func, attr)}")
                
                print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_tool_schemas()