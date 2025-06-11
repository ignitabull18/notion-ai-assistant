"""
Slack Lists API integration for Jungle Scout product tracking
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
import json

from utils.logging import logger


class JungleScoutListsManager:
    """Manages Slack Lists for product tracking and monitoring"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def create_product_watchlist(
        self,
        channel_id: str,
        list_name: str,
        products: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Create a product watchlist using Slack Lists API"""
        try:
            # Create the list
            list_response = self.client.lists_create(
                name=list_name,
                description="Track Amazon product prices, rankings, and opportunities",
                channel=channel_id,
                columns=[
                    {
                        "name": "Product",
                        "type": "text",
                        "key": "product_name"
                    },
                    {
                        "name": "ASIN",
                        "type": "text", 
                        "key": "asin"
                    },
                    {
                        "name": "Current Price",
                        "type": "currency",
                        "key": "current_price"
                    },
                    {
                        "name": "Price Change",
                        "type": "percent",
                        "key": "price_change"
                    },
                    {
                        "name": "BSR",
                        "type": "number",
                        "key": "bsr"
                    },
                    {
                        "name": "Opportunity Score",
                        "type": "number",
                        "key": "opportunity_score"
                    },
                    {
                        "name": "Status",
                        "type": "select",
                        "key": "status",
                        "options": ["🟢 Buy", "🟡 Watch", "🔴 Avoid", "⚡ Hot"]
                    },
                    {
                        "name": "Last Updated",
                        "type": "date",
                        "key": "last_updated"
                    }
                ]
            )
            
            if not list_response.get("ok"):
                return None
            
            list_id = list_response["list"]["id"]
            
            # Add products to the list
            for product in products:
                self.add_product_to_list(list_id, product)
            
            return list_id
            
        except SlackApiError as e:
            logger.error(f"Error creating product watchlist: {e}")
            return None
    
    def add_product_to_list(
        self,
        list_id: str,
        product: Dict[str, Any]
    ) -> bool:
        """Add a product to an existing list"""
        try:
            # Calculate price change if historical data available
            price_change = 0
            if product.get("historical_price"):
                price_change = ((product["price"] - product["historical_price"]) / 
                               product["historical_price"]) * 100
            
            # Determine status based on opportunity score
            score = product.get("opportunity_score", 5)
            if score >= 8:
                status = "⚡ Hot"
            elif score >= 7:
                status = "🟢 Buy"
            elif score >= 5:
                status = "🟡 Watch"
            else:
                status = "🔴 Avoid"
            
            response = self.client.lists_items_create(
                list_id=list_id,
                fields={
                    "product_name": product.get("title", "Unknown Product"),
                    "asin": product.get("asin", ""),
                    "current_price": product.get("price", 0),
                    "price_change": price_change,
                    "bsr": product.get("bsr", 0),
                    "opportunity_score": score,
                    "status": status,
                    "last_updated": datetime.now().isoformat()
                }
            )
            
            return response.get("ok", False)
            
        except SlackApiError as e:
            logger.error(f"Error adding product to list: {e}")
            return False
    
    def create_keyword_tracking_list(
        self,
        channel_id: str,
        keywords: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Create a keyword performance tracking list"""
        try:
            list_response = self.client.lists_create(
                name="🎯 Keyword Performance Tracker",
                description="Monitor search volume, competition, and trends for target keywords",
                channel=channel_id,
                columns=[
                    {
                        "name": "Keyword",
                        "type": "text",
                        "key": "keyword"
                    },
                    {
                        "name": "Search Volume",
                        "type": "number",
                        "key": "search_volume"
                    },
                    {
                        "name": "Trend",
                        "type": "select",
                        "key": "trend",
                        "options": ["📈 Rising", "➡️ Stable", "📉 Declining"]
                    },
                    {
                        "name": "Competition",
                        "type": "select",
                        "key": "competition",
                        "options": ["🟢 Low", "🟡 Medium", "🔴 High"]
                    },
                    {
                        "name": "CPC",
                        "type": "currency",
                        "key": "cpc"
                    },
                    {
                        "name": "Opportunity",
                        "type": "rating",
                        "key": "opportunity",
                        "max_rating": 5
                    }
                ]
            )
            
            if not list_response.get("ok"):
                return None
            
            list_id = list_response["list"]["id"]
            
            # Add keywords to the list
            for kw in keywords:
                self._add_keyword_to_list(list_id, kw)
            
            return list_id
            
        except SlackApiError as e:
            logger.error(f"Error creating keyword list: {e}")
            return None
    
    def create_competitor_tracking_list(
        self,
        channel_id: str,
        competitors: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Create a competitor monitoring list"""
        try:
            list_response = self.client.lists_create(
                name="🎯 Competitor Monitor",
                description="Track competitor products, pricing, and market share",
                channel=channel_id,
                columns=[
                    {
                        "name": "Competitor",
                        "type": "text",
                        "key": "brand"
                    },
                    {
                        "name": "Product",
                        "type": "text",
                        "key": "product"
                    },
                    {
                        "name": "Price",
                        "type": "currency",
                        "key": "price"
                    },
                    {
                        "name": "Market Share",
                        "type": "percent",
                        "key": "market_share"
                    },
                    {
                        "name": "Rating",
                        "type": "rating",
                        "key": "rating",
                        "max_rating": 5
                    },
                    {
                        "name": "Reviews",
                        "type": "number",
                        "key": "reviews"
                    },
                    {
                        "name": "Threat Level",
                        "type": "select",
                        "key": "threat",
                        "options": ["🟢 Low", "🟡 Medium", "🔴 High", "⚡ Critical"]
                    },
                    {
                        "name": "Action",
                        "type": "checkbox",
                        "key": "needs_action"
                    }
                ]
            )
            
            if not list_response.get("ok"):
                return None
            
            list_id = list_response["list"]["id"]
            
            # Add competitors
            for comp in competitors:
                self._add_competitor_to_list(list_id, comp)
            
            return list_id
            
        except SlackApiError as e:
            logger.error(f"Error creating competitor list: {e}")
            return None
    
    def create_product_launch_checklist(
        self,
        channel_id: str,
        product_name: str
    ) -> Optional[str]:
        """Create a product launch checklist"""
        try:
            list_response = self.client.lists_create(
                name=f"🚀 Launch Checklist: {product_name}",
                description="Track all tasks for successful product launch",
                channel=channel_id,
                columns=[
                    {
                        "name": "Task",
                        "type": "text",
                        "key": "task"
                    },
                    {
                        "name": "Category",
                        "type": "select",
                        "key": "category",
                        "options": ["Research", "Sourcing", "Listing", "Marketing", "Launch", "Post-Launch"]
                    },
                    {
                        "name": "Status",
                        "type": "select",
                        "key": "status",
                        "options": ["📋 To Do", "🔄 In Progress", "✅ Complete", "⚠️ Blocked"]
                    },
                    {
                        "name": "Priority",
                        "type": "select",
                        "key": "priority",
                        "options": ["🔴 Critical", "🟡 High", "🟢 Normal", "⚪ Low"]
                    },
                    {
                        "name": "Due Date",
                        "type": "date",
                        "key": "due_date"
                    },
                    {
                        "name": "Assigned To",
                        "type": "user",
                        "key": "assignee"
                    },
                    {
                        "name": "Complete",
                        "type": "checkbox",
                        "key": "complete"
                    }
                ]
            )
            
            if not list_response.get("ok"):
                return None
            
            list_id = list_response["list"]["id"]
            
            # Add default launch tasks
            self._add_launch_tasks(list_id)
            
            return list_id
            
        except SlackApiError as e:
            logger.error(f"Error creating launch checklist: {e}")
            return None
    
    def update_list_item(
        self,
        list_id: str,
        item_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a list item with new data"""
        try:
            response = self.client.lists_items_update(
                list_id=list_id,
                item_id=item_id,
                fields=updates
            )
            
            return response.get("ok", False)
            
        except SlackApiError as e:
            logger.error(f"Error updating list item: {e}")
            return False
    
    def _add_keyword_to_list(self, list_id: str, keyword: Dict[str, Any]) -> bool:
        """Add keyword to tracking list"""
        try:
            # Determine trend
            trend_value = keyword.get("trend", "stable").lower()
            if "rising" in trend_value:
                trend = "📈 Rising"
            elif "declining" in trend_value:
                trend = "📉 Declining"
            else:
                trend = "➡️ Stable"
            
            # Determine competition
            difficulty = keyword.get("difficulty", 5)
            if difficulty <= 3:
                competition = "🟢 Low"
            elif difficulty <= 7:
                competition = "🟡 Medium"
            else:
                competition = "🔴 High"
            
            # Calculate opportunity (1-5 stars)
            volume = keyword.get("search_volume", 0)
            opportunity = min(5, max(1, int(volume / 2000)))
            
            self.client.lists_items_create(
                list_id=list_id,
                fields={
                    "keyword": keyword.get("keyword", ""),
                    "search_volume": volume,
                    "trend": trend,
                    "competition": competition,
                    "cpc": keyword.get("cpc", 0),
                    "opportunity": opportunity
                }
            )
            return True
        except Exception:
            return False
    
    def _add_competitor_to_list(self, list_id: str, competitor: Dict[str, Any]) -> bool:
        """Add competitor to tracking list"""
        try:
            # Determine threat level
            market_share = competitor.get("market_share", 0)
            if market_share > 20:
                threat = "⚡ Critical"
            elif market_share > 10:
                threat = "🔴 High"
            elif market_share > 5:
                threat = "🟡 Medium"
            else:
                threat = "🟢 Low"
            
            self.client.lists_items_create(
                list_id=list_id,
                fields={
                    "brand": competitor.get("brand", "Unknown"),
                    "product": competitor.get("title", ""),
                    "price": competitor.get("price", 0),
                    "market_share": market_share,
                    "rating": int(competitor.get("rating", 0)),
                    "reviews": competitor.get("reviews", 0),
                    "threat": threat,
                    "needs_action": market_share > 15
                }
            )
            return True
        except Exception:
            return False
    
    def _add_launch_tasks(self, list_id: str) -> None:
        """Add default product launch tasks"""
        tasks = [
            # Research Phase
            {"task": "Complete market research", "category": "Research", "priority": "🔴 Critical"},
            {"task": "Analyze top 10 competitors", "category": "Research", "priority": "🔴 Critical"},
            {"task": "Validate product opportunity", "category": "Research", "priority": "🔴 Critical"},
            {"task": "Keyword research & optimization", "category": "Research", "priority": "🟡 High"},
            
            # Sourcing Phase
            {"task": "Find reliable suppliers", "category": "Sourcing", "priority": "🔴 Critical"},
            {"task": "Order product samples", "category": "Sourcing", "priority": "🔴 Critical"},
            {"task": "Negotiate pricing & MOQ", "category": "Sourcing", "priority": "🟡 High"},
            {"task": "Quality inspection setup", "category": "Sourcing", "priority": "🟡 High"},
            
            # Listing Phase
            {"task": "Professional product photography", "category": "Listing", "priority": "🔴 Critical"},
            {"task": "Write optimized title & bullets", "category": "Listing", "priority": "🔴 Critical"},
            {"task": "Create A+ content", "category": "Listing", "priority": "🟡 High"},
            {"task": "Set up backend keywords", "category": "Listing", "priority": "🟡 High"},
            
            # Marketing Phase
            {"task": "PPC campaign setup", "category": "Marketing", "priority": "🔴 Critical"},
            {"task": "Social media strategy", "category": "Marketing", "priority": "🟢 Normal"},
            {"task": "Influencer outreach", "category": "Marketing", "priority": "🟢 Normal"},
            {"task": "Email campaign setup", "category": "Marketing", "priority": "⚪ Low"},
            
            # Launch Phase
            {"task": "Inventory shipment to FBA", "category": "Launch", "priority": "🔴 Critical"},
            {"task": "Launch pricing strategy", "category": "Launch", "priority": "🔴 Critical"},
            {"task": "Early reviewer program", "category": "Launch", "priority": "🟡 High"},
            {"task": "Monitor launch metrics", "category": "Launch", "priority": "🟡 High"},
            
            # Post-Launch
            {"task": "Optimize PPC campaigns", "category": "Post-Launch", "priority": "🟡 High"},
            {"task": "Gather customer feedback", "category": "Post-Launch", "priority": "🟡 High"},
            {"task": "Adjust pricing strategy", "category": "Post-Launch", "priority": "🟢 Normal"},
            {"task": "Plan inventory restock", "category": "Post-Launch", "priority": "🟢 Normal"}
        ]
        
        for task in tasks:
            try:
                self.client.lists_items_create(
                    list_id=list_id,
                    fields={
                        "task": task["task"],
                        "category": task["category"],
                        "status": "📋 To Do",
                        "priority": task["priority"],
                        "complete": False
                    }
                )
            except Exception:
                pass


# List view helpers
def create_list_preview_blocks(list_type: str, items_count: int) -> List[Dict[str, Any]]:
    """Create preview blocks for a list"""
    emoji_map = {
        "watchlist": "📊",
        "keywords": "🎯",
        "competitors": "🎯",
        "checklist": "🚀"
    }
    
    title_map = {
        "watchlist": "Product Watchlist Created",
        "keywords": "Keyword Tracker Created",
        "competitors": "Competitor Monitor Created",
        "checklist": "Launch Checklist Created"
    }
    
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji_map.get(list_type, '📋')} {title_map.get(list_type, 'List Created')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{items_count} items* added to your list\n"
                       f"The list will automatically update with latest data."
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 View List"
                    },
                    "style": "primary",
                    "action_id": "view_list"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "➕ Add Items"
                    },
                    "action_id": "add_to_list"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔔 Set Alerts"
                    },
                    "action_id": "configure_alerts"
                }
            ]
        }
    ]


# Global instance
jungle_scout_lists_manager = JungleScoutListsManager(None)  # Client injected at runtime