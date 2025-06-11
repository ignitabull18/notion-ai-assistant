"""
Jungle Scout Bookmarks Manager
Handles bookmarks for Amazon products, research reports, and market data
"""
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

from jungle_scout_ai.logging import logger


class JungleScoutBookmarksManager:
    """Manages product research and market analysis bookmarks"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def add_product_bookmark(self, channel_id: str, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add an Amazon product as a bookmark
        
        Args:
            channel_id: The channel to add bookmark to
            product_data: Dict containing product info
                - asin: Amazon ASIN
                - title: Product title
                - url: Amazon URL
                - price: Current price
                - rating: Product rating
                - opportunity_score: Optional opportunity score
                
        Returns:
            Bookmark object if successful
        """
        try:
            # Create descriptive title
            title = product_data["title"]
            if len(title) > 50:
                title = title[:47] + "..."
            
            # Add key metrics to title
            if product_data.get("price"):
                title += f" - ${product_data['price']}"
            if product_data.get("rating"):
                title += f" - {product_data['rating']}⭐"
            
            # Determine emoji based on opportunity score
            opportunity = product_data.get("opportunity_score", 0)
            if opportunity >= 8:
                emoji = "🔥"  # Hot opportunity
            elif opportunity >= 6:
                emoji = "✨"  # Good opportunity
            elif opportunity >= 4:
                emoji = "📦"  # Average product
            else:
                emoji = "🛍️"  # Default product
            
            response = self.client.bookmarks_add(
                channel_id=channel_id,
                title=title,
                type="link",
                link=product_data["url"],
                emoji=emoji,
                entity_id=f"product_{product_data['asin']}"
            )
            
            return response.get("bookmark")
            
        except SlackApiError as e:
            logger.error(f"Error adding product bookmark: {e.response['error']}")
            return None
    
    def add_research_bookmark(self, channel_id: str, research_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add a research report or analysis as a bookmark"""
        try:
            research_types = {
                "market_analysis": "📊",
                "competitor_report": "🎯",
                "keyword_research": "🔍",
                "sales_forecast": "📈",
                "product_validation": "✅",
                "trend_analysis": "📉"
            }
            
            research_type = research_data.get("type", "general")
            emoji = research_types.get(research_type, "📋")
            
            # Add date to title
            date_str = datetime.now().strftime("%m/%d")
            title = f"{research_data['title']} - {date_str}"
            
            response = self.client.bookmarks_add(
                channel_id=channel_id,
                title=title,
                type="link",
                link=research_data["url"],
                emoji=emoji,
                entity_id=f"research_{research_data.get('id', '')}"
            )
            
            return response.get("bookmark")
            
        except SlackApiError as e:
            logger.error(f"Error adding research bookmark: {e.response['error']}")
            return None
    
    def create_market_resource_bookmarks(self, channel_id: str) -> List[Dict[str, Any]]:
        """Create default bookmarks for market research resources"""
        resources = [
            {
                "title": "Amazon Best Sellers",
                "url": "https://www.amazon.com/Best-Sellers/zgbs",
                "emoji": "🏆",
                "entity_id": "amazon_bestsellers"
            },
            {
                "title": "Amazon New Releases",
                "url": "https://www.amazon.com/gp/new-releases",
                "emoji": "🆕",
                "entity_id": "amazon_new"
            },
            {
                "title": "Amazon Movers & Shakers",
                "url": "https://www.amazon.com/gp/movers-and-shakers",
                "emoji": "📈",
                "entity_id": "amazon_movers"
            },
            {
                "title": "Jungle Scout Academy",
                "url": "https://www.junglescout.com/academy",
                "emoji": "🎓",
                "entity_id": "js_academy"
            },
            {
                "title": "FBA Calculator",
                "url": "https://sellercentral.amazon.com/fba/profitabilitycalculator",
                "emoji": "🧮",
                "entity_id": "fba_calc"
            },
            {
                "title": "Seller Central",
                "url": "https://sellercentral.amazon.com",
                "emoji": "💼",
                "entity_id": "seller_central"
            }
        ]
        
        created_bookmarks = []
        for resource in resources:
            try:
                response = self.client.bookmarks_add(
                    channel_id=channel_id,
                    title=resource["title"],
                    type="link",
                    link=resource["url"],
                    emoji=resource["emoji"],
                    entity_id=resource["entity_id"]
                )
                if response.get("bookmark"):
                    created_bookmarks.append(response["bookmark"])
            except SlackApiError as e:
                logger.error(f"Error adding resource bookmark: {e}")
        
        return created_bookmarks
    
    def create_watchlist_bookmark(self, channel_id: str, watchlist_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a bookmark for a product watchlist"""
        try:
            # Create watchlist title with product count
            product_count = len(watchlist_data.get("products", []))
            title = f"{watchlist_data['name']} ({product_count} products)"
            
            response = self.client.bookmarks_add(
                channel_id=channel_id,
                title=title,
                type="link",
                link=watchlist_data["url"],
                emoji="👁️",
                entity_id=f"watchlist_{watchlist_data['id']}"
            )
            
            return response.get("bookmark")
            
        except SlackApiError as e:
            logger.error(f"Error adding watchlist bookmark: {e.response['error']}")
            return None
    
    def get_product_bookmarks(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get all product-related bookmarks from a channel"""
        try:
            response = self.client.bookmarks_list(channel_id=channel_id)
            all_bookmarks = response.get("bookmarks", [])
            
            # Filter product bookmarks
            product_bookmarks = []
            product_emojis = ["🔥", "✨", "📦", "🛍️", "🏆", "👁️"]
            
            for bookmark in all_bookmarks:
                # Check if it's a product bookmark
                if (bookmark.get("entity_id", "").startswith("product_") or
                    bookmark.get("emoji") in product_emojis or
                    "amazon.com" in bookmark.get("link", "")):
                    product_bookmarks.append(bookmark)
            
            return product_bookmarks
            
        except SlackApiError as e:
            logger.error(f"Error getting product bookmarks: {e.response['error']}")
            return []
    
    def organize_research_bookmarks(self, channel_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Organize research bookmarks by type"""
        try:
            response = self.client.bookmarks_list(channel_id=channel_id)
            all_bookmarks = response.get("bookmarks", [])
            
            organized = {
                "Hot Products": [],      # 🔥
                "Good Opportunities": [],  # ✨
                "Tracked Products": [],   # 👁️
                "Market Analysis": [],    # 📊
                "Research Reports": [],   # 📋
                "Resources": []          # 🎓, 🧮, 💼
            }
            
            emoji_to_category = {
                "🔥": "Hot Products",
                "✨": "Good Opportunities",
                "👁️": "Tracked Products",
                "📊": "Market Analysis",
                "📈": "Market Analysis",
                "📉": "Market Analysis",
                "📋": "Research Reports",
                "🎯": "Research Reports",
                "🔍": "Research Reports",
                "✅": "Research Reports",
                "🎓": "Resources",
                "🧮": "Resources",
                "💼": "Resources",
                "🏆": "Resources",
                "🆕": "Resources"
            }
            
            for bookmark in all_bookmarks:
                emoji = bookmark.get("emoji")
                if emoji in emoji_to_category:
                    category = emoji_to_category[emoji]
                    organized[category].append(bookmark)
            
            # Remove empty categories
            return {k: v for k, v in organized.items() if v}
            
        except SlackApiError as e:
            logger.error(f"Error organizing bookmarks: {e.response['error']}")
            return {}


def create_product_bookmarks_blocks(bookmarks: List[Dict[str, Any]], 
                                  channel_id: str) -> List[Dict[str, Any]]:
    """Create blocks for product bookmarks interface"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🛍️ Product Research Bookmarks"
            }
        }
    ]
    
    if not bookmarks:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No product bookmarks found. Start tracking products to see them here!"
            }
        })
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add Resources"
                    },
                    "action_id": f"add_market_resources_{channel_id}",
                    "style": "primary"
                }
            ]
        })
        return blocks
    
    # Organize by opportunity level
    hot_products = []
    good_products = []
    tracked_products = []
    other_products = []
    
    for bookmark in bookmarks:
        emoji = bookmark.get("emoji", "🛍️")
        if emoji == "🔥":
            hot_products.append(bookmark)
        elif emoji == "✨":
            good_products.append(bookmark)
        elif emoji == "👁️":
            tracked_products.append(bookmark)
        else:
            other_products.append(bookmark)
    
    # Display hot products first
    if hot_products:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🔥 *Hot Opportunities ({len(hot_products)})*"
            }
        })
        
        for bookmark in hot_products[:3]:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{bookmark['link']}|{bookmark['title']}>"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Analyze"
                    },
                    "action_id": f"analyze_bookmark_{bookmark['id']}",
                    "value": bookmark['link']
                }
            })
    
    # Display good opportunities
    if good_products:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✨ *Good Opportunities ({len(good_products)})*"
            }
        })
        
        for bookmark in good_products[:2]:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{bookmark['link']}|{bookmark['title']}>"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View"
                    },
                    "url": bookmark['link']
                }
            })
    
    # Show tracked products count
    if tracked_products:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"👁️ *Tracking {len(tracked_products)} products*"
            }
        })
    
    blocks.append({"type": "divider"})
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Add Product"
                },
                "action_id": f"add_product_bookmark_{channel_id}",
                "style": "primary"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View All"
                },
                "action_id": f"view_all_bookmarks_{channel_id}"
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Export List"
                },
                "action_id": f"export_bookmarks_{channel_id}"
            }
        ]
    })
    
    return blocks


def create_add_product_bookmark_modal(channel_id: str) -> Dict[str, Any]:
    """Create modal for adding a product bookmark"""
    return {
        "type": "modal",
        "callback_id": "add_product_bookmark_modal",
        "title": {
            "type": "plain_text",
            "text": "Add Product Bookmark"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "private_metadata": channel_id,
        "blocks": [
            {
                "type": "input",
                "block_id": "product_url",
                "element": {
                    "type": "url_text_input",
                    "action_id": "url_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "https://amazon.com/dp/..."
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Amazon Product URL"
                }
            },
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
                    "text": "ASIN (optional)"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "opportunity_score",
                "element": {
                    "type": "number_input",
                    "action_id": "score_input",
                    "is_decimal_allowed": True,
                    "min_value": "0",
                    "max_value": "10",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "7.5"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Opportunity Score (0-10)"
                },
                "optional": True
            },
            {
                "type": "input",
                "block_id": "notes",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "notes_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Why is this product interesting?"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Notes"
                },
                "optional": True
            }
        ]
    }
}