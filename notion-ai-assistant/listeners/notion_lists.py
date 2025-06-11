"""
Notion-integrated Lists Manager
Syncs Slack lists with Notion databases for enhanced task management
"""
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio

from listeners.agno_integration import process_with_agent
from listeners.ui_components import create_notion_status_blocks
from utils.logging import logger


class NotionListsManager:
    """Manages lists that sync with Notion databases"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_notion_synced_list(self, channel_id: str, notion_db_id: str, 
                                 title: str, sync_options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a Slack list that syncs with a Notion database
        
        Args:
            channel_id: Slack channel ID
            notion_db_id: Notion database ID to sync with
            title: List title
            sync_options: Sync configuration (fields mapping, update frequency)
            
        Returns:
            List object if successful
        """
        try:
            # Create list in Slack (mock for now)
            list_data = {
                "id": f"L{channel_id[:8]}",
                "title": title,
                "channel": channel_id,
                "notion_db_id": notion_db_id,
                "sync_enabled": True,
                "sync_options": sync_options,
                "emoji": "🔄",
                "color": "#7C3AED",  # Notion purple
                "created": datetime.now().isoformat()
            }
            
            # Store sync configuration
            self._store_sync_config(list_data["id"], notion_db_id, sync_options)
            
            return list_data
            
        except Exception as e:
            logger.error(f"Error creating Notion-synced list: {e}")
            return None
    
    def sync_from_notion(self, list_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Sync list items from Notion database"""
        try:
            # Get sync configuration
            sync_config = self._get_sync_config(list_id)
            if not sync_config:
                return []
            
            # Query Notion database through agent
            notion_items = asyncio.run(
                process_with_agent(
                    user_id=user_id,
                    message=f"Get all items from Notion database {sync_config['notion_db_id']} with their status, assignee, and due dates"
                )
            )
            
            # Parse and convert to list items (simplified)
            items = []
            # In production, parse the agent response properly
            mock_items = [
                {
                    "text": "Review Q4 goals",
                    "status": "in_progress",
                    "assignee": "U123456",
                    "due_date": "2024-12-31"
                },
                {
                    "text": "Update team wiki",
                    "status": "open",
                    "due_date": "2024-12-15"
                }
            ]
            
            for item_data in mock_items:
                items.append({
                    "id": f"LI{datetime.now().timestamp()}",
                    "text": item_data["text"],
                    "status": item_data.get("status", "open"),
                    "assignee": item_data.get("assignee"),
                    "due_date": item_data.get("due_date"),
                    "notion_id": item_data.get("notion_id")
                })
            
            return items
            
        except Exception as e:
            logger.error(f"Error syncing from Notion: {e}")
            return []
    
    def sync_to_notion(self, list_id: str, item_updates: List[Dict[str, Any]], user_id: str) -> bool:
        """Sync list updates back to Notion"""
        try:
            sync_config = self._get_sync_config(list_id)
            if not sync_config:
                return False
            
            # Update Notion through agent
            for update in item_updates:
                if update.get("notion_id"):
                    asyncio.run(
                        process_with_agent(
                            user_id=user_id,
                            message=f"Update Notion page {update['notion_id']} with status: {update['status']}"
                        )
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error syncing to Notion: {e}")
            return False
    
    def create_notion_task_list(self, channel_id: str, user_id: str, 
                              project_name: str) -> Optional[Dict[str, Any]]:
        """Create a task list from a Notion project"""
        try:
            # Create Notion database for tasks
            db_creation = asyncio.run(
                process_with_agent(
                    user_id=user_id,
                    message=f"Create a new Notion database called '{project_name} Tasks' with properties: Status (select), Assignee (person), Due Date (date), Priority (select)"
                )
            )
            
            # Mock database ID (in production, parse from agent response)
            notion_db_id = "mock-db-id-123"
            
            # Create synced list
            list_obj = self.create_notion_synced_list(
                channel_id=channel_id,
                notion_db_id=notion_db_id,
                title=f"📋 {project_name} Tasks",
                sync_options={
                    "sync_frequency": "realtime",
                    "field_mapping": {
                        "status": "Status",
                        "assignee": "Assignee",
                        "due_date": "Due Date",
                        "priority": "Priority"
                    }
                }
            )
            
            return list_obj
            
        except Exception as e:
            logger.error(f"Error creating Notion task list: {e}")
            return None
    
    def create_content_calendar_list(self, channel_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a content calendar list synced with Notion"""
        try:
            # Create content calendar in Notion
            calendar_creation = asyncio.run(
                process_with_agent(
                    user_id=user_id,
                    message="Create a Notion database for content calendar with properties: Title, Status, Author, Publish Date, Content Type, and Tags"
                )
            )
            
            # Create synced list
            list_obj = self.create_notion_synced_list(
                channel_id=channel_id,
                notion_db_id="content-calendar-db",
                title="📅 Content Calendar",
                sync_options={
                    "sync_frequency": "hourly",
                    "field_mapping": {
                        "title": "Title",
                        "status": "Status",
                        "assignee": "Author",
                        "due_date": "Publish Date"
                    },
                    "filters": {
                        "status": ["Draft", "In Review", "Scheduled"]
                    }
                }
            )
            
            return list_obj
            
        except Exception as e:
            logger.error(f"Error creating content calendar: {e}")
            return None
    
    def _store_sync_config(self, list_id: str, notion_db_id: str, sync_options: Dict[str, Any]):
        """Store sync configuration (in production, use a database)"""
        # Mock storage
        pass
    
    def _get_sync_config(self, list_id: str) -> Optional[Dict[str, Any]]:
        """Get sync configuration for a list"""
        # Mock retrieval
        return {
            "notion_db_id": "mock-db-id",
            "sync_options": {}
        }


def create_notion_list_blocks(list_data: Dict[str, Any], items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for Notion-synced list display"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔄 {list_data['title']}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📊 Synced with Notion • Last updated: <t:{int(datetime.now().timestamp())}:R>"
                }
            ]
        },
        {"type": "divider"}
    ]
    
    # Group items by status
    todo_items = [i for i in items if i["status"] in ["open", "todo"]]
    in_progress = [i for i in items if i["status"] == "in_progress"]
    done_items = [i for i in items if i["status"] in ["completed", "done"]]
    
    # To Do section
    if todo_items:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📌 To Do ({len(todo_items)})*"
            }
        })
        
        for item in todo_items[:5]:
            due_text = f" • Due: {item['due_date']}" if item.get('due_date') else ""
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• {item['text']}{due_text}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Start"
                    },
                    "action_id": f"start_notion_item_{item['id']}",
                    "value": item['id']
                }
            })
    
    # In Progress section
    if in_progress:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔄 In Progress ({len(in_progress)})*"
            }
        })
        
        for item in in_progress[:3]:
            assignee = f" • <@{item['assignee']}>" if item.get('assignee') else ""
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• {item['text']}{assignee}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Complete"
                    },
                    "action_id": f"complete_notion_item_{item['id']}",
                    "value": item['id'],
                    "style": "primary"
                }
            })
    
    # Summary
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"✅ {len(done_items)} completed • 📊 {len(items)} total items"
            }
        ]
    })
    
    # Actions
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🔄 Sync Now"
                },
                "action_id": f"sync_notion_list_{list_data['id']}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📝 Open in Notion"
                },
                "action_id": f"open_notion_db_{list_data['notion_db_id']}",
                "url": f"https://notion.so/{list_data['notion_db_id']}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "➕ Add Task"
                },
                "action_id": f"add_notion_task_{list_data['id']}"
            }
        ]
    })
    
    return blocks


