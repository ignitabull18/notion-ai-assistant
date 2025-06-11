"""
Link Unfurling for Slack AI Assistant
Provides rich previews for shared links
"""
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from slack_bolt import App, Ack
from slack_sdk.web import WebClient

from utils.logging import logger


class LinkUnfurler:
    """Handles link unfurling for various URL types"""
    
    def __init__(self, client: WebClient):
        self.client = client
        self.unfurlers = {
            'github.com': self._unfurl_github,
            'docs.google.com': self._unfurl_google_docs,
            'youtube.com': self._unfurl_youtube,
            'youtu.be': self._unfurl_youtube,
            'slack.com': self._unfurl_slack_message,
            'wikipedia.org': self._unfurl_wikipedia,
            'stackoverflow.com': self._unfurl_stackoverflow
        }
    
    def register_handlers(self, app: App):
        """Register link unfurling event handlers"""
        app.event("link_shared")(self.handle_link_shared)
    
    def handle_link_shared(self, event: Dict[str, Any], client: WebClient):
        """Handle link_shared events"""
        try:
            unfurls = {}
            
            for link in event.get("links", []):
                url = link.get("url", "")
                domain = urlparse(url).netloc.lower()
                
                # Remove www. prefix
                if domain.startswith('www.'):
                    domain = domain[4:]
                
                # Find appropriate unfurler
                for pattern, unfurler in self.unfurlers.items():
                    if pattern in domain:
                        unfurl = unfurler(url)
                        if unfurl:
                            unfurls[url] = unfurl
                        break
            
            # Send unfurls if any were generated
            if unfurls:
                client.chat_unfurl(
                    channel=event["channel"],
                    ts=event["message_ts"],
                    unfurls=unfurls
                )
                
        except Exception as e:
            logger.error(f"Error unfurling links: {e}")
    
    def _unfurl_github(self, url: str) -> Optional[Dict[str, Any]]:
        """Unfurl GitHub links"""
        # Extract repo info from URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
        if not match:
            return None
        
        owner, repo = match.groups()
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*GitHub Repository: {owner}/{repo}*\n"
                                f"View code, issues, and pull requests"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open in GitHub"
                        },
                        "url": url,
                        "action_id": "open_github"
                    }
                }
            ]
        }
    
    def _unfurl_google_docs(self, url: str) -> Optional[Dict[str, Any]]:
        """Unfurl Google Docs links"""
        doc_type = "Document"
        if "spreadsheets" in url:
            doc_type = "Spreadsheet"
        elif "presentation" in url:
            doc_type = "Presentation"
        elif "forms" in url:
            doc_type = "Form"
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Google {doc_type}*\n"
                                f"Collaborate on this {doc_type.lower()} in Google Workspace"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f"Open {doc_type}"
                        },
                        "url": url,
                        "action_id": "open_google_doc"
                    }
                }
            ]
        }
    
    def _unfurl_youtube(self, url: str) -> Optional[Dict[str, Any]]:
        """Unfurl YouTube links"""
        # Extract video ID
        video_id = None
        if "youtube.com/watch" in url:
            match = re.search(r'v=([^&]+)', url)
            if match:
                video_id = match.group(1)
        elif "youtu.be" in url:
            match = re.search(r'youtu\.be/([^?]+)', url)
            if match:
                video_id = match.group(1)
        
        if not video_id:
            return None
        
        return {
            "blocks": [
                {
                    "type": "video",
                    "title": {
                        "type": "plain_text",
                        "text": "YouTube Video"
                    },
                    "title_url": url,
                    "description": {
                        "type": "plain_text",
                        "text": "Click to watch on YouTube"
                    },
                    "video_url": url,
                    "alt_text": "YouTube video",
                    "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                    "author_name": "YouTube"
                }
            ]
        }
    
    def _unfurl_slack_message(self, url: str) -> Optional[Dict[str, Any]]:
        """Unfurl Slack message links"""
        # Extract workspace and message info
        match = re.search(r'slack\.com/archives/([^/]+)/p(\d+)', url)
        if not match:
            return None
        
        channel_id, ts = match.groups()
        # Convert timestamp format
        ts = f"{ts[:10]}.{ts[10:]}"
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Slack Message*\n"
                                "Jump to this conversation"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Message"
                        },
                        "url": url,
                        "action_id": "view_slack_message"
                    }
                }
            ]
        }
    
    def _unfurl_wikipedia(self, url: str) -> Optional[Dict[str, Any]]:
        """Unfurl Wikipedia links"""
        # Extract article title
        match = re.search(r'wikipedia\.org/wiki/([^?#]+)', url)
        if not match:
            return None
        
        article = match.group(1).replace('_', ' ')
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Wikipedia: {article}*\n"
                                f"Learn more about this topic on Wikipedia"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Read Article"
                        },
                        "url": url,
                        "action_id": "open_wikipedia"
                    }
                }
            ]
        }
    
    def _unfurl_stackoverflow(self, url: str) -> Optional[Dict[str, Any]]:
        """Unfurl Stack Overflow links"""
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Stack Overflow*\n"
                                "Technical Q&A and solutions"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Answer"
                        },
                        "url": url,
                        "action_id": "open_stackoverflow"
                    }
                }
            ]
        }


def register_link_unfurling(app: App, client: WebClient):
    """Register link unfurling handlers with the app"""
    unfurler = LinkUnfurler(client)
    unfurler.register_handlers(app)