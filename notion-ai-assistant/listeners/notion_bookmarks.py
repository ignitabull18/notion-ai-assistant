"""
Notion-specific Bookmarks Manager
Handles bookmarks for Notion pages, databases, and resources
"""
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List, Optional
import re

from utils.logging import logger


class NotionBookmarksManager:
    """Manages Notion-related bookmarks in Slack channels"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def add_notion_bookmark(self, channel_id: str, notion_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a Notion page or database as a bookmark
        
        Args:
            channel_id: The channel to add bookmark to
            notion_data: Dict containing notion page/database info
                - url: Notion URL
                - title: Page/Database title
                - type: 'page' or 'database'
                - id: Notion ID
                
        Returns:
            Bookmark object if successful
        """
        try:
            # Determine emoji based on type
            emoji_map = {
                "page": "📄",
                "database": "🗄️",
                "workspace": "🏢",
                "template": "📋",
                "wiki": "📚"
            }
            
            notion_type = notion_data.get("type", "page")
            emoji = emoji_map.get(notion_type, "📝")
            
            response = self.client.bookmarks_add(
                channel_id=channel_id,
                title=notion_data["title"],
                type="link",
                link=notion_data["url"],
                emoji=emoji,
                entity_id=f"notion_{notion_data.get('id', '')}"
            )
            
            return response.get("bookmark")
            
        except SlackApiError as e:
            logger.error(f"Error adding Notion bookmark: {e.response['error']}")
            return None
    
    def sync_notion_workspace_bookmarks(self, channel_id: str, 
                                      workspace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sync important Notion pages/databases as bookmarks"""
        created_bookmarks = []
        
        # Add workspace home
        if workspace_data.get("workspace_url"):
            workspace_bookmark = self.add_notion_bookmark(
                channel_id=channel_id,
                notion_data={
                    "url": workspace_data["workspace_url"],
                    "title": f"{workspace_data.get('name', 'Notion')} Workspace",
                    "type": "workspace",
                    "id": "workspace_home"
                }
            )
            if workspace_bookmark:
                created_bookmarks.append(workspace_bookmark)
        
        # Add important databases
        for db in workspace_data.get("databases", [])[:5]:  # Limit to 5
            db_bookmark = self.add_notion_bookmark(
                channel_id=channel_id,
                notion_data={
                    "url": db["url"],
                    "title": db["title"],
                    "type": "database",
                    "id": db["id"]
                }
            )
            if db_bookmark:
                created_bookmarks.append(db_bookmark)
        
        # Add frequently accessed pages
        for page in workspace_data.get("frequent_pages", [])[:5]:  # Limit to 5
            page_bookmark = self.add_notion_bookmark(
                channel_id=channel_id,
                notion_data={
                    "url": page["url"],
                    "title": page["title"],
                    "type": "page",
                    "id": page["id"]
                }
            )
            if page_bookmark:
                created_bookmarks.append(page_bookmark)
        
        return created_bookmarks
    
    def create_notion_template_bookmarks(self, channel_id: str) -> List[Dict[str, Any]]:
        """Create bookmarks for common Notion templates"""
        templates = [
            {
                "title": "Meeting Notes Template",
                "url": "https://www.notion.so/templates/meeting-notes",
                "type": "template",
                "id": "meeting_notes_template"
            },
            {
                "title": "Project Tracker",
                "url": "https://www.notion.so/templates/project-tracker",
                "type": "template",
                "id": "project_tracker_template"
            },
            {
                "title": "Task Database",
                "url": "https://www.notion.so/templates/task-database",
                "type": "template",
                "id": "task_db_template"
            },
            {
                "title": "Knowledge Base",
                "url": "https://www.notion.so/templates/knowledge-base",
                "type": "template",
                "id": "kb_template"
            },
            {
                "title": "Team Wiki",
                "url": "https://www.notion.so/templates/team-wiki",
                "type": "template",
                "id": "wiki_template"
            }
        ]
        
        created_bookmarks = []
        for template in templates:
            bookmark = self.add_notion_bookmark(channel_id, template)
            if bookmark:
                created_bookmarks.append(bookmark)
        
        return created_bookmarks
    
    def extract_notion_id_from_url(self, url: str) -> Optional[str]:
        """Extract Notion page/database ID from URL"""
        # Notion URLs typically end with a 32-character hex ID
        pattern = r'([a-f0-9]{32})'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def get_notion_bookmarks(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get all Notion-related bookmarks from a channel"""
        try:
            response = self.client.bookmarks_list(channel_id=channel_id)
            all_bookmarks = response.get("bookmarks", [])
            
            # Filter Notion bookmarks
            notion_bookmarks = []
            for bookmark in all_bookmarks:
                # Check if it's a Notion bookmark by entity_id or URL
                if (bookmark.get("entity_id", "").startswith("notion_") or
                    "notion.so" in bookmark.get("link", "") or
                    bookmark.get("emoji") in ["📄", "🗄️", "📋", "📚", "🏢"]):
                    notion_bookmarks.append(bookmark)
            
            return notion_bookmarks
            
        except SlackApiError as e:
            logger.error(f"Error getting Notion bookmarks: {e.response['error']}")
            return []
    
    def organize_notion_bookmarks(self, channel_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Organize Notion bookmarks by type"""
        bookmarks = self.get_notion_bookmarks(channel_id)
        
        organized = {
            "Pages": [],
            "Databases": [],
            "Templates": [],
            "Workspace": [],
            "Other": []
        }
        
        emoji_to_type = {
            "📄": "Pages",
            "🗄️": "Databases",
            "📋": "Templates",
            "🏢": "Workspace",
            "📚": "Other"
        }
        
        for bookmark in bookmarks:
            emoji = bookmark.get("emoji", "📝")
            category = emoji_to_type.get(emoji, "Other")
            organized[category].append(bookmark)
        
        # Remove empty categories
        return {k: v for k, v in organized.items() if v}


def create_notion_bookmarks_blocks(bookmarks: List[Dict[str, Any]], 
                                 channel_id: str) -> List[Dict[str, Any]]:
    """Create blocks for Notion bookmarks interface"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📚 Notion Bookmarks"
            }
        }
    ]
    
    if not bookmarks:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No Notion bookmarks found in this channel."
            }
        })
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add Templates"
                    },
                    "action_id": f"add_notion_templates_{channel_id}",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Sync Workspace"
                    },
                    "action_id": f"sync_notion_workspace_{channel_id}"
                }
            ]
        })
        return blocks
    
    # Organize by type
    manager = NotionBookmarksManager(None)  # Just for organization
    organized = {}
    
    emoji_to_type = {
        "📄": "Pages",
        "🗄️": "Databases",
        "📋": "Templates",
        "🏢": "Workspace",
        "📚": "Other"
    }
    
    for bookmark in bookmarks:
        emoji = bookmark.get("emoji", "📝")
        category = emoji_to_type.get(emoji, "Other")
        if category not in organized:
            organized[category] = []
        organized[category].append(bookmark)
    
    # Display by category
    for category, items in organized.items():
        if not items:
            continue
            
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{category}* ({len(items)})"
            }
        })
        
        for bookmark in items[:3]:  # Show max 3 per category
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{bookmark.get('emoji', '📝')} <{bookmark['link']}|{bookmark['title']}>"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Open"
                    },
                    "url": bookmark['link']
                }
            })
    
    blocks.append({"type": "divider"})
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Add Page/Database"
                },
                "action_id": f"add_notion_bookmark_{channel_id}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Sync Workspace"
                },
                "action_id": f"sync_notion_workspace_{channel_id}"
            }
        ]
    })
    
    return blocks


def create_add_notion_bookmark_modal(channel_id: str) -> Dict[str, Any]:
    """Create modal for adding a Notion bookmark"""
    return {
        "type": "modal",
        "callback_id": "add_notion_bookmark_modal",
        "title": {
            "type": "plain_text",
            "text": "Add Notion Bookmark"
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
                "block_id": "notion_url",
                "element": {
                    "type": "url_text_input",
                    "action_id": "url_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "https://notion.so/..."
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Notion URL"
                }
            },
            {
                "type": "input",
                "block_id": "bookmark_title",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "title_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Page or Database name"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Title"
                }
            },
            {
                "type": "input",
                "block_id": "notion_type",
                "element": {
                    "type": "static_select",
                    "action_id": "type_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select type"
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "📄 Page"},
                            "value": "page"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🗄️ Database"},
                            "value": "database"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📋 Template"},
                            "value": "template"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📚 Wiki"},
                            "value": "wiki"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Type"
                }
            }
        ]
    }
}