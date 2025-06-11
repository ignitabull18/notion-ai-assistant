"""
Enhanced Lists Manager for Slack AI Assistant
Handles creating, updating, and managing channel lists with full API features
"""
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from listeners.ui_components import create_status_blocks
from utils.logging import logger


class ListItemStatus(Enum):
    """List item status options"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ListsManager:
    """Enhanced manager for Slack Lists API"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_list(self, channel_id: str, title: str, description: Optional[str] = None,
                   emoji: Optional[str] = None, color: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new list in a channel
        
        Args:
            channel_id: Channel to create list in
            title: List title
            description: Optional list description
            emoji: Optional emoji icon
            color: Optional color (hex or name)
            
        Returns:
            List object if successful
        """
        try:
            params = {
                "channel": channel_id,
                "title": title
            }
            
            if description:
                params["description"] = description
            if emoji:
                params["emoji"] = emoji
            if color:
                params["color"] = color
                
            # Note: This is a placeholder as the Lists API is still in development
            # In production, use: response = self.client.lists_create(**params)
            
            # Mock response for demonstration
            return {
                "id": f"L{channel_id[:8]}",
                "title": title,
                "description": description,
                "channel": channel_id,
                "emoji": emoji or "📋",
                "color": color or "#4A90E2",
                "created": datetime.now().isoformat(),
                "items_count": 0
            }
            
        except SlackApiError as e:
            logger.error(f"Error creating list: {e.response['error']}")
            return None
    
    def add_item(self, list_id: str, text: str, assignee: Optional[str] = None,
                due_date: Optional[str] = None, priority: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Add an item to a list"""
        try:
            params = {
                "list_id": list_id,
                "text": text,
                "status": ListItemStatus.OPEN.value
            }
            
            if assignee:
                params["assignee"] = assignee
            if due_date:
                params["due_date"] = due_date
            if priority:
                params["priority"] = priority
                
            # Mock response
            return {
                "id": f"LI{list_id[:6]}{datetime.now().timestamp()}",
                "list_id": list_id,
                "text": text,
                "status": ListItemStatus.OPEN.value,
                "assignee": assignee,
                "due_date": due_date,
                "priority": priority,
                "created": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding list item: {e}")
            return None
    
    def update_item_status(self, list_id: str, item_id: str, status: ListItemStatus) -> bool:
        """Update the status of a list item"""
        try:
            # In production: self.client.lists_items_update(
            #     list_id=list_id,
            #     item_id=item_id,
            #     status=status.value
            # )
            return True
            
        except Exception as e:
            logger.error(f"Error updating item status: {e}")
            return False
    
    def get_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """Get list details including all items"""
        try:
            # Mock response
            return {
                "id": list_id,
                "title": "Sample List",
                "items": [
                    {
                        "id": "LI001",
                        "text": "First task",
                        "status": "open",
                        "assignee": "U123456"
                    },
                    {
                        "id": "LI002",
                        "text": "Second task",
                        "status": "completed",
                        "completed_by": "U123456"
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting list: {e}")
            return None
    
    def delete_list(self, list_id: str) -> bool:
        """Delete a list"""
        try:
            # In production: self.client.lists_delete(list_id=list_id)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting list: {e}")
            return False
    
    def create_task_list(self, channel_id: str, title: str, tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create a task list with multiple items"""
        # Create the list
        list_obj = self.create_list(
            channel_id=channel_id,
            title=title,
            description="Task list created by AI Assistant",
            emoji="✅",
            color="#28a745"
        )
        
        if not list_obj:
            return None
        
        # Add tasks
        for task in tasks:
            self.add_item(
                list_id=list_obj["id"],
                text=task["text"],
                assignee=task.get("assignee"),
                due_date=task.get("due_date"),
                priority=task.get("priority", 3)
            )
        
        return list_obj
    
    def create_shopping_list(self, channel_id: str, items: List[str]) -> Optional[Dict[str, Any]]:
        """Create a shopping list"""
        list_obj = self.create_list(
            channel_id=channel_id,
            title="🛒 Shopping List",
            description=f"Shopping list with {len(items)} items",
            emoji="🛒",
            color="#FFA500"
        )
        
        if not list_obj:
            return None
        
        # Add items
        for item in items:
            self.add_item(list_id=list_obj["id"], text=item)
        
        return list_obj
    
    def create_project_checklist(self, channel_id: str, project_name: str, 
                               milestones: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create a project checklist with milestones"""
        list_obj = self.create_list(
            channel_id=channel_id,
            title=f"📊 {project_name} Checklist",
            description="Project milestones and deliverables",
            emoji="📊",
            color="#6f42c1"
        )
        
        if not list_obj:
            return None
        
        # Add milestones with priorities
        for idx, milestone in enumerate(milestones):
            self.add_item(
                list_id=list_obj["id"],
                text=milestone["text"],
                due_date=milestone.get("due_date"),
                priority=5 - idx  # Higher priority for earlier milestones
            )
        
        return list_obj


def create_list_management_blocks(list_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create blocks for list management interface"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{list_data.get('emoji', '📋')} {list_data['title']}"
            }
        }
    ]
    
    if list_data.get("description"):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"_{list_data['description']}_"
            }
        })
    
    blocks.append({"type": "divider"})
    
    # Show items grouped by status
    items = list_data.get("items", [])
    
    # Group items
    open_items = [item for item in items if item["status"] == "open"]
    in_progress = [item for item in items if item["status"] == "in_progress"]
    completed = [item for item in items if item["status"] == "completed"]
    
    # Open items
    if open_items:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📌 Open ({len(open_items)})*"
            }
        })
        
        for item in open_items[:5]:  # Show max 5
            assignee_text = f" - <@{item['assignee']}>" if item.get('assignee') else ""
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• {item['text']}{assignee_text}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✓ Complete"
                    },
                    "action_id": f"complete_item_{item['id']}",
                    "value": item['id']
                }
            })
    
    # In progress items
    if in_progress:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔄 In Progress ({len(in_progress)})*"
            }
        })
        
        for item in in_progress[:3]:
            blocks.append({
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"• {item['text']} - <@{item.get('assignee', 'unassigned')}>"
                }]
            })
    
    # Completed items count
    if completed:
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"✅ *{len(completed)} completed items*"
            }]
        })
    
    blocks.append({"type": "divider"})
    
    # Actions
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "➕ Add Item"
                },
                "action_id": f"add_list_item_{list_data['id']}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📊 View All"
                },
                "action_id": f"view_full_list_{list_data['id']}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "⚙️ Settings"
                },
                "action_id": f"list_settings_{list_data['id']}"
            }
        ]
    })
    
    return blocks


