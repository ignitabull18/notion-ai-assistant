"""
Jungle Scout Block Kit formatter for beautiful AI Assistant responses
"""
import re
import json
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class JungleScoutFormatter:
    """Format Jungle Scout responses using Slack Block Kit for beautiful UI"""
    
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
                # Check for Amazon links and add buttons
                amazon_link_pattern = r'https?://(?:www\.)?amazon\.com/[^\s]+'
                if re.search(amazon_link_pattern, para):
                    match = re.search(amazon_link_pattern, para)
                    link_text = para[:match.start()].strip()
                    
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": link_text if link_text else para[:200]
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View on Amazon",
                                "emoji": True
                            },
                            "url": match.group(0),
                            "action_id": "view_amazon_product"
                        }
                    })
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
        if any(word in response_text.lower() for word in ['product', 'research', 'opportunity']):
            blocks.extend([
                {"type": "divider"},
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Create Research Canvas",
                                "emoji": True
                            },
                            "style": "primary",
                            "action_id": "create_research_canvas_from_response"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Track Products",
                                "emoji": True
                            },
                            "action_id": "track_products_from_response"
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
                        "text": "_Tip: Check your search query or try a different ASIN/keyword_"
                    }
                ]
            }
        ]
    
    @staticmethod
    def format_status_update(action: str, status: str, details: Optional[str] = None) -> List[Dict[str, Any]]:
        """Format status updates with progress indicators"""
        status_emoji = {
            "starting": "⏳",
            "researching": "🔍",
            "analyzing": "📊",
            "processing": "⚡", 
            "tracking": "📈",
            "validating": "✅",
            "completed": "🎉",
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
                    "text": "🌲 Welcome to Jungle Scout AI Assistant!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hey <@{user_id}>! I'm your AI-powered Amazon selling assistant. I can help you discover profitable products, analyze competitors, and dominate the marketplace."
                }
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔍 Product Research*\nFind high-opportunity products with AI-powered insights"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_product_research"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Sales Analytics*\nTrack performance metrics and revenue trends"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_sales_analytics"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎯 Keyword Analysis*\nOptimize listings with powerful keyword insights"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_keyword_analysis"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔬 Competitor Intelligence*\nAnalyze competition and find market gaps"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Try It",
                        "emoji": True
                    },
                    "action_id": "try_competitor_analysis"
                }
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "_Use commands like `research wireless earbuds` or click a button above to get started!_"
                    }
                ]
            }
        ]
    
    @staticmethod
    def format_channel_analysis(channel_id: str, analysis: str, key_insights: List[str] = None) -> List[Dict[str, Any]]:
        """Format channel analysis results"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📊 Amazon Seller Discussion Analysis",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Analysis of <#{channel_id}> discussions"
                    }
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": analysis
                }
            }
        ]
        
        if key_insights:
            blocks.extend([
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*🎯 Key Insights:*"
                    }
                }
            ])
            
            insights_text = "\n".join([f"• {insight}" for insight in key_insights[:5]])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": insights_text
                }
            })
        
        blocks.extend([
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Research Top Opportunity",
                            "emoji": True
                        },
                        "style": "primary",
                        "action_id": "research_from_analysis"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Strategy Canvas",
                            "emoji": True
                        },
                        "action_id": "create_strategy_canvas"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Track Mentioned Products",
                            "emoji": True
                        },
                        "action_id": "track_mentioned_products"
                    }
                ]
            }
        ])
        
        return blocks