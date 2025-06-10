#!/usr/bin/env python3
"""Test Slack formatting enhancements"""

import json
from listeners.slack_formatter import SlackFormatter

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
    
    # Test 3: Error message
    print("\n\n3️⃣ ERROR MESSAGE:")
    print("-" * 50)
    
    error_blocks = SlackFormatter.format_error_message(
        "Unable to connect to Notion. Please check your workspace permissions."
    )
    print(json.dumps(error_blocks, indent=2))
    
    # Test 4: Status update
    print("\n\n4️⃣ STATUS UPDATE:")
    print("-" * 50)
    
    status_blocks = SlackFormatter.format_status_update(
        action="Creating Marketing Projects Database",
        status="in_progress",
        details="Setting up properties and views..."
    )
    print(json.dumps(status_blocks, indent=2))
    
    print("\n✅ Formatting tests complete!")

if __name__ == "__main__":
    test_formatting()