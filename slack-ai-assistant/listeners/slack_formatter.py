"""
Slack Block Kit formatter for beautiful assistant responses
"""
import re
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SlackFormatter:
    """Format assistant responses using Slack Block Kit for beautiful UI"""
    
    @staticmethod
    def format_channel_summary(channel_id: str, messages: List[Dict], summary: str) -> List[Dict[str, Any]]:
        """Format a channel summary with rich UI"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Channel Summary",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Summary of <#{channel_id}> - Last {len(messages)} messages"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": summary
                }
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Canvas Summary",
                            "emoji": True
                        },
                        "style": "primary",
                        "action_id": "create_summary_canvas"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Search in Channel",
                            "emoji": True
                        },
                        "action_id": "search_channel"
                    }
                ]
            }
        ]
        return blocks
    
    @staticmethod
    def format_search_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results with rich UI"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔍 Search Results",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Found {len(results)} results for *\"{query}\"*"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        for idx, result in enumerate(results[:10]):  # Limit to 10 results
            message_text = result.get('text', 'No content')
            channel_id = result.get('channel', {}).get('id', 'Unknown')
            timestamp = result.get('ts', '')
            user = result.get('user', 'Unknown')
            
            # Truncate long messages
            if len(message_text) > 200:
                message_text = message_text[:197] + "..."
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*In <#{channel_id}>*\n{message_text}\n_<@{user}> • <!date^{int(float(timestamp))}^{{date_short_pretty}} at {{time}}|{timestamp}>_"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Go to Message",
                        "emoji": True
                    },
                    "url": f"https://slack.com/archives/{channel_id}/p{timestamp.replace('.', '')}",
                    "action_id": f"goto_message_{idx}"
                }
            })
            
            if idx < len(results) - 1 and idx < 9:
                blocks.append({"type": "divider"})
        
        if len(results) > 10:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_Showing 10 of {len(results)} results. Refine your search for better results._"
                    }
                ]
            })
        
        return blocks
    
    @staticmethod
    def format_reminder_created(reminder_text: str, time: str, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """Format reminder creation confirmation"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⏰ Reminder Set!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reminder:* {reminder_text}\n*When:* <!date^{int(time)}^{{date_long_pretty}} at {{time}}|{time}>"
                }
            }
        ]
        
        if channel:
            blocks[1]["text"]["text"] += f"\n*Where:* <#{channel}>"
        
        blocks.extend([
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View All Reminders",
                            "emoji": True
                        },
                        "action_id": "view_reminders"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Cancel This Reminder",
                            "emoji": True
                        },
                        "style": "danger",
                        "action_id": "cancel_reminder"
                    }
                ]
            }
        ])
        
        return blocks
    
    @staticmethod
    def format_team_analytics(analytics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format team analytics with visualizations"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Team Analytics",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Period: {analytics_data.get('period', 'Last 7 days')}"
                    }
                ]
            },
            {"type": "divider"}
        ]
        
        # Key metrics
        metrics = analytics_data.get('metrics', {})
        if metrics:
            fields = []
            for metric, value in metrics.items():
                fields.append({
                    "type": "mrkdwn",
                    "text": f"*{metric}*\n{value}"
                })
            
            blocks.append({
                "type": "section",
                "fields": fields[:10]  # Slack limits to 10 fields
            })
            blocks.append({"type": "divider"})
        
        # Top contributors
        if 'top_contributors' in analytics_data:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 Top Contributors*"
                }
            })
            
            for idx, contributor in enumerate(analytics_data['top_contributors'][:5]):
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"{idx + 1}. <@{contributor['user_id']}> - {contributor['message_count']} messages"
                        }
                    ]
                })
        
        # Actions
        blocks.extend([
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Analytics Canvas",
                            "emoji": True
                        },
                        "style": "primary",
                        "action_id": "create_analytics_canvas"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Export Report",
                            "emoji": True
                        },
                        "action_id": "export_analytics"
                    }
                ]
            }
        ])
        
        return blocks
    
    @staticmethod
    def format_assistant_response(response_text: str) -> List[Dict[str, Any]]:
        """Convert assistant response to beautiful Slack blocks"""
        blocks = []
        
        # Split response into paragraphs
        paragraphs = response_text.split('\n\n')
        
        for para in paragraphs:
            if not para.strip():
                continue
                
            # Headers (marked with #)
            if para.startswith('#'):
                level = len(para) - len(para.lstrip('#'))
                header_text = para.lstrip('#').strip()
                
                if level == 1:
                    blocks.append({
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": header_text,
                            "emoji": True
                        }
                    })
                else:
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{header_text}*"
                        }
                    })
                blocks.append({"type": "divider"})
                
            # Bullet lists
            elif para.strip().startswith(('- ', '• ', '* ', '1. ')):
                list_items = []
                for line in para.split('\n'):
                    if line.strip().startswith(('- ', '• ', '* ')):
                        list_items.append(line.strip()[2:])
                    elif re.match(r'^\d+\.\s', line.strip()):
                        list_items.append(re.sub(r'^\d+\.\s', '', line.strip()))
                
                if list_items:
                    formatted_list = '\n'.join([f"• {item}" for item in list_items])
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": formatted_list
                        }
                    })
                    
            # Code blocks
            elif para.startswith('```'):
                code_content = para.strip('`').strip()
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{code_content}```"
                    }
                })
                
            # Regular paragraphs
            else:
                # Truncate long paragraphs
                text = para if len(para) <= 2000 else para[:1997] + "..."
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                })
        
        # Add suggested actions based on content
        if any(word in response_text.lower() for word in ['summary', 'summarize', 'overview']):
            blocks.extend([
                {"type": "divider"},
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Create Canvas",
                                "emoji": True
                            },
                            "style": "primary",
                            "action_id": "create_canvas_from_summary"
                        }
                    ]
                }
            ])
        
        # Slack has a limit of 50 blocks per message
        if len(blocks) > 50:
            blocks = blocks[:48]
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Response truncated due to length._"
                    }
                ]
            })
        
        return blocks
    
    @staticmethod
    def format_error_message(error: str) -> List[Dict[str, Any]]:
        """Format error messages with helpful styling"""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Oops! Something went wrong*\n\n{error}"
                }
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Tip: Try rephrasing your request or check if I have the necessary permissions_"
                    }
                ]
            }
        ]
    
    @staticmethod
    def format_status_update(action: str, status: str, details: Optional[str] = None) -> List[Dict[str, Any]]:
        """Format status updates with progress indicators"""
        status_emoji = {
            "starting": "⏳",
            "in_progress": "🔄", 
            "completed": "✅",
            "failed": "❌"
        }
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji.get(status, '📍')} *{action}*"
                }
            }
        ]
        
        if details:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": details[:150]  # Ensure under context limit
                    }
                ]
            })
        
        return blocks
    
    @staticmethod
    def format_welcome_message(user_id: str) -> List[Dict[str, Any]]:
        """Format a welcome message with quick actions"""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "👋 Welcome to Slack AI Assistant!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey <@{user_id}>! I'm here to help you work more efficiently in Slack. Here's what I can do:"
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Summarize Conversations*\nGet quick summaries of long channel discussions"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_summarize"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*⏰ Smart Reminders*\nSet intelligent reminders based on conversations"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_reminder"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔍 Search Across Channels*\nFind information quickly across all your channels"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_search"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📈 Team Analytics*\nGet insights into team communication patterns"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_analytics"
                }
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Just ask me anything or click a button above to get started!_"
                    }
                ]
            }
        ]