"""
UI Components for Notion AI Assistant
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


def create_notion_status_blocks(status: str, message: str) -> List[Dict[str, Any]]:
    """Create status indicator blocks"""
    emoji_map = {
        "processing": "⏳",
        "thinking": "🤔",
        "complete": "✅",
        "error": "❌",
        "working": "⚙️"
    }
    
    return [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{emoji_map.get(status, '📝')} *Status:* {message}"
                }
            ]
        }
    ]


def create_canvas_preview_blocks(canvas_url: str, title: str, description: str) -> List[Dict[str, Any]]:
    """Create blocks for canvas preview with link"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✨ *{title}*\n\n{description}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Open Canvas"
                    },
                    "url": canvas_url,
                    "style": "primary"
                }
            ]
        }
    ]


def create_page_creation_modal() -> Dict[str, Any]:
    """Create modal for Notion page creation"""
    return {
        "type": "modal",
        "callback_id": "create_page_modal",
        "title": {
            "type": "plain_text",
            "text": "Create Notion Page"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Page"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "title_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "page_title",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter page title"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Page Title"
                }
            },
            {
                "type": "input",
                "block_id": "parent_block",
                "element": {
                    "type": "static_select",
                    "action_id": "parent_type",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select parent location"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Workspace Root"
                            },
                            "value": "workspace"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Subpage"
                            },
                            "value": "subpage"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Database Entry"
                            },
                            "value": "database"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Parent Location"
                }
            },
            {
                "type": "input",
                "block_id": "content_block",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "page_content",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter initial page content (optional)"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Initial Content"
                }
            }
        ]
    }


def create_database_creation_modal() -> Dict[str, Any]:
    """Create modal for Notion database creation"""
    return {
        "type": "modal",
        "callback_id": "create_database_modal",
        "title": {
            "type": "plain_text",
            "text": "Create Notion Database"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Database"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "name_block",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "db_name",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter database name"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Database Name"
                }
            },
            {
                "type": "input",
                "block_id": "type_block",
                "element": {
                    "type": "static_select",
                    "action_id": "db_type",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select database type"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Task Management"
                            },
                            "value": "tasks"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Project Tracking"
                            },
                            "value": "projects"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Contact Management"
                            },
                            "value": "contacts"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Content Calendar"
                            },
                            "value": "content"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Custom"
                            },
                            "value": "custom"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Database Type"
                }
            },
            {
                "type": "input",
                "block_id": "properties_block",
                "optional": True,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "db_properties",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., Status (select), Due Date (date), Assignee (person)"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Properties (optional)"
                }
            }
        ]
    }


def create_welcome_blocks() -> List[Dict[str, Any]]:
    """Create welcome interface blocks for Notion AI Assistant"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 Welcome to Notion AI Assistant"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*I'm here to help you manage and optimize your Notion workspace!*\n\nI can assist with:\n• 📄 Creating and updating pages\n• 🗄️ Managing databases and properties\n• 🔍 Searching your workspace\n• 📊 Generating reports and summaries\n• 🏗️ Building workspace templates"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🚀 Quick Actions*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📄 Create Page"
                    },
                    "action_id": "open_page_modal",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🗄️ Create Database"
                    },
                    "action_id": "open_database_modal"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Workspace Summary"
                    },
                    "action_id": "create_workspace_canvas"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 Project Template"
                    },
                    "action_id": "create_project_template",
                    "value": "general"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔄 Workflows"
                    },
                    "action_id": "show_workflows"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 *Tip:* You can also use natural language to ask me anything about your Notion workspace!"
                }
            ]
        }
    ]


def create_database_list_blocks(databases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for displaying a list of databases with actions"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🗄️ Your Notion Databases"
            }
        }
    ]
    
    for db in databases[:10]:  # Limit to 10 for UI performance
        db_id = db.get('id', '')
        db_name = db.get('title', 'Untitled Database')
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{db_name}*\n`{db_id}`\n_{db.get('description', 'No description')}_"
            },
            "accessory": {
                "type": "overflow",
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "🔍 View Details"
                        },
                        "value": f"view|{db_id}"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "📊 Schema Canvas"
                        },
                        "value": f"schema|{db_id}|{db_name}"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "➕ Add Entry"
                        },
                        "value": f"add|{db_id}"
                    }
                ],
                "action_id": f"db_action_{db_id[:8]}"
            }
        })
    
    if len(databases) > 10:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_Showing 10 of {len(databases)} databases_"
                }
            ]
        })
    
    return blocks


def create_workflow_blocks(workflow_name: str, steps: List[str]) -> List[Dict[str, Any]]:
    """Create blocks for workflow visualization"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔄 Workflow: {workflow_name}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Steps:*"
            }
        }
    ]
    
    for i, step in enumerate(steps, 1):
        emoji = "✅" if i == 1 else "⏳"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *Step {i}:* {step}"
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📄 Document Workflow"
                },
                "action_id": "create_workflow_canvas",
                "value": workflow_name
            }
        ]
    })
    
    return blocks


