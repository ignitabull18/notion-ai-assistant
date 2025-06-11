"""
Bookmarks Manager for Slack AI Assistant
Handles creating, updating, and managing channel bookmarks
"""
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List, Optional
from datetime import datetime

from listeners.ui_components import create_status_blocks
from utils.logging import logger


class BookmarksManager:
    """Manages Slack channel bookmarks"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def add_bookmark(self, channel_id: str, title: str, link: str, 
                    emoji: Optional[str] = None, entity_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Add a bookmark to a channel
        
        Args:
            channel_id: The channel to add bookmark to
            title: Bookmark title
            link: URL to bookmark
            emoji: Optional emoji icon
            entity_id: Optional entity ID for deduplication
            
        Returns:
            Bookmark object if successful, None otherwise
        """
        try:
            params = {
                "channel_id": channel_id,
                "title": title,
                "type": "link",
                "link": link
            }
            
            if emoji:
                params["emoji"] = emoji
            if entity_id:
                params["entity_id"] = entity_id
                
            response = self.client.bookmarks_add(**params)
            return response.get("bookmark")
            
        except SlackApiError as e:
            logger.error(f"Error adding bookmark: {e.response['error']}")
            return None
    
    def update_bookmark(self, channel_id: str, bookmark_id: str, 
                       title: Optional[str] = None, link: Optional[str] = None,
                       emoji: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update an existing bookmark"""
        try:
            params = {
                "channel_id": channel_id,
                "bookmark_id": bookmark_id
            }
            
            if title:
                params["title"] = title
            if link:
                params["link"] = link
            if emoji:
                params["emoji"] = emoji
                
            response = self.client.bookmarks_edit(**params)
            return response.get("bookmark")
            
        except SlackApiError as e:
            logger.error(f"Error updating bookmark: {e.response['error']}")
            return None
    
    def remove_bookmark(self, channel_id: str, bookmark_id: str) -> bool:
        """Remove a bookmark from a channel"""
        try:
            self.client.bookmarks_remove(
                channel_id=channel_id,
                bookmark_id=bookmark_id
            )
            return True
            
        except SlackApiError as e:
            logger.error(f"Error removing bookmark: {e.response['error']}")
            return False
    
    def list_bookmarks(self, channel_id: str) -> List[Dict[str, Any]]:
        """List all bookmarks in a channel"""
        try:
            response = self.client.bookmarks_list(channel_id=channel_id)
            return response.get("bookmarks", [])
            
        except SlackApiError as e:
            logger.error(f"Error listing bookmarks: {e.response['error']}")
            return []
    
    def create_ai_assistant_bookmarks(self, channel_id: str) -> List[Dict[str, Any]]:
        """Create default AI assistant bookmarks for a channel"""
        default_bookmarks = [
            {
                "title": "AI Assistant Help",
                "link": "https://slack.com/help/articles/1500001478722",
                "emoji": "🤖",
                "entity_id": "ai_help"
            },
            {
                "title": "Workspace Dashboard",
                "link": "https://app.slack.com/client",
                "emoji": "📊",
                "entity_id": "workspace_dashboard"
            },
            {
                "title": "Team Directory",
                "link": "https://slack.com/intl/en-us/help/articles/360003534892",
                "emoji": "👥",
                "entity_id": "team_directory"
            },
            {
                "title": "Shortcuts Guide",
                "link": "https://slack.com/help/articles/201374536",
                "emoji": "⚡",
                "entity_id": "shortcuts_guide"
            }
        ]
        
        created_bookmarks = []
        for bookmark in default_bookmarks:
            result = self.add_bookmark(
                channel_id=channel_id,
                title=bookmark["title"],
                link=bookmark["link"],
                emoji=bookmark.get("emoji"),
                entity_id=bookmark.get("entity_id")
            )
            if result:
                created_bookmarks.append(result)
        
        return created_bookmarks
    
    def create_resource_bookmark(self, channel_id: str, resource_type: str, 
                               resource_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a bookmark for a specific resource"""
        resource_configs = {
            "document": {
                "emoji": "📄",
                "title_prefix": "Doc: "
            },
            "dashboard": {
                "emoji": "📊",
                "title_prefix": "Dashboard: "
            },
            "report": {
                "emoji": "📈",
                "title_prefix": "Report: "
            },
            "tool": {
                "emoji": "🔧",
                "title_prefix": "Tool: "
            },
            "reference": {
                "emoji": "📚",
                "title_prefix": "Ref: "
            }
        }
        
        config = resource_configs.get(resource_type, {"emoji": "🔗", "title_prefix": ""})
        
        return self.add_bookmark(
            channel_id=channel_id,
            title=f"{config['title_prefix']}{resource_data.get('title', 'Resource')}",
            link=resource_data["url"],
            emoji=config["emoji"],
            entity_id=resource_data.get("id")
        )
    
    def organize_bookmarks_by_category(self, channel_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Organize channel bookmarks by category based on emoji"""
        bookmarks = self.list_bookmarks(channel_id)
        
        categories = {
            "📄": "Documents",
            "📊": "Dashboards",
            "📈": "Reports",
            "🔧": "Tools",
            "📚": "References",
            "🤖": "AI Resources",
            "👥": "Team",
            "⚡": "Shortcuts",
            "🔗": "Other"
        }
        
        organized = {category: [] for category in categories.values()}
        organized["Other"] = []
        
        for bookmark in bookmarks:
            emoji = bookmark.get("emoji", "🔗")
            category = categories.get(emoji, "Other")
            organized[category].append(bookmark)
        
        # Remove empty categories
        return {k: v for k, v in organized.items() if v}


def create_bookmarks_management_blocks(bookmarks: List[Dict[str, Any]], 
                                     channel_id: str) -> List[Dict[str, Any]]:
    """Create blocks for bookmark management interface"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📚 Channel Bookmarks"
            }
        }
    ]
    
    if not bookmarks:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No bookmarks found in this channel."
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Add Default Bookmarks"
                },
                "action_id": f"add_default_bookmarks_{channel_id}",
                "style": "primary"
            }
        })
        return blocks
    
    # Group bookmarks by emoji category
    categories = {}
    for bookmark in bookmarks:
        emoji = bookmark.get("emoji", "🔗")
        if emoji not in categories:
            categories[emoji] = []
        categories[emoji].append(bookmark)
    
    # Display bookmarks by category
    for emoji, category_bookmarks in categories.items():
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{len(category_bookmarks)} bookmark(s)*"
            }
        })
        
        for bookmark in category_bookmarks[:3]:  # Show max 3 per category
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{bookmark['link']}|{bookmark['title']}>"
                },
                "accessory": {
                    "type": "overflow",
                    "action_id": f"bookmark_menu_{bookmark['id']}",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Edit"
                            },
                            "value": f"edit_{bookmark['id']}"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Remove"
                            },
                            "value": f"remove_{bookmark['id']}"
                        }
                    ]
                }
            })
    
    blocks.append({
        "type": "divider"
    })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Add Bookmark"
                },
                "action_id": f"add_bookmark_{channel_id}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Organize"
                },
                "action_id": f"organize_bookmarks_{channel_id}"
            }
        ]
    })
    
    return blocks


def create_add_bookmark_modal(channel_id: str) -> Dict[str, Any]:
    """Create modal for adding a new bookmark"""
    return {
        "type": "modal",
        "callback_id": "add_bookmark_modal",
        "title": {
            "type": "plain_text",
            "text": "Add Bookmark"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "private_metadata": channel_id,
        "blocks": [
            {
                "type": "input",
                "block_id": "bookmark_title",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "title_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Bookmark title"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Title"
                }
            },
            {
                "type": "input",
                "block_id": "bookmark_url",
                "element": {
                    "type": "url_text_input",
                    "action_id": "url_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "https://example.com"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "URL"
                }
            },
            {
                "type": "input",
                "block_id": "bookmark_category",
                "element": {
                    "type": "static_select",
                    "action_id": "category_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select category"
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "📄 Document"},
                            "value": "📄"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📊 Dashboard"},
                            "value": "📊"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📈 Report"},
                            "value": "📈"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🔧 Tool"},
                            "value": "🔧"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📚 Reference"},
                            "value": "📚"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🔗 Other"},
                            "value": "🔗"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Category"
                }
            }
        ]
    }
}