"""
Advanced Slack Assistant API features for Jungle Scout AI
"""
from typing import Dict, List, Any, Optional
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
import time
import json
from datetime import datetime

from utils.logging import logger


class JungleScoutAssistantFeatures:
    """Implements advanced Slack Assistant API features"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def set_thread_status(
        self, 
        channel_id: str, 
        thread_ts: str, 
        status: str,
        emoji: str = None
    ) -> bool:
        """Set status on assistant thread to show processing state"""
        try:
            status_text = {
                "analyzing": "🔍 Analyzing market data...",
                "calculating": "🧮 Calculating opportunity scores...",
                "comparing": "📊 Comparing competitors...",
                "generating": "📝 Generating insights...",
                "complete": "✅ Analysis complete!"
            }.get(status, status)
            
            # Add emoji if provided
            if emoji:
                status_text = f"{emoji} {status_text}"
            
            response = self.client.assistant_threads_setStatus(
                channel_id=channel_id,
                thread_ts=thread_ts,
                status=status_text
            )
            
            return response.get("ok", False)
            
        except SlackApiError as e:
            logger.error(f"Error setting thread status: {e}")
            return False
    
    def set_suggested_prompts(
        self,
        channel_id: str,
        thread_ts: str,
        prompts: List[Dict[str, str]]
    ) -> bool:
        """Set suggested prompts for next actions"""
        try:
            # Format prompts for Slack API
            formatted_prompts = []
            for prompt in prompts[:4]:  # Max 4 prompts
                formatted_prompts.append({
                    "title": prompt.get("title", ""),
                    "message": prompt.get("message", "")
                })
            
            response = self.client.assistant_threads_setSuggestedPrompts(
                channel_id=channel_id,
                thread_ts=thread_ts,
                prompts=formatted_prompts
            )
            
            return response.get("ok", False)
            
        except SlackApiError as e:
            logger.error(f"Error setting suggested prompts: {e}")
            return False
    
    def set_thread_title(
        self,
        channel_id: str,
        thread_ts: str,
        title: str
    ) -> bool:
        """Set a custom title for the assistant thread"""
        try:
            response = self.client.assistant_threads_setTitle(
                channel_id=channel_id,
                thread_ts=thread_ts,
                title=title
            )
            
            return response.get("ok", False)
            
        except SlackApiError as e:
            logger.error(f"Error setting thread title: {e}")
            return False
    
    def create_smart_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate smart suggestions based on analysis context"""
        suggestions = []
        
        # Product research context
        if context.get("type") == "product_research":
            product = context.get("top_product", {})
            if product:
                suggestions.extend([
                    {
                        "title": "🔍 Deep dive on top product",
                        "message": f"competitor {product.get('asin', '')}"
                    },
                    {
                        "title": "📈 Analyze market trends",
                        "message": f"trends {context.get('category', 'electronics')}"
                    },
                    {
                        "title": "🎯 Find related keywords",
                        "message": f"keywords {context.get('search_query', '')}"
                    },
                    {
                        "title": "📊 Create tracking dashboard",
                        "message": "dashboard sales"
                    }
                ])
        
        # Competitor analysis context
        elif context.get("type") == "competitor_analysis":
            suggestions.extend([
                {
                    "title": "📋 Track this competitor",
                    "message": f"track {context.get('asin', '')}"
                },
                {
                    "title": "🔍 Find similar products",
                    "message": f"research {context.get('category', '')}"
                },
                {
                    "title": "📊 Compare sales performance",
                    "message": "sales last 30 days"
                },
                {
                    "title": "💡 Validate opportunity",
                    "message": f"validate {context.get('product_idea', '')}"
                }
            ])
        
        # Keyword analysis context
        elif context.get("type") == "keyword_analysis":
            keyword = context.get("keyword", "")
            suggestions.extend([
                {
                    "title": "🔍 Find products for this keyword",
                    "message": f"research {keyword}"
                },
                {
                    "title": "📈 Check keyword trends",
                    "message": f"trends {keyword}"
                },
                {
                    "title": "🎯 Find related keywords",
                    "message": f"keywords {keyword} variations"
                },
                {
                    "title": "📝 Create keyword strategy",
                    "message": f"validate {keyword} product opportunity"
                }
            ])
        
        return suggestions[:4]  # Return max 4 suggestions
    
    def animate_processing(
        self,
        channel_id: str,
        thread_ts: str,
        steps: List[str],
        delay: float = 1.5
    ) -> None:
        """Animate through processing steps with status updates"""
        try:
            for i, step in enumerate(steps):
                # Calculate progress
                progress = int((i + 1) / len(steps) * 100)
                
                # Set status with progress
                status = f"{step} ({progress}%)"
                self.set_thread_status(channel_id, thread_ts, status)
                
                # Wait before next step
                if i < len(steps) - 1:
                    time.sleep(delay)
            
            # Set complete status
            self.set_thread_status(channel_id, thread_ts, "complete", "✅")
            
        except Exception as e:
            logger.error(f"Error animating processing: {e}")


