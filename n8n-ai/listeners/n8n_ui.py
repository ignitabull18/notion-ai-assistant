"""
N8N UI Components - Rich Slack Block Kit interfaces
"""
from typing import Dict, Any, List, Optional


def create_welcome_blocks() -> List[Dict[str, Any]]:
    """Create welcome message blocks"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔧 N8N Workflow Assistant"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Welcome! I'm your N8N workflow automation expert. I can help you:"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "🏗️ *Build Workflows*\nFrom descriptions or screenshots"
                },
                {
                    "type": "mrkdwn",
                    "text": "📥 *Import/Export*\nJSON workflow files"
                },
                {
                    "type": "mrkdwn",
                    "text": "▶️ *Execute*\nRun and monitor workflows"
                },
                {
                    "type": "mrkdwn",
                    "text": "🔍 *Analyze*\nOptimize and document"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Quick Actions:*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 My Workflows"
                    },
                    "action_id": "list_workflows",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "➕ Create Workflow"
                    },
                    "action_id": "create_workflow"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📤 Import JSON"
                    },
                    "action_id": "import_workflow"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🎯 Templates"
                    },
                    "action_id": "show_templates"
                }
            ]
        }
    ]


def create_workflow_blocks(workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create blocks for displaying a workflow"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📋 {workflow.get('name', 'Workflow')}"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*ID:* `{workflow.get('id', 'N/A')}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:* {'🟢 Active' if workflow.get('active') else '🔴 Inactive'}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Nodes:* {len(workflow.get('nodes', []))}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Created:* {workflow.get('createdAt', 'Unknown')[:10]}"
                }
            ]
        }
    ]
    
    # Add node information
    nodes = workflow.get('nodes', [])
    if nodes:
        node_list = []
        for node in nodes[:5]:  # Show first 5 nodes
            node_list.append(f"• {node.get('name', 'Unnamed')} ({node.get('type', 'Unknown')})")
        
        if len(nodes) > 5:
            node_list.append(f"• ... and {len(nodes) - 5} more nodes")
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Nodes:*\n" + "\n".join(node_list)
            }
        })
    
    # Add actions
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "▶️ Execute"
                },
                "action_id": f"execute_workflow_{workflow.get('id')}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "✏️ Edit"
                },
                "action_id": f"edit_workflow_{workflow.get('id')}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📥 Export"
                },
                "action_id": f"export_workflow_{workflow.get('id')}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Stats"
                },
                "action_id": f"workflow_stats_{workflow.get('id')}"
            }
        ]
    })
    
    return blocks


def create_workflow_list_blocks(workflows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for listing workflows"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📋 Your Workflows"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Found {len(workflows)} workflow(s)*"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    if not workflows:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "_No workflows found. Create your first workflow!_"
            }
        })
        return blocks
    
    # Add each workflow
    for workflow in workflows[:10]:  # Limit to 10 to avoid block limit
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{workflow.get('name', 'Unnamed')}*\n"
                       f"ID: `{workflow.get('id')}` | "
                       f"Status: {'🟢 Active' if workflow.get('active') else '🔴 Inactive'} | "
                       f"Nodes: {len(workflow.get('nodes', []))}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View"
                },
                "action_id": f"view_workflow_{workflow.get('id')}"
            }
        })
    
    if len(workflows) > 10:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"_... and {len(workflows) - 10} more workflows_"
            }
        })
    
    return blocks


def create_execution_blocks(execution: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create blocks for workflow execution result"""
    status = execution.get('status', 'unknown')
    status_emoji = {
        'success': '✅',
        'error': '❌',
        'running': '🔄',
        'waiting': '⏳'
    }.get(status, '❓')
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{status_emoji} Workflow Execution"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Execution ID:* `{execution.get('id', 'N/A')}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Status:* {status.title()}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Workflow:* {execution.get('workflowName', 'Unknown')}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Started:* {execution.get('startedAt', 'Unknown')[:19]}"
                }
            ]
        }
    ]
    
    # Add error info if failed
    if status == 'error' and execution.get('error'):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Error:*\n```{execution['error']}```"
            }
        })
    
    # Add execution time if completed
    if execution.get('stoppedAt'):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Completed:* {execution['stoppedAt'][:19]}"
            }
        })
    
    return blocks


def create_workflow_canvas_blocks(canvas_url: str, title: str, description: str) -> Dict[str, Any]:
    """Create blocks for workflow canvas preview"""
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📄 *Canvas Created: {title}*\n{description}"
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
    }


def create_import_modal() -> Dict[str, Any]:
    """Create modal for importing workflow JSON"""
    return {
        "type": "modal",
        "callback_id": "import_workflow_modal",
        "title": {
            "type": "plain_text",
            "text": "Import Workflow"
        },
        "submit": {
            "type": "plain_text",
            "text": "Import"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Paste your N8N workflow JSON below:"
                }
            },
            {
                "type": "input",
                "block_id": "workflow_json",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "workflow_json_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": '{"name": "My Workflow", "nodes": [...], "connections": {...}}'
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Workflow JSON"
                }
            },
            {
                "type": "input",
                "block_id": "workflow_name",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "workflow_name_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "My Imported Workflow"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Workflow Name (optional)"
                },
                "optional": True
            }
        ]
    }


def create_workflow_builder_modal() -> Dict[str, Any]:
    """Create modal for building a workflow"""
    return {
        "type": "modal",
        "callback_id": "build_workflow_modal",
        "title": {
            "type": "plain_text",
            "text": "Build Workflow"
        },
        "submit": {
            "type": "plain_text",
            "text": "Build"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Describe what you want your workflow to do:"
                }
            },
            {
                "type": "input",
                "block_id": "workflow_description",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "description_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "When a Slack message is posted, send an email notification and create a task in Trello..."
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Workflow Description"
                }
            },
            {
                "type": "input",
                "block_id": "workflow_name",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "name_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Slack to Email & Trello"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Workflow Name"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Suggested integrations:*\nSlack, Email, Trello, Google Sheets, Webhook, HTTP Request, Database"
                }
            }
        ]
    }