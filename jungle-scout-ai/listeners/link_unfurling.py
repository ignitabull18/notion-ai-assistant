"""
Link Unfurling for Jungle Scout AI Assistant
Provides rich previews for Amazon product links
"""
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from slack_bolt import App
from slack_sdk.web import WebClient

from jungle_scout_ai.logging import logger


class AmazonLinkUnfurler:
    """Handles link unfurling for Amazon product URLs"""
    
    def __init__(self, client: WebClient):
        self.client = client
        self.amazon_domains = [
            'amazon.com', 'amazon.co.uk', 'amazon.ca', 'amazon.de', 
            'amazon.fr', 'amazon.es', 'amazon.it', 'amazon.co.jp',
            'amazon.in', 'amazon.com.mx', 'amazon.com.br', 'amazon.com.au'
        ]
    
    def register_handlers(self, app: App):
        """Register link unfurling event handlers"""
        app.event("link_shared")(self.handle_link_shared)
    
    def handle_link_shared(self, event: Dict[str, Any], client: WebClient):
        """Handle link_shared events for Amazon URLs"""
        try:
            unfurls = {}
            
            for link in event.get("links", []):
                url = link.get("url", "")
                domain = urlparse(url).netloc.lower()
                
                # Remove www. prefix
                if domain.startswith('www.'):
                    domain = domain[4:]
                
                # Check if it's an Amazon URL
                if any(amazon_domain in domain for amazon_domain in self.amazon_domains):
                    unfurl = self._unfurl_amazon_link(url)
                    if unfurl:
                        unfurls[url] = unfurl
            
            # Send unfurls if any were generated
            if unfurls:
                client.chat_unfurl(
                    channel=event["channel"],
                    ts=event["message_ts"],
                    unfurls=unfurls
                )
                
        except Exception as e:
            logger.error(f"Error unfurling Amazon links: {e}")
    
    def _unfurl_amazon_link(self, url: str) -> Optional[Dict[str, Any]]:
        """Create rich unfurl for Amazon product links"""
        # Extract ASIN from URL
        asin = self._extract_asin(url)
        
        if not asin:
            return self._create_generic_amazon_unfurl(url)
        
        return self._create_product_unfurl(url, asin)
    
    def _extract_asin(self, url: str) -> Optional[str]:
        """Extract ASIN from Amazon URL"""
        # Various ASIN patterns in Amazon URLs
        patterns = [
            r'/dp/([A-Z0-9]{10})',
            r'/gp/product/([A-Z0-9]{10})',
            r'/exec/obidos/ASIN/([A-Z0-9]{10})',
            r'/o/ASIN/([A-Z0-9]{10})',
            r'/gp/aw/d/([A-Z0-9]{10})',
            r'(?:dp|product)/([A-Z0-9]{10})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def _create_product_unfurl(self, url: str, asin: str) -> Dict[str, Any]:
        """Create unfurl for Amazon product"""
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🛍️ Amazon Product*\n"
                                f"ASIN: `{asin}`\n"
                                f"Analyze this product with Jungle Scout AI"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View on Amazon"
                        },
                        "url": url,
                        "action_id": "open_amazon_product"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 Quick Analysis"
                            },
                            "action_id": f"quick_analyze_{asin}",
                            "value": asin,
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔬 Deep Analysis"
                            },
                            "action_id": f"deep_analyze_{asin}",
                            "value": asin
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📈 Track Product"
                            },
                            "action_id": f"track_product_{asin}",
                            "value": asin
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🎯 Keywords"
                            },
                            "action_id": f"analyze_keywords_{asin}",
                            "value": asin
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "💰 Sales Estimate"
                            },
                            "action_id": f"sales_estimate_{asin}",
                            "value": asin
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🏆 Competitors"
                            },
                            "action_id": f"find_competitors_{asin}",
                            "value": asin
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📉 Price History"
                            },
                            "action_id": f"price_history_{asin}",
                            "value": asin
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📝 Create Report"
                            },
                            "action_id": f"create_report_{asin}",
                            "value": asin
                        }
                    ]
                }
            ]
        }
    
    def _create_generic_amazon_unfurl(self, url: str) -> Dict[str, Any]:
        """Create generic unfurl for non-product Amazon pages"""
        page_type = "Amazon Page"
        
        if "/s?" in url or "field-keywords" in url:
            page_type = "Search Results"
        elif "/b/" in url or "node=" in url:
            page_type = "Category Page"
        elif "/stores/" in url:
            page_type = "Brand Store"
        
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🛒 Amazon {page_type}*\n"
                                f"Analyze this page with Jungle Scout AI"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open on Amazon"
                        },
                        "url": url,
                        "action_id": "open_amazon_page"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔍 Analyze Page"
                            },
                            "action_id": "analyze_amazon_page",
                            "value": url
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 Extract Products"
                            },
                            "action_id": "extract_products",
                            "value": url
                        }
                    ]
                }
            ]
        }


def register_amazon_link_unfurling(app: App, client: WebClient):
    """Register Amazon link unfurling handlers with the app"""
    unfurler = AmazonLinkUnfurler(client)
    unfurler.register_handlers(app)