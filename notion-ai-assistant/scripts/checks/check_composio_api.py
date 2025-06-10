#!/usr/bin/env python3
"""Check Composio API for action schemas"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def check_composio_api():
    composio_token = os.getenv("COMPOSIO_TOKEN")
    if not composio_token:
        print("❌ COMPOSIO_TOKEN not found")
        return
    
    try:
        # Try to get action schemas from Composio API
        headers = {
            "Authorization": f"Bearer {composio_token}",
            "Content-Type": "application/json"
        }
        
        # Get actions for Notion app
        url = "https://backend.composio.dev/api/v1/actions"
        params = {"appNames": "notion"}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            actions = response.json()
            print(f"✅ Found {len(actions.get('items', []))} Notion actions from API")
            
            # Look for our problematic actions
            problem_actions = ["NOTION_CREATE_NOTION_PAGE", "NOTION_INSERT_ROW_DATABASE"]
            
            for action in actions.get('items', []):
                if action.get('name') in problem_actions:
                    print(f"\n🔧 Action: {action.get('name')}")
                    print(f"Display Name: {action.get('displayName', 'N/A')}")
                    print(f"Description: {action.get('description', 'N/A')}")
                    
                    # Check for parameters
                    if 'parameters' in action:
                        print("Parameters:")
                        print(json.dumps(action['parameters'], indent=2))
                    elif 'inputParameters' in action:
                        print("Input Parameters:")
                        print(json.dumps(action['inputParameters'], indent=2))
                    else:
                        print("Available keys in action:", list(action.keys()))
                    
                    print("\n" + "="*50)
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_composio_api()