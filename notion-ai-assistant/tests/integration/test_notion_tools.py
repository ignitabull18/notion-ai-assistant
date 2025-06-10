#!/usr/bin/env python3
"""Test Notion tool availability and functionality"""

import os
import asyncio
from dotenv import load_dotenv
from composio_agno import ComposioToolSet, App

load_dotenv()

async def test_notion_tools():
    """Test what Notion tools are available"""
    composio_key = os.getenv("COMPOSIO_TOKEN")
    if not composio_key:
        print("❌ COMPOSIO_TOKEN not found in environment")
        return
    
    print("✅ Found COMPOSIO_TOKEN")
    
    try:
        # Create toolset
        toolset = ComposioToolSet(api_key=composio_key)
        print("✅ Created ComposioToolSet")
        
        # Try to get Notion tools
        try:
            tools = toolset.get_tools(apps=[App.NOTION])
            print(f"✅ Got {len(tools)} Notion tools")
            
            # Print first few tool names
            print("\nAvailable Notion tools:")
            for i, tool in enumerate(tools[:10]):
                if hasattr(tool, 'name'):
                    print(f"  - {tool.name}")
                elif hasattr(tool, '__name__'):
                    print(f"  - {tool.__name__}")
                else:
                    print(f"  - {type(tool)}")
                    
        except Exception as e:
            print(f"❌ Error getting tools: {e}")
            
        # Try to list databases directly
        print("\n🔍 Attempting to list Notion databases...")
        try:
            # Try NOTION_FETCH_DATABASE
            result = toolset.execute_action(
                action="NOTION_FETCH_DATABASE",
                params={}
            )
            print(f"✅ NOTION_FETCH_DATABASE result type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Keys: {list(result.keys())}")
                print(f"   Successful: {result.get('successful', result.get('successfull'))}")
                if result.get('error'):
                    print(f"   ❌ Error: {result['error']}")
                if 'data' in result:
                    print(f"   Data: {result['data']}")
                    
                # Try with search endpoint instead
                print("\n🔍 Trying NOTION_SEARCH...")
                search_result = toolset.execute_action(
                    action="NOTION_SEARCH",
                    params={"query": "", "filter": {"property": "object", "value": "database"}}
                )
                print(f"   Search result: {search_result}")
        except Exception as e:
            print(f"❌ NOTION_FETCH_DATABASE failed: {e}")
            
    except Exception as e:
        print(f"❌ Failed to create toolset: {e}")

if __name__ == "__main__":
    asyncio.run(test_notion_tools())