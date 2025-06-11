"""
Link Unfurling for Notion AI Assistant
Provides rich previews for Notion pages and databases
"""
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from slack_bolt import App
from slack_sdk.web import WebClient

from utils.logging import logger


class NotionLinkUnfurler:
    """Handles link unfurling for Notion URLs"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def register_handlers(self, app: App):
        """Register link unfurling event handlers"""
        app.event("link_shared")(self.handle_link_shared)
    
    def handle_link_shared(self, event: Dict[str, Any], client: WebClient):
        """Handle link_shared events for Notion URLs"""
        try:
            unfurls = {}
            
            for link in event.get("links", []):
                url = link.get("url", "")
                
                # Check if it's a Notion URL
                if "notion.so" in url or "notion.site" in url:
                    unfurl = self._unfurl_notion_link(url)
                    if unfurl:
                        unfurls[url] = unfurl
            
            # Send unfurls if any were generated
            if unfurls:
                client.chat_unfurl(
                    channel=event["channel"],
                    ts=event["message_ts"],
                    unfurls=unfurls
                )
                
        except Exception as e:
            logger.error(f"Error unfurling Notion links: {e}")
    
    def _unfurl_notion_link(self, url: str) -> Optional[Dict[str, Any]]:
        """Create rich unfurl for Notion links"""
        # Determine if it's a page or database
        is_database = any(indicator in url for indicator in [
            "?v=", "collectionId", "database", "/db/"
        ])
        
        # Extract ID from URL
        notion_id = self._extract_notion_id(url)
        
        if is_database:
            return self._create_database_unfurl(url, notion_id)
        else:
            return self._create_page_unfurl(url, notion_id)
    
    def _extract_notion_id(self, url: str) -> Optional[str]:
        """Extract Notion ID from URL"""
        # Match various Notion URL formats
        patterns = [
            r'notion\.so/([a-f0-9]{32})',
            r'notion\.so/[^/]+/([a-f0-9]{32})',
            r'notion\.site/([a-f0-9]{32})',
            r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).replace('-', '')
        
        return None
    
    def _create_page_unfurl(self, url: str, notion_id: Optional[str]) -> Dict[str, Any]:
        """Create unfurl for Notion page"""
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*📄 Notion Page*\n"
                                "View and edit this page in Notion"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open in Notion"
                        },
                        "url": url,
                        "action_id": "open_notion_page"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📋 Get Page Info"
                            },
                            "action_id": f"get_page_info_{notion_id}",
                            "value": notion_id or url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "💬 Add Comment"
                            },
                            "action_id": f"add_page_comment_{notion_id}",
                            "value": notion_id or url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📑 Duplicate"
                            },
                            "action_id": f"duplicate_page_{notion_id}",
                            "value": notion_id or url
                        }
                    ]
                }
            ]
        }
    
    def _create_database_unfurl(self, url: str, notion_id: Optional[str]) -> Dict[str, Any]:
        """Create unfurl for Notion database"""
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🗄️ Notion Database*\n"
                                "Manage and query this database"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open Database"
                        },
                        "url": url,
                        "action_id": "open_notion_database"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 View Schema"
                            },
                            "action_id": f"view_db_schema_{notion_id}",
                            "value": notion_id or url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "➕ Add Entry"
                            },
                            "action_id": f"add_db_entry_{notion_id}",
                            "value": notion_id or url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔍 Query"
                            },
                            "action_id": f"query_database_{notion_id}",
                            "value": notion_id or url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📄 Create Canvas"
                            },
                            "action_id": f"create_db_canvas_{notion_id}",
                            "value": notion_id or url
                        }
                    ]
                }
            ]
        }


def register_notion_link_unfurling(app: App, client: WebClient):
    """Register Notion link unfurling handlers with the app"""
    unfurler = NotionLinkUnfurler(client)
    unfurler.register_handlers(app)