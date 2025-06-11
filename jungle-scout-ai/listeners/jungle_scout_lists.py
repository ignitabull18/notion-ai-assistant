"""
Jungle Scout Lists Manager
Specialized lists for product research, tracking, and market analysis
"""
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re

from listeners.jungle_scout_ui import create_status_blocks
from jungle_scout_ai.logging import logger


class JungleScoutListsManager:
    """Manages product research and tracking lists"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_product_watchlist(self, channel_id: str, name: str, 
                               criteria: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a product watchlist with monitoring criteria
        
        Args:
            channel_id: Channel to create list in
            name: Watchlist name
            criteria: Monitoring criteria (price thresholds, BSR limits, etc.)
            
        Returns:
            List object if successful
        """
        try:
            # Create list (mock implementation)
            list_data = {
                "id": f"LW{channel_id[:8]}",
                "title": f"🎯 {name}",
                "channel": channel_id,
                "type": "watchlist",
                "criteria": criteria,
                "emoji": "👁️",
                "color": "#FF6B6B",
                "created": datetime.now().isoformat(),
                "items_count": 0
            }
            
            return list_data
            
        except Exception as e:
            logger.error(f"Error creating product watchlist: {e}")
            return None
    
    def add_product_to_watchlist(self, list_id: str, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add a product to watchlist with monitoring settings"""
        try:
            # Create watchlist item
            item = {
                "id": f"LI{list_id[:6]}{product_data['asin']}",
                "list_id": list_id,
                "asin": product_data["asin"],
                "title": product_data["title"],
                "current_price": product_data.get("price"),
                "current_bsr": product_data.get("bsr"),
                "current_rating": product_data.get("rating"),
                "alerts": {
                    "price_drop": product_data.get("alert_price_drop", True),
                    "bsr_improve": product_data.get("alert_bsr_improve", True),
                    "new_reviews": product_data.get("alert_reviews", False),
                    "stock_low": product_data.get("alert_stock", False)
                },
                "thresholds": {
                    "price_threshold": product_data.get("price_threshold"),
                    "bsr_threshold": product_data.get("bsr_threshold")
                },
                "added": datetime.now().isoformat(),
                "last_checked": datetime.now().isoformat()
            }
            
            return item
            
        except Exception as e:
            logger.error(f"Error adding product to watchlist: {e}")
            return None
    
    def create_research_checklist(self, channel_id: str, product_category: str) -> Optional[Dict[str, Any]]:
        """Create a product research checklist"""
        try:
            # Create research checklist
            list_data = {
                "id": f"LR{channel_id[:8]}",
                "title": f"🔍 {product_category} Research Checklist",
                "channel": channel_id,
                "type": "research_checklist",
                "emoji": "✅",
                "color": "#28A745",
                "created": datetime.now().isoformat()
            }
            
            # Add standard research steps
            research_steps = [
                {"text": "Analyze market size and growth trends", "category": "market"},
                {"text": "Identify top 10 competitors", "category": "competition"},
                {"text": "Review competitor pricing strategies", "category": "competition"},
                {"text": "Analyze keyword search volume", "category": "seo"},
                {"text": "Check seasonality patterns", "category": "market"},
                {"text": "Calculate profit margins", "category": "financial"},
                {"text": "Evaluate supplier options", "category": "sourcing"},
                {"text": "Review patent/trademark issues", "category": "legal"},
                {"text": "Assess product differentiation opportunities", "category": "strategy"},
                {"text": "Create financial projections", "category": "financial"}
            ]
            
            # Mock adding items
            list_data["items"] = [
                {
                    "id": f"RI{idx}",
                    "text": step["text"],
                    "category": step["category"],
                    "status": "open",
                    "priority": 5 - (idx // 2)  # Decreasing priority
                }
                for idx, step in enumerate(research_steps)
            ]
            
            return list_data
            
        except Exception as e:
            logger.error(f"Error creating research checklist: {e}")
            return None
    
    def create_launch_checklist(self, channel_id: str, product_name: str) -> Optional[Dict[str, Any]]:
        """Create a product launch checklist"""
        try:
            list_data = {
                "id": f"LL{channel_id[:8]}",
                "title": f"🚀 {product_name} Launch Checklist",
                "channel": channel_id,
                "type": "launch_checklist",
                "emoji": "🚀",
                "color": "#6F42C1",
                "created": datetime.now().isoformat()
            }
            
            # Launch phases with tasks
            launch_phases = {
                "Pre-Launch": [
                    "Finalize product design and packaging",
                    "Order product samples",
                    "Create product photography",
                    "Write compelling product listing",
                    "Set up Amazon Seller Central account",
                    "Create brand registry"
                ],
                "Launch Week": [
                    "Create listing and upload images",
                    "Set competitive launch price",
                    "Enable PPC campaigns",
                    "Send inventory to FBA",
                    "Implement launch promotion strategy"
                ],
                "Post-Launch": [
                    "Monitor and respond to reviews",
                    "Optimize PPC campaigns",
                    "Adjust pricing based on competition",
                    "Track sales velocity",
                    "Plan inventory replenishment"
                ]
            }
            
            # Create tasks with deadlines
            items = []
            task_id = 0
            for phase, tasks in launch_phases.items():
                for task in tasks:
                    task_id += 1
                    due_date = datetime.now() + timedelta(days=task_id * 2)
                    items.append({
                        "id": f"LT{task_id}",
                        "text": task,
                        "phase": phase,
                        "status": "open",
                        "due_date": due_date.strftime("%Y-%m-%d"),
                        "priority": 5 if phase == "Pre-Launch" else 3
                    })
            
            list_data["items"] = items
            return list_data
            
        except Exception as e:
            logger.error(f"Error creating launch checklist: {e}")
            return None
    
    def create_competitor_tracking_list(self, channel_id: str, category: str, 
                                      competitors: List[str]) -> Optional[Dict[str, Any]]:
        """Create a competitor tracking list"""
        try:
            list_data = {
                "id": f"LC{channel_id[:8]}",
                "title": f"🎯 {category} Competitor Tracking",
                "channel": channel_id,
                "type": "competitor_tracking",
                "emoji": "🔍",
                "color": "#DC3545",
                "created": datetime.now().isoformat()
            }
            
            # Add competitors to track
            items = []
            for idx, competitor_asin in enumerate(competitors[:10]):  # Max 10
                items.append({
                    "id": f"CT{idx}",
                    "asin": competitor_asin,
                    "text": f"Track competitor {competitor_asin}",
                    "metrics_to_track": ["price", "bsr", "reviews", "inventory"],
                    "status": "active",
                    "last_checked": datetime.now().isoformat()
                })
            
            list_data["items"] = items
            return list_data
            
        except Exception as e:
            logger.error(f"Error creating competitor tracking list: {e}")
            return None


def create_watchlist_blocks(watchlist_data: Dict[str, Any], 
                          items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for product watchlist display"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{watchlist_data.get('emoji', '👁️')} {watchlist_data['title']}"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📊 Monitoring {len(items)} products • Last check: <t:{int(datetime.now().timestamp())}:R>"
                }
            ]
        },
        {"type": "divider"}
    ]
    
    # Show products with alerts
    alerts = []
    watching = []
    
    for item in items:
        # Check for triggered alerts (mock logic)
        has_alert = False
        alert_messages = []
        
        if item.get("current_price", 100) < item.get("thresholds", {}).get("price_threshold", 90):
            has_alert = True
            alert_messages.append("💰 Price dropped!")
        
        if item.get("current_bsr", 10000) < item.get("thresholds", {}).get("bsr_threshold", 5000):
            has_alert = True
            alert_messages.append("📈 BSR improved!")
        
        if has_alert:
            alerts.append((item, alert_messages))
        else:
            watching.append(item)
    
    # Show alerts first
    if alerts:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🚨 Alerts ({len(alerts)})*"
            }
        })
        
        for item, messages in alerts[:3]:  # Show max 3
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{item['title'][:50]}...*\n"
                           f"ASIN: `{item['asin']}` • {' • '.join(messages)}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Details"
                    },
                    "action_id": f"view_alert_details_{item['asin']}",
                    "style": "primary"
                }
            })
    
    # Show watching products count
    if watching:
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"👁️ Watching {len(watching)} more products"
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
                    "text": "➕ Add Product"
                },
                "action_id": f"add_to_watchlist_{watchlist_data['id']}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "⚙️ Settings"
                },
                "action_id": f"watchlist_settings_{watchlist_data['id']}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Report"
                },
                "action_id": f"watchlist_report_{watchlist_data['id']}"
            }
        ]
    })
    
    return blocks


def create_research_checklist_blocks(checklist_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create blocks for research checklist display"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": checklist_data['title']
            }
        }
    ]
    
    # Group tasks by category
    categories = {}
    for item in checklist_data.get("items", []):
        category = item.get("category", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    # Category emoji map
    category_emojis = {
        "market": "📊",
        "competition": "🎯",
        "seo": "🔍",
        "financial": "💰",
        "sourcing": "📦",
        "legal": "⚖️",
        "strategy": "🎨"
    }
    
    # Display by category
    for category, items in categories.items():
        completed = sum(1 for item in items if item["status"] == "completed")
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{category_emojis.get(category, '📌')} *{category.title()}* ({completed}/{len(items)})"
            }
        })
        
        for item in items:
            if item["status"] != "completed":
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{'☐' if item['status'] == 'open' else '🔄'} {item['text']}"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✓" if item['status'] == 'open' else "Complete"
                        },
                        "action_id": f"complete_research_item_{item['id']}",
                        "value": item['id']
                    }
                })
    
    # Progress summary
    total_items = len(checklist_data.get("items", []))
    completed_items = sum(1 for item in checklist_data.get("items", []) 
                         if item["status"] == "completed")
    progress_pct = int((completed_items / total_items * 100)) if total_items > 0 else 0
    
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Progress: {progress_pct}%* ({completed_items}/{total_items} completed)"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "📊 View Report"
            },
            "action_id": f"view_research_report_{checklist_data['id']}",
            "style": "primary"
        }
    })
    
    return blocks


def create_jungle_scout_list_templates() -> List[Dict[str, Any]]:
    """Create blocks for Jungle Scout list templates"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📋 Product Research List Templates"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Choose a template to organize your Amazon seller journey:"
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*👁️ Product Watchlist*\nMonitor ASINs for price drops and BSR changes"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_product_watchlist",
                "style": "primary"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔍 Research Checklist*\nComplete product validation checklist"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_research_checklist"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🚀 Launch Checklist*\nStep-by-step product launch tasks"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_launch_checklist"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎯 Competitor Tracker*\nMonitor top competitors in your niche"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_competitor_tracker"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📦 Supplier Evaluation*\nCompare and track supplier options"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Create"
                },
                "action_id": "create_supplier_list"
            }
        }
    ]