def create_search_results_blocks(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Create blocks for Notion search results"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔍 Search Results for: {query}"
            }
        }
    ]
    
    if not results:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "_No results found. Try a different search term._"
            }
        })
        return blocks
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
                "text": f"Found *{len(results)}* results"
        }
    })
    
    for result in results[:5]:  # Show top 5 results
        result_type = result.get('type', 'page')
        emoji = "📄" if result_type == 'page' else "🗄️"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{result.get('title', 'Untitled')}*\n_{result.get('path', 'Unknown location')}_"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Open"
                },
                "action_id": f"open_{result.get('id', '')[:20]}",
                "value": result.get('id', '')
            }
        })
    
    return blocks


def create_workflow_template_blocks(templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for workflow template selection"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔄 Notion Workflow Templates"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select a workflow template to automate your Notion workspace:"
            }
        }
    ]
    
    for template in templates:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{template['name']}*\n_{template['description']}_\n📋 {template['steps']} steps"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": f"use_workflow_{template['id']}",
                "value": template['id'],
                "style": "primary"
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🛠️ Create Custom Workflow"
                },
                "action_id": "create_custom_workflow"
            }
        ]
    })
    
    return blocks


def create_workflow_status_blocks(workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create blocks showing workflow execution status"""
    status_emoji = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫"
    }
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{status_emoji.get(workflow['status'], '📋')} {workflow['name']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Status:* {workflow['status'].title()}\n*Progress:* Step {workflow['current_step'] + 1} of {workflow['total_steps']}"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add step details
    for step in workflow['steps']:
        step_emoji = status_emoji.get(step['status'], '○')
        text = f"{step_emoji} *{step['name']}*"
        
        if step['status'] == 'failed' and step.get('error'):
            text += f"\n   ❗ Error: _{step['error']}_"
        elif step['status'] == 'completed':
            text += "\n   ✓ Completed successfully"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        })
    
    # Add actions based on status
    if workflow['status'] == 'running':
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "⏸️ Pause"
                    },
                    "action_id": f"pause_workflow_{workflow['workflow_id']}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🚫 Cancel"
                    },
                    "action_id": f"cancel_workflow_{workflow['workflow_id']}",
                    "style": "danger"
                }
            ]
        })
    elif workflow['status'] == 'completed':
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📄 View Results"
                    },
                    "action_id": f"view_results_{workflow['workflow_id']}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔄 Run Again"
                    },
                    "action_id": f"rerun_workflow_{workflow['workflow_id']}"
                }
            ]
        })
    
    return blocks


def create_workflow_builder_modal() -> Dict[str, Any]:
    """Create modal for building custom workflows"""
    return {
        "type": "modal",
        "callback_id": "workflow_builder_modal",
        "title": {
            "type": "plain_text",
            "text": "Build Custom Workflow"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Workflow"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "workflow_name",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "name",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Enter workflow name"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Workflow Name"
                }
            },
            {
                "type": "input",
                "block_id": "workflow_description",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "description",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Describe what this workflow does"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Description"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Add Workflow Steps*\nDefine the steps in your workflow:"
                }
            },
            {
                "type": "input",
                "block_id": "step_1",
                "element": {
                    "type": "static_select",
                    "action_id": "step_action",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select first action"
                    },
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "Create Page"},
                            "value": "create_page"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Query Database"},
                            "value": "query_database"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Update Properties"},
                            "value": "update_properties"
                        },
                        {
                            "text": {"type": "plain_text", "text": "Archive Items"},
                            "value": "archive_items"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Step 1"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "+ Add Step"
                        },
                        "action_id": "add_workflow_step"
                    }
                ]
            }
        ]
    }