def create_notion_list_templates_blocks() -> List[Dict[str, Any]]:
    """Create blocks for Notion list templates"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📋 Notion List Templates"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Create lists that automatically sync with your Notion workspace:"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📋 Project Tasks*\nSync tasks with status, assignees, and deadlines"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_notion_task_list",
                "style": "primary"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📅 Content Calendar*\nManage content pipeline with publish dates"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_content_calendar"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎯 OKRs Tracker*\nTrack objectives and key results"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_okr_tracker"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🐛 Bug Tracker*\nSync with Notion bug database"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_bug_tracker"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📚 Reading List*\nTrack books, articles, and resources"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_reading_list"
            }
        }
    ]


def create_add_notion_task_modal(list_id: str, list_title: str) -> Dict[str, Any]:
    """Create modal for adding task that syncs to Notion"""
    return {
        "type": "modal",
        "callback_id": "add_notion_task_modal",
        "title": {
            "type": "plain_text",
            "text": "Add Notion Task"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Task"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "private_metadata": list_id,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Adding task to *{list_title}*\nThis will create a new page in your Notion database."
                }
            },
            {
                "type": "input",
                "block_id": "task_title",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "title_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Task title"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Title"
                }
            },
            {
                "type": "input",
                "block_id": "task_description",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "description_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Add more details..."
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Description"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "task_status",
                "element": {
                    "type": "static_select",
                    "action_id": "status_input",
                    "initial_option": {
                        "text": {"type": "plain_text", "text": "To Do"},
                        "value": "todo"
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "To Do"},
                            "value": "todo"
                        },
                        {
                            "text": {"type": "plain_text", "text": "In Progress"},
                            "value": "in_progress"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Review"},
                            "value": "review"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Status"
                }
            },
            {
                "type": "input",
                "block_id": "task_assignee",
                "element": {
                    "type": "users_select",
                    "action_id": "assignee_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select assignee"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Assignee"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "task_due_date",
                "element": {
                    "type": "datepicker",
                    "action_id": "due_date_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select date"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Due Date"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "task_priority",
                "element": {
                    "type": "static_select",
                    "action_id": "priority_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select priority"
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "🔴 High"},
                            "value": "high"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🟡 Medium"},
                            "value": "medium"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🟢 Low"},
                            "value": "low"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Priority"
                },
                "optional": True
            }
        ]
    }
}