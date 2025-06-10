#!/usr/bin/env python3
"""Standalone test for Slack formatting - demonstrates the implementation"""

import json
import re
from typing import List, Dict, Any, Optional

# Copy of SlackFormatter class for standalone testing
class SlackFormatter:
    """Format agent responses using Slack Block Kit for beautiful UI"""
    
    @staticmethod
    def format_notion_databases(databases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format a list of Notion databases into beautiful Slack blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Notion Databases",
                    "emoji": True
                }
            },
            {"type": "divider"}
        ]
        
        for db in databases:
            db_name = db.get('title', [{}])[0].get('plain_text', 'Untitled')
            db_id = db.get('id', '')
            created_time = db.get('created_time', '')[:10]  # Just date
            
            # Database block with info and button
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{db_name}*\n`{db_id}`\n_Created: {created_time}_"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Open in Notion",
                        "emoji": True
                    },
                    "url": f"https://notion.so/{db_id.replace('-', '')}",
                    "action_id": f"open_db_{db_id}"
                }
            })
        
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Found *{len(databases)}* databases in your workspace"
                }
            ]
        })
        
        return blocks
    
    @staticmethod
    def format_agent_response(response_text: str) -> List[Dict[str, Any]]:
        """Convert agent markdown response to beautiful Slack blocks"""
        blocks = []
        
        # Split response into paragraphs
        paragraphs = response_text.split('\n\n')
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            # Headers (marked with #)
            if para.startswith('#'):
                level = len(para) - len(para.lstrip('#'))
                header_text = para.lstrip('#').strip()
                
                if level == 1:
                    blocks.append({
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": header_text,
                            "emoji": True
                        }
                    })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{header_text}*"
                        }
                    })
                blocks.append({"type": "divider"})
                
            # Bullet lists
            elif para.strip().startswith(('- ', '• ', '* ', '1. ')):
                list_items = []
                for line in para.split('\n'):
                    if line.strip().startswith(('- ', '• ', '* ')):
                        list_items.append(line.strip()[2:])
                    elif re.match(r'^\d+\.\s', line.strip()):
                        list_items.append(re.sub(r'^\d+\.\s', '', line.strip()))
                
                if list_items:
                    formatted_list = '\n'.join([f"• {item}" for item in list_items])
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": formatted_list
                        }
                    })
                    
            # Code blocks
            elif para.startswith('```'):
                code_content = para.strip('`').strip()
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{code_content}```"
                    }
                })
                
            # Regular paragraphs
            else:
                # Convert Notion links to clickable buttons
                notion_link_pattern = r'https://(?:www\.)?notion\.so/([a-f0-9\-]+)'
                if re.search(notion_link_pattern, para):
                    # Extract the link and create a section with button
                    match = re.search(notion_link_pattern, para)
                    link_text = para[:match.start()].strip()
                    
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": link_text if link_text else para
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Open in Notion",
                                "emoji": True
                            },
                            "url": match.group(0),
                            "action_id": f"open_link_{match.group(1)}"
                        }
                    })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": para
                        }
                    })
        
        # Add footer with Notion AI branding
        if blocks:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "✨ _Powered by Notion AI Assistant_"
                    }
                ]
            })
        
        return blocks


def test_formatting():
    """Test various formatting scenarios"""
    
    print("🎨 Testing Slack Block Kit Formatting\n")
    
    # Test 1: Database listing
    print("1️⃣ DATABASE LISTING:")
    print("-" * 50)
    
    test_databases = [
        {
            "id": "59833787-2cf9-4fdf-8782-e53db20768a5",
            "title": [{"plain_text": "Marketing Projects"}],
            "created_time": "2024-01-15T10:30:00Z"
        },
        {
            "id": "12345678-abcd-efgh-ijkl-1234567890ab",
            "title": [{"plain_text": "Content Calendar"}],
            "created_time": "2024-02-20T14:45:00Z"
        }
    ]
    
    blocks = SlackFormatter.format_notion_databases(test_databases)
    print(json.dumps(blocks, indent=2))
    
    # Test 2: Agent response with various elements
    print("\n\n2️⃣ AGENT RESPONSE FORMATTING:")
    print("-" * 50)
    
    test_response = """# Workspace Architecture Proposal

Here's a comprehensive plan for your marketing workspace:

## Database Structure

- **Projects Database**: Track all marketing campaigns
- **Content Calendar**: Schedule and manage content
- **Team Tasks**: Assign and monitor team responsibilities

### Implementation Steps

1. Create the main Marketing Hub page
2. Set up the three core databases
3. Link them with relations
4. Add useful views and filters

```
Marketing Hub/
├── Projects Database
├── Content Calendar
└── Team Tasks
```

Here's your workspace link: https://notion.so/59833787-2cf9-4fdf-8782-e53db20768a5

Let me know if you need help with the next steps!"""
    
    blocks = SlackFormatter.format_agent_response(test_response)
    print(json.dumps(blocks, indent=2))
    
    print("\n✅ Formatting tests complete!")
    print("\n📋 SUMMARY:")
    print("- Created beautiful Slack Block Kit formatting for database listings")
    print("- Added clickable 'Open in Notion' buttons for all links")
    print("- Implemented rich formatting for headers, lists, and code blocks")
    print("- Added context footers and dividers for visual separation")

if __name__ == "__main__":
    test_formatting()