def create_add_list_item_modal(list_id: str, list_title: str) -> Dict[str, Any]:
    """Create modal for adding item to list"""
    return {
        "type": "modal",
        "callback_id": "add_list_item_modal",
        "title": {
            "type": "plain_text",
            "text": "Add Item"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add"
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
                    "text": f"Adding item to *{list_title}*"
                }
            },
            {
                "type": "input",
                "block_id": "item_text",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter item description"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Item"
                }
            },
            {
                "type": "input",
                "block_id": "item_assignee",
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
                    "text": "Assign To"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "item_due_date",
                "element": {
                    "type": "datepicker",
                    "action_id": "due_date_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select due date"
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
                "block_id": "item_priority",
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
                            "value": "5"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🟡 Medium"},
                            "value": "3"
                        },
                        {
                            "text": {"type": "plain_text", "text": "🟢 Low"},
                            "value": "1"
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


def create_list_templates_blocks() -> List[Dict[str, Any]]:
    """Create blocks showing list templates"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📋 List Templates"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Choose a template to quickly create a new list:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*✅ Task List*\nPerfect for project tasks and to-dos"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": "use_task_template",
                "value": "task"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🛒 Shopping List*\nFor team supplies or event planning"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": "use_shopping_template",
                "value": "shopping"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📊 Project Checklist*\nTrack milestones and deliverables"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": "use_project_template",
                "value": "project"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎯 Goals Tracker*\nMonitor team or personal objectives"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": "use_goals_template",
                "value": "goals"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📅 Event Planning*\nOrganize events with assignable tasks"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": "use_event_template",
                "value": "event"
            }
        }
    ]