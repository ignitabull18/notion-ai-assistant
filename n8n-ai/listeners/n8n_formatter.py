"""
N8N Response Formatter - Format agent responses for Slack
"""
import json
import logging
from typing import Dict, Any, List, Optional, Union
from listeners.n8n_ui import (
    create_workflow_blocks,
    create_workflow_list_blocks,
    create_execution_blocks
)

logger = logging.getLogger(__name__)


def format_workflow_response(response: Any) -> Dict[str, Any]:
    """Format workflow-related responses for Slack"""
    try:
        # Handle string responses
        if isinstance(response, str):
            return format_text_response(response)
        
        # Handle agent response objects
        if hasattr(response, 'data') and response.data:
            return format_data_response(response.data)
        
        # Handle dict responses
        if isinstance(response, dict):
            return format_dict_response(response)
        
        # Default formatting
        return format_text_response(str(response))
        
    except Exception as e:
        logger.error(f"Error formatting response: {e}")
        return format_error_response(str(e))


def format_text_response(text: str) -> Dict[str, Any]:
    """Format plain text response"""
    # Split into sections if long
    sections = text.split('\n\n')
    blocks = []
    
    for section in sections[:10]:  # Limit to avoid block limit
        if section.strip():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": section[:3000]  # Slack text limit
                }
            })
    
    return {
        "blocks": blocks,
        "text": text[:150]  # Fallback text
    }


def format_data_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format structured data response"""
    blocks = []
    
    # Handle workflow data
    if "workflow" in data:
        workflow = data["workflow"]
        blocks.extend(create_workflow_blocks(workflow))
    
    # Handle workflow list
    elif "workflows" in data:
        workflows = data["workflows"]
        blocks.extend(create_workflow_list_blocks(workflows))
    
    # Handle execution data
    elif "execution" in data:
        execution = data["execution"]
        blocks.extend(create_execution_blocks(execution))
    
    # Handle executions list
    elif "executions" in data:
        blocks.extend(format_executions_list(data["executions"]))
    
    # Handle node list
    elif "nodes" in data:
        blocks.extend(format_nodes_list(data["nodes"]))
    
    # Handle workflow JSON
    elif "workflow_json" in data:
        blocks.extend(format_workflow_json(data["workflow_json"]))
    
    # Handle suggestions
    elif "suggestions" in data:
        blocks.extend(format_suggestions(data["suggestions"]))
    
    # Handle documentation
    elif "documentation" in data:
        blocks.extend(format_documentation(data["documentation"]))
    
    # Handle error
    elif "error" in data:
        return format_error_response(data["error"])
    
    # Handle success message
    elif "message" in data:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✅ {data['message']}"
            }
        })
    
    # Add any additional info
    for key, value in data.items():
        if key not in ["workflow", "workflows", "execution", "executions", 
                       "nodes", "workflow_json", "suggestions", "documentation",
                       "error", "message", "success"]:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{key.title()}:* {format_value(value)}"
                }
            })
    
    return {
        "blocks": blocks,
        "text": "N8N Response"
    }


def format_dict_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format dictionary response"""
    # Check if it's a tool response
    if "success" in data:
        if data["success"]:
            return format_data_response(data)
        else:
            return format_error_response(data.get("error", "Unknown error"))
    
    # Otherwise format as data
    return format_data_response(data)


def format_executions_list(executions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format list of executions"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Workflow Executions"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Found {len(executions)} execution(s)*"
            }
        }
    ]
    
    for execution in executions[:5]:  # Show latest 5
        status_emoji = {
            'success': '✅',
            'error': '❌',
            'running': '🔄',
            'waiting': '⏳'
        }.get(execution.get('status', 'unknown'), '❓')
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{status_emoji} *{execution.get('workflowName', 'Unknown')}*\n"
                       f"ID: `{execution.get('id')}` | "
                       f"Started: {execution.get('startedAt', 'Unknown')[:19]}"
            }
        })
    
    return blocks


def format_nodes_list(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format list of available nodes"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔧 Available N8N Nodes"
            }
        }
    ]
    
    # Group by category
    categories = {}
    for node in nodes:
        category = node.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(node)
    
    for category, category_nodes in categories.items():
        node_list = []
        for node in category_nodes[:5]:
            node_list.append(f"• *{node['name']}* (`{node['type']}`)")
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{category}:*\n" + "\n".join(node_list)
            }
        })
    
    return blocks


def format_workflow_json(workflow_json: str) -> List[Dict[str, Any]]:
    """Format workflow JSON for display"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📋 Workflow JSON"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Here's your workflow in JSON format:"
            }
        }
    ]
    
    # Truncate if too long
    if len(workflow_json) > 2000:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{workflow_json[:2000]}...```\n_JSON truncated. Use export to canvas for full content._"
            }
        })
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"```{workflow_json}```"
            }
        })
    
    return blocks


def format_suggestions(suggestions: str) -> List[Dict[str, Any]]:
    """Format workflow improvement suggestions"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "💡 Workflow Improvement Suggestions"
            }
        }
    ]
    
    # Split suggestions into sections
    sections = suggestions.split('\n\n')
    for section in sections[:5]:
        if section.strip():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": section[:3000]
                }
            })
    
    return blocks


def format_documentation(documentation: str) -> List[Dict[str, Any]]:
    """Format workflow documentation"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📚 Workflow Documentation"
            }
        }
    ]
    
    # Take first part for preview
    preview = documentation[:1000]
    if len(documentation) > 1000:
        preview += "...\n\n_Full documentation exported to canvas._"
    
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": preview
        }
    })
    
    return blocks


def format_error_response(error: str) -> Dict[str, Any]:
    """Format error response"""
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"❌ *Error:* {error}"
                }
            }
        ],
        "text": f"Error: {error}"
    }


def format_value(value: Any) -> str:
    """Format a value for display"""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    elif isinstance(value, list):
        return f"{len(value)} items"
    elif isinstance(value, dict):
        return f"{len(value)} properties"
    else:
        return str(value)[:100]  # Truncate long values