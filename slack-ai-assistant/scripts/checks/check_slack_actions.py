#!/usr/bin/env python3
"""
Check available Slack actions in Composio
"""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from composio import ComposioToolSet, AppType


def main():
    print("🔍 Checking available Slack actions in Composio...")
    print("="*60)
    
    try:
        toolset = ComposioToolSet()
        
        # Get all Slack actions
        print("\n📋 Available Slack Actions:")
        print("-"*40)
        
        slack_actions = toolset.get_actions(
            apps=[AppType.SLACK]
        )
        
        action_list = []
        for i, action in enumerate(slack_actions, 1):
            action_name = action.name if hasattr(action, 'name') else str(action)
            print(f"{i}. {action_name}")
            action_list.append(action_name)
            
        print(f"\n✅ Total Slack actions available: {len(slack_actions)}")
        
        # Save to JSON for reference
        output_path = Path(__file__).parent.parent.parent / "data" / "slack_actions.json"
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(action_list, f, indent=2)
            
        print(f"\n💾 Saved action list to: {output_path}")
        
        # Show some key actions
        print("\n🌟 Key Actions for Slack Assistant:")
        print("-"*40)
        key_actions = [
            "SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL",
            "SLACK_SCHEDULES_A_MESSAGE_TO_A_CHANNEL_AT_A_SPECIFIED_TIME",
            "SLACK_CREATE_A_REMINDER",
            "SLACK_SEARCH_FOR_MESSAGES_WITH_QUERY",
            "SLACK_FETCHES_A_CONVERSATIONS_HISTORY"
        ]
        
        for action in key_actions:
            if action in action_list:
                print(f"✓ {action}")
            else:
                print(f"✗ {action} (not found)")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()