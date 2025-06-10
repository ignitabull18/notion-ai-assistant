#!/usr/bin/env python3
"""Test Composio Notion integration"""

import os
import json
from dotenv import load_dotenv
from composio_agno import ComposioToolSet, Action

# Load environment variables
load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def test_composio_connection():
    """Test basic Composio connection and available actions."""
    print("🔧 Testing Composio connection...")
    
    try:
        # Initialize Composio
        composio_client = ComposioToolSet(api_key=os.getenv("COMPOSIO_TOKEN"))
        print("✅ Composio client initialized")
        
        # Check connected accounts
        accounts = composio_client.get_connected_accounts()
        print(f"📱 Connected accounts: {len(accounts)}")
        
        notion_connected = False
        for acc in accounts:
            app_name = getattr(acc, 'appName', 'Unknown')
            display_name = getattr(acc, 'accountDisplayName', 'N/A')
            print(f"  - {app_name}: {display_name}")
            if app_name == "notion":
                notion_connected = True
        
        if not notion_connected:
            print("❌ Notion is not connected! Please connect at: https://app.composio.dev")
            return False
        
        print("✅ Notion is connected!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_list_databases():
    """Test listing Notion databases."""
    print("\n📊 Testing NOTION_LIST_DATABASES...")
    
    try:
        composio_client = ComposioToolSet(api_key=os.getenv("COMPOSIO_TOKEN"))
        
        result = composio_client.execute_action(
            action=Action.NOTION_LIST_DATABASES,
            params={}
        )
        
        print(f"Raw result: {json.dumps(result, indent=2)[:500]}...")
        
        if result.get("data", {}).get("results"):
            databases = result["data"]["results"]
            print(f"✅ Found {len(databases)} database(s):")
            
            for i, db in enumerate(databases[:3]):  # Show first 3
                title = db.get("title", [{}])[0].get("plain_text", "Untitled")
                print(f"  {i+1}. {title} (ID: {db.get('id', 'N/A')[:8]}...)")
            
            return databases[0]["id"] if databases else None
        else:
            print("❌ No databases found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_search():
    """Test Notion search."""
    print("\n🔍 Testing NOTION_SEARCH...")
    
    try:
        composio_client = ComposioToolSet(api_key=os.getenv("COMPOSIO_TOKEN"))
        
        result = composio_client.execute_action(
            action=Action.NOTION_SEARCH,
            params={"query": "test"}
        )
        
        print(f"Raw result: {json.dumps(result, indent=2)[:500]}...")
        
        if result.get("data", {}).get("results"):
            results = result["data"]["results"]
            print(f"✅ Found {len(results)} result(s) for 'test':")
            
            for i, item in enumerate(results[:3]):  # Show first 3
                title = "Untitled"
                if item.get("properties", {}).get("title", {}).get("title"):
                    title = item["properties"]["title"]["title"][0].get("plain_text", "Untitled")
                
                print(f"  {i+1}. {title} ({item.get('object', 'unknown')}) ID: {item.get('id', 'N/A')[:8]}...")
            
            return results[0]["id"] if results else None
        else:
            print("❌ No search results found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_advanced_actions():
    """Test advanced Notion actions."""
    print("\n🧪 Testing advanced actions...")
    
    try:
        composio_client = ComposioToolSet(api_key=os.getenv("COMPOSIO_TOKEN"))
        
        # Test creating a page
        print("📝 Testing NOTION_CREATE_PAGE...")
        create_result = composio_client.execute_action(
            action=Action.NOTION_CREATE_PAGE,
            params={
                "properties": {
                    "title": [
                        {
                            "text": {
                                "content": "Test Page from Composio"
                            }
                        }
                    ]
                }
            }
        )
        
        if create_result.get("data", {}).get("id"):
            page_id = create_result["data"]["id"]
            print(f"✅ Created test page: {page_id[:8]}...")
            
            # Test reading the page
            print("📖 Testing NOTION_GET_PAGE...")
            read_result = composio_client.execute_action(
                action=Action.NOTION_GET_PAGE,
                params={"page_id": page_id}
            )
            
            if read_result.get("data"):
                print("✅ Successfully read the page")
            else:
                print("❌ Failed to read the page")
            
            # Test updating the page
            print("✏️ Testing NOTION_UPDATE_PAGE...")
            update_result = composio_client.execute_action(
                action=Action.NOTION_UPDATE_PAGE,
                params={
                    "page_id": page_id,
                    "properties": {
                        "title": [
                            {
                                "text": {
                                    "content": "Updated Test Page"
                                }
                            }
                        ]
                    }
                }
            )
            
            if update_result.get("data"):
                print("✅ Successfully updated the page")
            else:
                print("❌ Failed to update the page")
            
            return page_id
        else:
            print("❌ Failed to create test page")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_database_operations(database_id):
    """Test database operations."""
    if not database_id:
        print("\n⏭️ Skipping database tests (no database ID)")
        return
        
    print(f"\n📊 Testing database operations with ID: {database_id[:8]}...")
    
    try:
        composio_client = ComposioToolSet(api_key=os.getenv("COMPOSIO_TOKEN"))
        
        # Test querying database
        print("🔍 Testing NOTION_QUERY_DATABASE...")
        query_result = composio_client.execute_action(
            action=Action.NOTION_QUERY_DATABASE,
            params={"database_id": database_id}
        )
        
        if query_result.get("data", {}).get("results"):
            items = query_result["data"]["results"]
            print(f"✅ Found {len(items)} item(s) in database")
        else:
            print("ℹ️ No items found in database (this is normal)")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🧪 Testing Composio Notion Integration")
    print("=" * 50)
    
    # Test basic connection
    if not test_composio_connection():
        print("\n❌ Basic connection failed. Please check your Composio setup.")
        exit(1)
    
    # Test listing databases
    database_id = test_list_databases()
    
    # Test search
    search_page_id = test_search()
    
    # Test advanced actions
    created_page_id = test_advanced_actions()
    
    # Test database operations
    test_database_operations(database_id)
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete!")
    
    if created_page_id:
        print(f"⚠️ Note: Created test page {created_page_id[:8]}... - you may want to delete it from Notion")