def create_add_to_watchlist_modal(list_id: str) -> Dict[str, Any]:
    """Create modal for adding product to watchlist"""
    return {
        "type": "modal",
        "callback_id": "add_to_watchlist_modal",
        "title": {
            "type": "plain_text",
            "text": "Add to Watchlist"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add Product"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "private_metadata": list_id,
        "blocks": [
            {
                "type": "input",
                "block_id": "product_asin",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "asin_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "B08N5WRWNW"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Product ASIN"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Alert Settings*"
                }
            },
            {
                "type": "input",
                "block_id": "alert_types",
                "element": {
                    "type": "checkboxes",
                    "action_id": "alerts_input",
                    "initial_options": [
                        {
                            "text": {"type": "plain_text", "text": "💰 Price drops"},
                            "value": "price_drop"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📈 BSR improvements"},
                            "value": "bsr_improve"
                        }
                    ],
                    "options": [
                        {
                            "text": {"type": "plain_text", "text": "💰 Price drops"},
                            "value": "price_drop"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📈 BSR improvements"},
                            "value": "bsr_improve"
                        },
                        {
                            "text": {"type": "plain_text", "text": "⭐ New reviews"},
                            "value": "new_reviews"
                        },
                        {
                            "text": {"type": "plain_text", "text": "📦 Stock changes"},
                            "value": "stock_changes"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Alert me on"
                }
            },
            {
                "type": "input",
                "block_id": "price_threshold",
                "element": {
                    "type": "number_input",
                    "action_id": "price_input",
                    "is_decimal_allowed": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "25.99"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Alert if price drops below"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "bsr_threshold",
                "element": {
                    "type": "number_input",
                    "action_id": "bsr_input",
                    "is_decimal_allowed": False,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "5000"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Alert if BSR improves to"
                },
                "optional": True
            }
        ]
    }
}