# Advanced Block Kit components with rich interactions
def create_advanced_product_card(product: Dict[str, Any]) -> Dict[str, Any]:
    """Create an advanced product card with rich components"""
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*{product.get('title', 'Product')}*\n"
                   f"ASIN: `{product.get('asin', '')}`\n"
                   f"💰 ${product.get('price', 0):.2f} | "
                   f"⭐ {product.get('rating', 0)}/5 ({product.get('reviews', 0):,} reviews)"
        },
        "accessory": {
            "type": "overflow",
            "action_id": f"product_overflow_{product.get('asin', '')}",
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "🔍 Deep Analysis"
                    },
                    "value": json.dumps({"action": "analyze", "asin": product.get('asin', '')})
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Track Product"
                    },
                    "value": json.dumps({"action": "track", "asin": product.get('asin', '')})
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "🎯 Find Keywords"
                    },
                    "value": json.dumps({"action": "keywords", "asin": product.get('asin', '')})
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "📈 View Trends"
                    },
                    "value": json.dumps({"action": "trends", "asin": product.get('asin', '')})
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "📝 Create Report"
                    },
                    "value": json.dumps({"action": "report", "asin": product.get('asin', '')})
                }
            ]
        }
    }


def create_rich_text_insights(insights: Dict[str, Any]) -> Dict[str, Any]:
    """Create rich text block with formatted insights"""
    elements = []
    
    # Add title
    elements.append({
        "type": "rich_text_section",
        "elements": [
            {
                "type": "text",
                "text": "🔍 Market Insights\n",
                "style": {
                    "bold": True
                }
            }
        ]
    })
    
    # Add insights with formatting
    if insights.get("opportunities"):
        elements.append({
            "type": "rich_text_section",
            "elements": [
                {
                    "type": "text",
                    "text": "Opportunities: ",
                    "style": {"bold": True}
                },
                {
                    "type": "text",
                    "text": insights["opportunities"],
                    "style": {"italic": True}
                }
            ]
        })
    
    # Add list of key findings
    if insights.get("findings"):
        list_items = []
        for finding in insights["findings"]:
            list_items.append({
                "type": "rich_text_section",
                "elements": [
                    {"type": "text", "text": finding}
                ]
            })
        
        elements.append({
            "type": "rich_text_list",
            "style": "bullet",
            "elements": list_items
        })
    
    return {
        "type": "rich_text",
        "elements": elements
    }


def create_date_range_picker() -> Dict[str, Any]:
    """Create date picker for trend analysis"""
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "📅 *Select Analysis Date Range*"
        },
        "accessory": {
            "type": "datepicker",
            "action_id": "trend_date_range",
            "initial_date": datetime.now().strftime("%Y-%m-%d"),
            "placeholder": {
                "type": "plain_text",
                "text": "Select end date"
            }
        }
    }


def create_bulk_action_checkboxes(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create checkboxes for bulk product actions"""
    options = []
    for product in products[:10]:  # Limit to 10
        options.append({
            "text": {
                "type": "mrkdwn",
                "text": f"*{product.get('title', 'Product')}*\n"
                       f"${product.get('price', 0):.2f} | BSR: {product.get('bsr', 'N/A')}"
            },
            "value": product.get('asin', '')
        })
    
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "📦 *Select Products for Bulk Actions*"
        },
        "accessory": {
            "type": "checkboxes",
            "action_id": "bulk_product_select",
            "options": options
        }
    }


# Global instance
jungle_scout_assistant_features = JungleScoutAssistantFeatures(None)  # Client injected at runtime