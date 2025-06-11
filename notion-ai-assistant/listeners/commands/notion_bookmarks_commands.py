"""
Notion bookmarks command handlers
"""
from slack_bolt import Ack, Say
from slack_sdk.web import WebClient
from typing import Dict, Any
import asyncio

from listeners.notion_bookmarks import (
    NotionBookmarksManager,
    create_notion_bookmarks_blocks,
    create_add_notion_bookmark_modal
)
from listeners.agno_integration import process_with_agent
from listeners.ui_components import create_notion_status_blocks
from utils.logging import logger


def handle_notion_bookmarks_command(ack: Ack, command: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /notion-bookmarks command"""
    ack()
    
    try:
        channel_id = command["channel_id"]
        text = command.get("text", "").strip()
        user_id = command["user_id"]
        
        bookmarks_manager = NotionBookmarksManager(client)
        
        if not text or text == "list":
            # List Notion bookmarks
            bookmarks = bookmarks_manager.get_notion_bookmarks(channel_id)
            blocks = create_notion_bookmarks_blocks(bookmarks, channel_id)
            say(blocks=blocks)
            
        elif text == "sync":
            # Sync workspace bookmarks
            say(blocks=create_notion_status_blocks("processing", "Syncing Notion workspace bookmarks..."))
            
            # Get workspace data from agent
            workspace_info = asyncio.run(
                process_with_agent(
                    user_id=user_id,
                    message="List my most important databases and frequently accessed pages with their URLs"
                )
            )
            
            # Parse response and create bookmarks
            # This is simplified - in production, parse the agent response properly
            mock_workspace_data = {
                "name": "My Notion",
                "workspace_url": "https://notion.so/workspace",
                "databases": [
                    {"id": "db1", "title": "Tasks", "url": "https://notion.so/tasks"},
                    {"id": "db2", "title": "Projects", "url": "https://notion.so/projects"}
                ],
                "frequent_pages": [
                    {"id": "page1", "title": "Team Wiki", "url": "https://notion.so/wiki"},
                    {"id": "page2", "title": "Meeting Notes", "url": "https://notion.so/meetings"}
                ]
            }
            
            created = bookmarks_manager.sync_notion_workspace_bookmarks(channel_id, mock_workspace_data)
            say(f"✅ Synced {len(created)} Notion bookmarks!")
            
        elif text == "templates":
            # Add template bookmarks
            say(blocks=create_notion_status_blocks("processing", "Adding Notion template bookmarks..."))
            created = bookmarks_manager.create_notion_template_bookmarks(channel_id)
            
            if created:
                say(f"✅ Added {len(created)} Notion template bookmarks!")
            else:
                say("❌ Failed to add template bookmarks.")
                
        elif text == "organize":
            # Organize bookmarks
            organized = bookmarks_manager.organize_notion_bookmarks(channel_id)
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 Notion Bookmarks by Type"
                    }
                }
            ]
            
            for category, items in organized.items():
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{category}* ({len(items)} items)"
                    }
                })
                
                for bookmark in items[:3]:
                    blocks.append({
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": f"{bookmark.get('emoji', '📝')} <{bookmark['link']}|{bookmark['title']}>"
                        }]
                    })
                    
            say(blocks=blocks)
            
        elif text == "help":
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 Notion Bookmarks Help"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Available commands:*\n"
                                "• `/notion-bookmarks` - List all Notion bookmarks\n"
                                "• `/notion-bookmarks sync` - Sync workspace bookmarks\n"
                                "• `/notion-bookmarks templates` - Add template bookmarks\n"
                                "• `/notion-bookmarks organize` - View by type\n"
                                "• `/notion-bookmarks help` - Show this help"
                    }
                }
            ]
            say(blocks=blocks)
            
        else:
            say("Unknown command. Try `/notion-bookmarks help`")
            
    except Exception as e:
        logger.error(f"Error handling Notion bookmarks command: {e}")
        say("❌ Sorry, I couldn't process the bookmarks command.")


def handle_notion_bookmark_action(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle Notion bookmark button actions"""
    ack()
    
    try:
        action = body["actions"][0]
        action_id = action["action_id"]
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        bookmarks_manager = NotionBookmarksManager(client)
        
        if action_id.startswith("add_notion_templates_"):
            # Add template bookmarks
            created = bookmarks_manager.create_notion_template_bookmarks(channel_id)
            
            # Update the message
            bookmarks = bookmarks_manager.get_notion_bookmarks(channel_id)
            blocks = create_notion_bookmarks_blocks(bookmarks, channel_id)
            
            client.chat_update(
                channel=channel_id,
                ts=body["message"]["ts"],
                blocks=blocks
            )
            
        elif action_id.startswith("sync_notion_workspace_"):
            # Sync workspace
            # Show processing
            client.chat_update(
                channel=channel_id,
                ts=body["message"]["ts"],
                blocks=create_notion_status_blocks("processing", "Syncing Notion workspace...")
            )
            
            # Get workspace data
            workspace_info = asyncio.run(
                process_with_agent(
                    user_id=user_id,
                    message="List my Notion workspace structure"
                )
            )
            
            # Mock data for demo
            mock_workspace_data = {
                "name": "Workspace",
                "workspace_url": "https://notion.so",
                "databases": [],
                "frequent_pages": []
            }
            
            bookmarks_manager.sync_notion_workspace_bookmarks(channel_id, mock_workspace_data)
            
            # Update with new bookmarks
            bookmarks = bookmarks_manager.get_notion_bookmarks(channel_id)
            blocks = create_notion_bookmarks_blocks(bookmarks, channel_id)
            
            client.chat_update(
                channel=channel_id,
                ts=body["message"]["ts"],
                blocks=blocks
            )
            
        elif action_id.startswith("add_notion_bookmark_"):
            # Open modal
            client.views_open(
                trigger_id=body["trigger_id"],
                view=create_add_notion_bookmark_modal(channel_id)
            )
            
    except Exception as e:
        logger.error(f"Error handling Notion bookmark action: {e}")


def handle_add_notion_bookmark_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle add Notion bookmark modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        url = values["notion_url"]["url_input"]["value"]
        title = values["bookmark_title"]["title_input"]["value"]
        notion_type = values["notion_type"]["type_input"]["selected_option"]["value"]
        channel_id = body["view"]["private_metadata"]
        
        bookmarks_manager = NotionBookmarksManager(client)
        
        # Extract ID from URL if possible
        notion_id = bookmarks_manager.extract_notion_id_from_url(url)
        
        # Add the bookmark
        bookmark = bookmarks_manager.add_notion_bookmark(
            channel_id=channel_id,
            notion_data={
                "url": url,
                "title": title,
                "type": notion_type,
                "id": notion_id or "custom"
            }
        )
        
        if bookmark:
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Added Notion bookmark: {title}"
            )
        else:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to add bookmark. You may not have permission to add bookmarks to <#{channel_id}>."
            )
            
    except Exception as e:
        logger.error(f"Error adding Notion bookmark: {e}")