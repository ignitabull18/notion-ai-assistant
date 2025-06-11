"""
Lists command handlers for Slack AI Assistant
"""
from slack_bolt import Ack, Say
from slack_sdk.web import WebClient
from typing import Dict, Any

from listeners.lists_manager import (
    ListsManager,
    create_list_management_blocks,
    create_add_list_item_modal,
    create_list_templates_blocks
)
from listeners.ui_components import create_status_blocks
from utils.logging import logger


def handle_lists_command(ack: Ack, command: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /ai-lists command"""
    ack()
    
    try:
        channel_id = command["channel_id"]
        text = command.get("text", "").strip()
        
        lists_manager = ListsManager(client)
        
        if not text or text == "help":
            # Show help
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 Lists Help"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Available commands:*\n"
                                "• `/ai-lists templates` - View list templates\n"
                                "• `/ai-lists create <title>` - Create a new list\n"
                                "• `/ai-lists add <list_id> <item>` - Quick add item\n"
                                "• `/ai-lists show <list_id>` - View a list\n"
                                "• `/ai-lists help` - Show this help"
                    }
                }
            ]
            say(blocks=blocks)
            
        elif text == "templates":
            # Show templates
            blocks = create_list_templates_blocks()
            say(blocks=blocks)
            
        elif text.startswith("create "):
            # Create new list
            title = text[7:].strip()
            if title:
                say(blocks=create_status_blocks("processing", f"Creating list: {title}..."))
                
                list_obj = lists_manager.create_list(
                    channel_id=channel_id,
                    title=title,
                    description=f"Created via /ai-lists command",
                    emoji="📋"
                )
                
                if list_obj:
                    say(f"✅ Created list: *{title}*\nList ID: `{list_obj['id']}`")
                else:
                    say("❌ Failed to create list.")
            else:
                say("Please provide a list title. Usage: `/ai-lists create <title>`")
                
        elif text.startswith("add "):
            # Quick add item
            parts = text[4:].split(" ", 1)
            if len(parts) == 2:
                list_id, item_text = parts
                
                item = lists_manager.add_item(
                    list_id=list_id,
                    text=item_text
                )
                
                if item:
                    say(f"✅ Added item to list {list_id}")
                else:
                    say("❌ Failed to add item. Check the list ID.")
            else:
                say("Usage: `/ai-lists add <list_id> <item text>`")
                
        elif text.startswith("show "):
            # Show specific list
            list_id = text[5:].strip()
            list_data = lists_manager.get_list(list_id)
            
            if list_data:
                blocks = create_list_management_blocks(list_data)
                say(blocks=blocks)
            else:
                say(f"❌ List not found: {list_id}")
                
        else:
            say("Unknown command. Try `/ai-lists help`")
            
    except Exception as e:
        logger.error(f"Error handling lists command: {e}")
        say("❌ Sorry, I couldn't process the lists command.")


def handle_list_action(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle list-related button actions"""
    ack()
    
    try:
        action = body["actions"][0]
        action_id = action["action_id"]
        channel_id = body["channel"]["id"]
        
        lists_manager = ListsManager(client)
        
        if action_id.startswith("complete_item_"):
            # Complete an item
            item_id = action["value"]
            list_id = item_id.split("_")[0]  # Extract list ID
            
            success = lists_manager.update_item_status(
                list_id=list_id,
                item_id=item_id,
                status=lists_manager.ListItemStatus.COMPLETED
            )
            
            if success:
                # Refresh the list display
                list_data = lists_manager.get_list(list_id)
                if list_data:
                    blocks = create_list_management_blocks(list_data)
                    client.chat_update(
                        channel=channel_id,
                        ts=body["message"]["ts"],
                        blocks=blocks
                    )
                    
        elif action_id.startswith("add_list_item_"):
            # Open add item modal
            list_id = action_id.replace("add_list_item_", "")
            list_data = lists_manager.get_list(list_id)
            
            if list_data:
                client.views_open(
                    trigger_id=body["trigger_id"],
                    view=create_add_list_item_modal(list_id, list_data["title"])
                )
                
        elif action_id.startswith("view_full_list_"):
            # Show full list details
            list_id = action_id.replace("view_full_list_", "")
            list_data = lists_manager.get_list(list_id)
            
            if list_data:
                # Show in thread or ephemeral message
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=body["user"]["id"],
                    text=f"Full list view for: {list_data['title']}\n"
                         f"Total items: {len(list_data.get('items', []))}"
                )
                
        elif action_id.startswith("use_") and action_id.endswith("_template"):
            # Use a template
            template_type = action["value"]
            
            if template_type == "task":
                list_obj = lists_manager.create_task_list(
                    channel_id=channel_id,
                    title="Team Tasks",
                    tasks=[
                        {"text": "Define project scope"},
                        {"text": "Create timeline"},
                        {"text": "Assign responsibilities"},
                        {"text": "Set up kickoff meeting"}
                    ]
                )
            elif template_type == "shopping":
                list_obj = lists_manager.create_shopping_list(
                    channel_id=channel_id,
                    items=["Office supplies", "Snacks", "Cleaning supplies"]
                )
            elif template_type == "project":
                list_obj = lists_manager.create_project_checklist(
                    channel_id=channel_id,
                    project_name="Q1 Project",
                    milestones=[
                        {"text": "Requirements gathering", "due_date": "2024-01-15"},
                        {"text": "Design phase", "due_date": "2024-02-01"},
                        {"text": "Development", "due_date": "2024-03-01"},
                        {"text": "Testing & QA", "due_date": "2024-03-15"},
                        {"text": "Launch", "due_date": "2024-03-31"}
                    ]
                )
            else:
                list_obj = None
            
            if list_obj:
                blocks = create_list_management_blocks(list_obj)
                say(blocks=blocks)
                
    except Exception as e:
        logger.error(f"Error handling list action: {e}")


def handle_add_list_item_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle add list item modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        list_id = body["view"]["private_metadata"]
        
        item_text = values["item_text"]["text_input"]["value"]
        assignee = values.get("item_assignee", {}).get("assignee_input", {}).get("selected_user")
        due_date = values.get("item_due_date", {}).get("due_date_input", {}).get("selected_date")
        priority = values.get("item_priority", {}).get("priority_input", {}).get("selected_option", {}).get("value")
        
        lists_manager = ListsManager(client)
        
        # Add the item
        item = lists_manager.add_item(
            list_id=list_id,
            text=item_text,
            assignee=assignee,
            due_date=due_date,
            priority=int(priority) if priority else None
        )
        
        if item:
            # Get channel from somewhere (stored with list)
            # For now, post to user
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"✅ Added item to list: {item_text}"
            )
        else:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text="❌ Failed to add item to list."
            )
            
    except Exception as e:
        logger.error(f"Error adding list item: {e}")