"""
App Home tab with interactive dashboards for Jungle Scout AI
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
import json

from utils.logging import logger


class JungleScoutAppHome:
    """Manages App Home tab with dashboards and insights"""
    
    def __init__(self, client: WebClient):
        self.client = client
    
    def publish_home_view(self, user_id: str, view_type: str = "dashboard") -> bool:
        """Publish the App Home view for a user"""
        try:
            if view_type == "dashboard":
                view = self._create_dashboard_view()
            elif view_type == "watchlist":
                view = self._create_watchlist_view()
            elif view_type == "insights":
                view = self._create_insights_view()
            elif view_type == "settings":
                view = self._create_settings_view()
            else:
                view = self._create_dashboard_view()
            
            response = self.client.views_publish(
                user_id=user_id,
                view=view
            )
            
            return response.get("ok", False)
            
        except SlackApiError as e:
            logger.error(f"Error publishing home view: {e}")
            return False
    
    def _create_dashboard_view(self) -> Dict[str, Any]:
        """Create main dashboard view"""
        return {
            "type": "home",
            "blocks": [
                # Header
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🌲 Jungle Scout AI Dashboard"
                    }
                },
                # Navigation tabs
                self._create_navigation_tabs("dashboard"),
                {"type": "divider"},
                
                # Quick stats
                self._create_quick_stats_section(),
                {"type": "divider"},
                
                # Recent activity
                self._create_recent_activity_section(),
                {"type": "divider"},
                
                # Top opportunities
                self._create_top_opportunities_section(),
                {"type": "divider"},
                
                # Quick actions
                self._create_quick_actions_section()
            ]
        }
    
    def _create_watchlist_view(self) -> Dict[str, Any]:
        """Create watchlist management view"""
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Product Watchlists"
                    }
                },
                self._create_navigation_tabs("watchlist"),
                {"type": "divider"},
                
                # Watchlist summary
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Your Watchlists*\n"
                               "Track product prices, rankings, and opportunities in real-time."
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "➕ New Watchlist"
                        },
                        "style": "primary",
                        "action_id": "create_watchlist"
                    }
                },
                
                # Active watchlists
                self._create_watchlist_cards(),
                
                # Price alerts
                {"type": "divider"},
                self._create_price_alerts_section()
            ]
        }
    
    def _create_insights_view(self) -> Dict[str, Any]:
        """Create market insights view"""
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "💡 Market Insights"
                    }
                },
                self._create_navigation_tabs("insights"),
                {"type": "divider"},
                
                # Trending categories
                self._create_trending_categories_section(),
                {"type": "divider"},
                
                # Emerging keywords
                self._create_emerging_keywords_section(),
                {"type": "divider"},
                
                # Market opportunities
                self._create_market_opportunities_section()
            ]
        }
    
    def _create_settings_view(self) -> Dict[str, Any]:
        """Create settings view"""
        return {
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚙️ Settings & Preferences"
                    }
                },
                self._create_navigation_tabs("settings"),
                {"type": "divider"},
                
                # Notification preferences
                self._create_notification_settings(),
                {"type": "divider"},
                
                # API connections
                self._create_api_settings(),
                {"type": "divider"},
                
                # Data preferences
                self._create_data_preferences()
            ]
        }
    
    def _create_navigation_tabs(self, active_tab: str) -> Dict[str, Any]:
        """Create navigation tabs"""
        elements = []
        tabs = [
            ("dashboard", "📊 Dashboard"),
            ("watchlist", "📋 Watchlists"),
            ("insights", "💡 Insights"),
            ("settings", "⚙️ Settings")
        ]
        
        for tab_id, label in tabs:
            style = "primary" if tab_id == active_tab else None
            elements.append({
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": label
                },
                "action_id": f"nav_{tab_id}",
                "style": style
            })
        
        return {
            "type": "actions",
            "elements": elements
        }
    
    def _create_quick_stats_section(self) -> Dict[str, Any]:
        """Create quick stats section"""
        return {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*📦 Products Tracked*\n247"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📈 Avg. Opportunity Score*\n7.8/10"
                },
                {
                    "type": "mrkdwn",
                    "text": "*💰 Total Market Value*\n$1.2M"
                },
                {
                    "type": "mrkdwn",
                    "text": "*🔔 Active Alerts*\n12"
                },
                {
                    "type": "mrkdwn",
                    "text": "*🎯 Keywords Monitored*\n156"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📊 Win Rate*\n68%"
                }
            ]
        }
    
    def _create_recent_activity_section(self) -> Dict[str, Any]:
        """Create recent activity feed"""
        activities = [
            "🔴 *Price Drop Alert*: _Wireless Earbuds Pro_ dropped to $24.99 (-15%)",
            "🟢 *New Opportunity*: _Smart Home Security_ scored 9.2/10",
            "📈 *Rank Improved*: _Fitness Tracker Band_ moved to #127 (+45 positions)",
            "🎯 *Keyword Trending*: _sustainable kitchen products_ +230% search volume"
        ]
        
        activity_text = "\n".join(activities)
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🕐 Recent Activity*\n{activity_text}"
            }
        }
    
    def _create_top_opportunities_section(self) -> Dict[str, Any]:
        """Create top opportunities section"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🎯 Top Opportunities This Week*"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View All"
                },
                "action_id": "view_all_opportunities"
            }
        }
    
    def _create_quick_actions_section(self) -> Dict[str, Any]:
        """Create quick actions grid"""
        return {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔍 Product Research"
                    },
                    "action_id": "quick_research",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Sales Dashboard"
                    },
                    "action_id": "quick_dashboard"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📈 Market Trends"
                    },
                    "action_id": "quick_trends"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🎯 Keyword Analysis"
                    },
                    "action_id": "quick_keywords"
                }
            ]
        }
    
    def _create_watchlist_cards(self) -> List[Dict[str, Any]]:
        """Create watchlist cards"""
        blocks = []
        
        # Example watchlists
        watchlists = [
            {
                "name": "🔥 Hot Products",
                "count": 15,
                "alerts": 3,
                "last_update": "2 hours ago"
            },
            {
                "name": "🎯 Competition Tracker",
                "count": 8,
                "alerts": 1,
                "last_update": "30 min ago"
            },
            {
                "name": "📈 Trending Items",
                "count": 22,
                "alerts": 5,
                "last_update": "1 hour ago"
            }
        ]
        
        for wl in watchlists:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{wl['name']}*\n"
                           f"📦 {wl['count']} products | "
                           f"🔔 {wl['alerts']} alerts | "
                           f"🕐 Updated {wl['last_update']}"
                },
                "accessory": {
                    "type": "overflow",
                    "action_id": f"watchlist_menu_{wl['name']}",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "👁️ View List"
                            },
                            "value": "view"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "➕ Add Products"
                            },
                            "value": "add"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "🔔 Configure Alerts"
                            },
                            "value": "alerts"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "📊 Export Data"
                            },
                            "value": "export"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "🗑️ Delete List"
                            },
                            "value": "delete"
                        }
                    ]
                }
            })
        
        return blocks
    
    def _create_price_alerts_section(self) -> Dict[str, Any]:
        """Create price alerts configuration"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔔 Price Alert Settings*\n"
                       "Get notified when products hit your target prices"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Configure Alerts"
                },
                "action_id": "configure_price_alerts"
            }
        }
    
    def _create_trending_categories_section(self) -> Dict[str, Any]:
        """Create trending categories section"""
        categories = [
            ("Home & Kitchen", "+45%", "🟢"),
            ("Electronics", "+32%", "🟢"),
            ("Health & Fitness", "+28%", "🟢"),
            ("Pet Supplies", "-12%", "🔴"),
            ("Toys & Games", "+15%", "🟡")
        ]
        
        fields = []
        for cat, change, indicator in categories:
            fields.append({
                "type": "mrkdwn",
                "text": f"{indicator} *{cat}*\n{change} this month"
            })
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📈 Trending Categories*"
            },
            "fields": fields[:4]  # Limit to 4 for layout
        }
    
    def _create_emerging_keywords_section(self) -> Dict[str, Any]:
        """Create emerging keywords section"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🚀 Emerging Keywords*\n"
                       "• `eco friendly kitchen` (+450% volume)\n"
                       "• `smart home security 2024` (+380% volume)\n"
                       "• `portable air purifier` (+290% volume)\n"
                       "• `wireless charging station` (+220% volume)"
            }
        }
    
    def _create_market_opportunities_section(self) -> Dict[str, Any]:
        """Create market opportunities with charts"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💎 Market Opportunities*\n"
                       "AI-identified gaps with high profit potential"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Explore All"
                },
                "action_id": "explore_opportunities",
                "style": "primary"
            }
        }
    
    def _create_notification_settings(self) -> Dict[str, Any]:
        """Create notification preferences"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔔 Notification Preferences*"
            },
            "accessory": {
                "type": "checkboxes",
                "action_id": "notification_prefs",
                "options": [
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "Price drop alerts"
                        },
                        "value": "price_drops"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "New opportunities (8+ score)"
                        },
                        "value": "opportunities"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "Competitor changes"
                        },
                        "value": "competitors"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "Keyword trends"
                        },
                        "value": "keywords"
                    }
                ],
                "initial_options": [
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "Price drop alerts"
                        },
                        "value": "price_drops"
                    },
                    {
                        "text": {
                            "type": "mrkdwn",
                            "text": "New opportunities (8+ score)"
                        },
                        "value": "opportunities"
                    }
                ]
            }
        }
    
    def _create_api_settings(self) -> Dict[str, Any]:
        """Create API connection settings"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔌 API Connections*\n"
                       "✅ Jungle Scout API: Connected\n"
                       "✅ Composio: Active\n"
                       "✅ LiteLLM: Configured"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Manage APIs"
                },
                "action_id": "manage_apis"
            }
        }
    
    def _create_data_preferences(self) -> Dict[str, Any]:
        """Create data preferences section"""
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📊 Data Preferences*"
            },
            "accessory": {
                "type": "static_select",
                "action_id": "data_refresh_rate",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Refresh Rate"
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Real-time"
                        },
                        "value": "realtime"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Every hour"
                        },
                        "value": "hourly"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Every 6 hours"
                        },
                        "value": "6hours"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Daily"
                        },
                        "value": "daily"
                    }
                ],
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "Every hour"
                    },
                    "value": "hourly"
                }
            }
        }


# Handle App Home interactions
def handle_app_home_opened(event: Dict[str, Any], client: WebClient):
    """Handle app_home_opened event"""
    try:
        user_id = event["user"]
        app_home = JungleScoutAppHome(client)
        app_home.publish_home_view(user_id)
    except Exception as e:
        logger.error(f"Error handling app home opened: {e}")


def handle_home_tab_navigation(ack, body: Dict[str, Any], client: WebClient):
    """Handle navigation between home tabs"""
    ack()
    
    try:
        action_id = body["actions"][0]["action_id"]
        tab = action_id.replace("nav_", "")
        user_id = body["user"]["id"]
        
        app_home = JungleScoutAppHome(client)
        app_home.publish_home_view(user_id, tab)
        
    except Exception as e:
        logger.error(f"Error handling home tab navigation: {e}")