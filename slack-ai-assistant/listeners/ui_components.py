"""
Enhanced UI components using Slack Block Kit and new AI features
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


def create_assistant_welcome_blocks() -> List[Dict[str, Any]]:
    """Create rich welcome message blocks for AI assistant"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🤖 Slack AI Assistant"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "I'm here to help you with intelligent Slack automation! Here's what I can do:"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*📊 Summarize*\nChannel conversations and meetings"
                },
                {
                    "type": "mrkdwn",
                    "text": "*⏰ Remind*\nSmart reminders and scheduling"
                },
                {
                    "type": "mrkdwn",
                    "text": "*🔍 Search*\nFind messages across channels"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📅 Schedule*\nPost messages at specific times"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📈 Analyze*\nTeam activity and metrics"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📝 Canvas*\nCreate collaborative documents"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Summarize This Channel"
                    },
                    "action_id": "quick_summarize",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Create Canvas"
                    },
                    "action_id": "create_canvas"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Set Reminder"
                    },
                    "action_id": "quick_reminder"
                }
            ]
        }
    ]


def create_summary_result_blocks(
    summary: str, 
    channel_name: str, 
    timeframe: str,
    key_topics: List[str] = None,
    action_items: List[str] = None
) -> List[Dict[str, Any]]:
    """Create rich summary result blocks"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Summary: #{channel_name}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 *Timeframe:* {timeframe} | 🕒 *Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Summary:*\n{summary}"
            }
        }
    ]
    
    if key_topics:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🏷️ Key Topics:*\n" + "\n".join([f"• {topic}" for topic in key_topics])
            }
        })
    
    if action_items:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*✅ Action Items:*\n" + "\n".join([f"• {item}" for item in action_items])
            }
        })
    
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Create Canvas"
                    },
                    "action_id": "create_summary_canvas",
                    "value": f"summary:{channel_name}:{timeframe}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Share Summary"
                    },
                    "action_id": "share_summary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Set Follow-up"
                    },
                    "action_id": "set_followup"
                }
            ]
        }
    ])
    
    return blocks


def create_reminder_form_modal() -> Dict[str, Any]:
    """Create modal form for setting reminders"""
    return {
        "type": "modal",
        "callback_id": "reminder_modal",
        "title": {
            "type": "plain_text",
            "text": "⏰ Set Reminder"
        },
        "submit": {
            "type": "plain_text",
            "text": "Create Reminder"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "reminder_text",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "What should I remind you about?"
                    },
                    "multiline": True
                },
                "label": {
                    "type": "plain_text",
                    "text": "Reminder Text"
                }
            },
            {
                "type": "input",
                "block_id": "reminder_time",
                "element": {
                    "type": "datetimepicker",
                    "action_id": "datetime_input"
                },
                "label": {
                    "type": "plain_text",
                    "text": "When?"
                }
            },
            {
                "type": "input",
                "block_id": "reminder_target",
                "element": {
                    "type": "radio_buttons",
                    "action_id": "target_input",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Just me (DM)"
                            },
                            "value": "dm"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "This channel"
                            },
                            "value": "channel"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Where to send reminder?"
                }
            }
        ]
    }


def create_canvas_preview_blocks(canvas_url: str, title: str, preview: str) -> List[Dict[str, Any]]:
    """Create blocks showing canvas creation result"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📝 Canvas Created!"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{title}*\n{preview}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Open Canvas"
                },
                "url": canvas_url,
                "style": "primary"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📝 Canvas is collaborative and will update automatically"
                }
            ]
        }
    ]


def create_search_results_blocks(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Create rich search results display"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔍 Search Results: \"{query}\""
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Found {len(results)} results"
                }
            ]
        }
    ]
    
    for i, result in enumerate(results[:5]):  # Limit to 5 results
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*#{result.get('channel', 'unknown')}* • {result.get('timestamp', '')}\n{result.get('text', '')[:200]}..."
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View"
                    },
                    "action_id": f"view_message_{i}",
                    "value": result.get('permalink', '')
                }
            }
        ])
    
    if len(results) > 5:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"... and {len(results) - 5} more results"
                }
            ]
        })
    
    return blocks


def create_assistant_status_blocks(status: str, message: str) -> List[Dict[str, Any]]:
    """Create status blocks for assistant operations"""
    status_emoji = {
        "thinking": "🤔",
        "processing": "⚡",
        "searching": "🔍",
        "creating": "✨",
        "complete": "✅",
        "error": "❌"
    }
    
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{status_emoji.get(status, '🤖')} {message}"
            }
        }
    ]


def get_suggested_prompts(context: str = "general") -> List[Dict[str, str]]:
    """Get context-appropriate suggested prompts"""
    prompts = {
        "general": [
            {"title": "Summarize today", "message": "summarize this channel from today"},
            {"title": "Quick reminder", "message": "remind me to review PRs tomorrow at 2pm"},
            {"title": "Search messages", "message": "search for deployment issues"},
            {"title": "Create meeting canvas", "message": "create a canvas for our team meeting notes"}
        ],
        "channel": [
            {"title": "Summarize this channel", "message": "summarize this channel from the last week"},
            {"title": "Analyze activity", "message": "analyze channel activity patterns"},
            {"title": "Find key topics", "message": "search for main discussion topics"},
            {"title": "Create summary canvas", "message": "create a canvas with channel highlights"}
        ],
        "dm": [
            {"title": "Set personal reminder", "message": "remind me to follow up on project tomorrow"},
            {"title": "Search my messages", "message": "search my recent conversations"},
            {"title": "Create task list", "message": "create a canvas with my action items"},
            {"title": "Schedule message", "message": "schedule a message for later"}
        ]
    }
    
    return prompts.get(context, prompts["general"])


def create_workflow_template_blocks(templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for workflow template selection"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔄 Slack Workflow Templates"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select a workflow template to automate your Slack workspace:"
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


def create_welcome_blocks() -> List[Dict[str, Any]]:
    """Create welcome blocks for Slack AI Assistant"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "👋 Welcome to Slack AI Assistant"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*I can help you with:*\n• 📊 Channel summaries and analytics\n• 🔍 Searching messages and files\n• ⏰ Setting reminders and scheduling\n• 📝 Creating collaborative canvases\n• 🔄 Automating workflows"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Summarize Channel"
                    },
                    "action_id": "quick_summarize"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Create Canvas"
                    },
                    "action_id": "create_canvas"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "⏰ Set Reminder"
                    },
                    "action_id": "set_reminder"
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
        }
    ]