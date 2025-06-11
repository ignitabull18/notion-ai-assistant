"""
Bookmark command handlers for Slack AI Assistant
"""
from slack_bolt import Ack, Say, Respond
from slack_sdk.web import WebClient
from typing import Dict, Any

from listeners.bookmarks_manager import (
    BookmarksManager, 
    create_bookmarks_management_blocks,
    create_add_bookmark_modal
)
from listeners.ui_components import create_status_blocks
from utils.logging import logger


def handle_bookmarks_command(ack: Ack, command: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /bookmarks command"""
    ack()
    
    try:
        channel_id = command["channel_id"]
        text = command.get("text", "").strip()
        
        bookmarks_manager = BookmarksManager(client)
        
        # Parse command
        if not text or text == "list":
            # List bookmarks
            bookmarks = bookmarks_manager.list_bookmarks(channel_id)
            blocks = create_bookmarks_management_blocks(bookmarks, channel_id)
            say(blocks=blocks)
            
        elif text == "add":
            # Open add bookmark modal
            client.views_open(
                trigger_id=command["trigger_id"],
                view=create_add_bookmark_modal(channel_id)
            )
            
        elif text == "organize":
            # Organize bookmarks by category
            organized = bookmarks_manager.organize_bookmarks_by_category(channel_id)
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 Bookmarks by Category"
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
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{bookmark.get('emoji', '🔗')} <{bookmark['link']}|{bookmark['title']}>"
                        }
                    })
                    
                if len(items) > 3:
                    blocks.append({
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": f"_...and {len(items) - 3} more_"
                        }]
                    })
                    
                blocks.append({"type": "divider"})
            
            say(blocks=blocks)
            
        elif text == "defaults":
            # Add default bookmarks
            say(blocks=create_status_blocks("processing", "Adding default AI assistant bookmarks..."))
            created = bookmarks_manager.create_ai_assistant_bookmarks(channel_id)
            
            if created:
                say(f"✅ Added {len(created)} default bookmarks to this channel!")
            else:
                say("❌ Failed to add default bookmarks.")
                
        elif text.startswith("add "):
            # Quick add bookmark
            parts = text[4:].split(" ", 1)
            if len(parts) == 2:
                url, title = parts
                bookmark = bookmarks_manager.add_bookmark(
                    channel_id=channel_id,
                    title=title,
                    link=url,
                    emoji="🔗"
                )
                
                if bookmark:
                    say(f"✅ Added bookmark: {bookmark['title']}")
                else:
                    say("❌ Failed to add bookmark. Make sure the URL is valid.")
            else:
                say("Usage: `/bookmarks add <url> <title>`")
                
        elif text == "help":
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 Bookmarks Help"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Available commands:*\n"
                                "• `/bookmarks` or `/bookmarks list` - List all bookmarks\n"
                                "• `/bookmarks add` - Open modal to add bookmark\n"
                                "• `/bookmarks add <url> <title>` - Quick add\n"
                                "• `/bookmarks organize` - View by category\n"
                                "• `/bookmarks defaults` - Add default bookmarks\n"
                                "• `/bookmarks help` - Show this help"
                    }
                }
            ]
            say(blocks=blocks)
            
        else:
            say("Unknown bookmarks command. Try `/bookmarks help`")
            
    except Exception as e:
        logger.error(f"Error handling bookmarks command: {e}")
        say("❌ Sorry, I couldn't process the bookmarks command.")


def handle_bookmark_action(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle bookmark-related button actions"""
    ack()
    
    try:
        action = body["actions"][0]
        action_id = action["action_id"]
        channel_id = body["channel"]["id"]
        
        bookmarks_manager = BookmarksManager(client)
        
        if action_id.startswith("add_default_bookmarks_"):
            # Add default bookmarks
            created = bookmarks_manager.create_ai_assistant_bookmarks(channel_id)
            
            # Update the message
            bookmarks = bookmarks_manager.list_bookmarks(channel_id)
            blocks = create_bookmarks_management_blocks(bookmarks, channel_id)
            
            client.chat_update(
                channel=channel_id,
                ts=body["message"]["ts"],
                blocks=blocks
            )
            
        elif action_id.startswith("add_bookmark_"):
            # Open add bookmark modal
            client.views_open(
                trigger_id=body["trigger_id"],
                view=create_add_bookmark_modal(channel_id)
            )
            
        elif action_id.startswith("bookmark_menu_"):
            # Handle overflow menu selection
            selected_option = action["selected_option"]["value"]
            bookmark_id = action_id.replace("bookmark_menu_", "")
            
            if selected_option.startswith("remove_"):
                # Remove bookmark
                success = bookmarks_manager.remove_bookmark(channel_id, bookmark_id)
                
                if success:
                    # Update the message
                    bookmarks = bookmarks_manager.list_bookmarks(channel_id)
                    blocks = create_bookmarks_management_blocks(bookmarks, channel_id)
                    
                    client.chat_update(
                        channel=channel_id,
                        ts=body["message"]["ts"],
                        blocks=blocks
                    )
                    
            elif selected_option.startswith("edit_"):
                # TODO: Implement bookmark editing
                client.chat_postMessage(
                    channel=body["user"]["id"],
                    text="Bookmark editing coming soon!"
                )
                
    except Exception as e:
        logger.error(f"Error handling bookmark action: {e}")


def handle_add_bookmark_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle add bookmark modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        title = values["bookmark_title"]["title_input"]["value"]
        url = values["bookmark_url"]["url_input"]["value"]
        emoji = values["bookmark_category"]["category_input"]["selected_option"]["value"]
        channel_id = body["view"]["private_metadata"]
        
        bookmarks_manager = BookmarksManager(client)
        
        # Add the bookmark
        bookmark = bookmarks_manager.add_bookmark(
            channel_id=channel_id,
            title=title,
            link=url,
            emoji=emoji
        )
        
        if bookmark:
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Added bookmark: {emoji} {title}"
            )
        else:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to add bookmark. You may not have permission to add bookmarks to <#{channel_id}>."
            )
            
    except Exception as e:
        logger.error(f"Error adding bookmark: {e}")