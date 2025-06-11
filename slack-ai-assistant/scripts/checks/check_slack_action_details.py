#!/usr/bin/env python3
"""Get detailed information about Slack actions including parameters"""

import os
import json
from dotenv import load_dotenv
from composio import ComposioToolSet, Action

load_dotenv("/Users/ignitabull/Desktop/agno/.env")

def get_slack_action_details():
    """Get detailed information about each Slack action"""
    composio_token = os.getenv("COMPOSIO_TOKEN")
    if not composio_token:
        print("❌ COMPOSIO_TOKEN not found")
        return
    
    try:
        toolset = ComposioToolSet(api_key=composio_token)
        
        # Get all Slack action schemas
        schemas = toolset.get_action_schemas(apps=["slack"])
        print(f"✅ Found {len(schemas)} Slack actions")
        print("=" * 80)
        
        detailed_actions = []
        
        # Process each action
        for idx, schema in enumerate(schemas):
            if isinstance(schema, dict):
                action_info = {
                    'name': schema.get('name', 'Unknown'),
                    'displayName': schema.get('displayName', ''),
                    'description': schema.get('description', ''),
                    'parameters': schema.get('parameters', {}),
                    'response': schema.get('response', {})
                }
            else:
                # Handle object type
                action_info = {
                    'name': getattr(schema, 'name', 'Unknown'),
                    'displayName': getattr(schema, 'display_name', ''),
                    'description': getattr(schema, 'description', ''),
                    'parameters': getattr(schema, 'parameters', {}),
                    'response': getattr(schema, 'response', {})
                }
            
            detailed_actions.append(action_info)
            
            # Display action details
            print(f"\n{idx + 1}. {action_info['name']}")
            print(f"   Display: {action_info['displayName']}")
            print(f"   Description: {action_info['description'][:100]}...")
            
            # Show parameters if available
            if action_info['parameters']:
                print("   Parameters:")
                if isinstance(action_info['parameters'], dict):
                    for param_name, param_info in action_info['parameters'].items():
                        required = param_info.get('required', False) if isinstance(param_info, dict) else False
                        desc = param_info.get('description', 'No description') if isinstance(param_info, dict) else str(param_info)
                        print(f"     - {param_name}: {desc[:70]}... {'[REQUIRED]' if required else '[OPTIONAL]'}")
                else:
                    print(f"     {action_info['parameters']}")
        
        # Save detailed information
        output_file = "/Users/ignitabull/Desktop/agno/notion-ai-assistant/data/slack_actions_detailed.json"
        with open(output_file, 'w') as f:
            json.dump(detailed_actions, f, indent=2)
        print(f"\n💾 Saved detailed action info to: {output_file}")
        
        # Show use cases for the assistant
        print("\n🎯 Potential Use Cases for Slack Assistant:")
        print("=" * 80)
        
        use_cases = [
            {
                "action": "SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL",
                "use_case": "Send task completion notifications, reminders, or status updates"
            },
            {
                "action": "SLACK_CREATE_A_REMINDER",
                "use_case": "Set reminders for meetings, deadlines, or follow-ups"
            },
            {
                "action": "SLACK_SEARCH_FOR_MESSAGES_WITH_QUERY",
                "use_case": "Search for previous discussions, decisions, or shared links"
            },
            {
                "action": "SLACK_ADD_REACTION_TO_AN_ITEM",
                "use_case": "Acknowledge messages or indicate task status with emojis"
            },
            {
                "action": "SLACK_SCHEDULES_A_MESSAGE_TO_A_CHANNEL_AT_A_SPECIFIED_TIME",
                "use_case": "Schedule daily standup reminders or weekly reports"
            },
            {
                "action": "SLACK_FETCH_CONVERSATION_HISTORY",
                "use_case": "Summarize channel discussions or extract action items"
            },
            {
                "action": "SLACK_LIST_ALL_SLACK_TEAM_USERS_WITH_PAGINATION",
                "use_case": "Find team members with specific skills or availability"
            },
            {
                "action": "SLACK_UPDATES_A_SLACK_MESSAGE",
                "use_case": "Update task status messages or correct information"
            }
        ]
        
        for use_case in use_cases:
            print(f"\n• {use_case['action']}")
            print(f"  → {use_case['use_case']}")
        
        # Example integrations with Notion
        print("\n🔗 Slack + Notion Integration Ideas:")
        print("=" * 80)
        print("1. When a task is completed in Notion → Send Slack notification")
        print("2. Create Notion task from Slack message → Add to project database")
        print("3. Schedule weekly Slack summary → Pull data from Notion dashboards")
        print("4. Search Slack for context → Add to Notion meeting notes")
        print("5. Set reminder in Slack → Create corresponding Notion reminder")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_slack_action_details()