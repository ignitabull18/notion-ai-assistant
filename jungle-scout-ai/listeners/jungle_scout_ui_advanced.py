"""
Advanced UI Components for Jungle Scout AI Assistant with rich blocks and inputs
"""
from typing import List, Dict, Any, Optional


def create_advanced_product_analysis_form() -> List[Dict[str, Any]]:
    """Create advanced form for product analysis with all input types"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔍 Advanced Product Analysis"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Analyze products with ",
                            "style": {"bold": True}
                        },
                        {
                            "type": "text",
                            "text": "AI-powered insights",
                            "style": {"italic": True, "bold": True}
                        },
                        {
                            "type": "text",
                            "text": " and "
                        },
                        {
                            "type": "text",
                            "text": "real-time data",
                            "style": {"code": True}
                        }
                    ]
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "input",
            "block_id": "amazon_url",
            "element": {
                "type": "url_text_input",
                "action_id": "amazon_url_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "https://amazon.com/dp/B08N5WRWNW"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "🛍️ Amazon Product URL"
            }
        },
        {
            "type": "input",
            "block_id": "target_price",
            "element": {
                "type": "number_input",
                "action_id": "price_input",
                "is_decimal_allowed": True,
                "min_value": "0.01",
                "max_value": "10000",
                "initial_value": "29.99"
            },
            "label": {
                "type": "plain_text",
                "text": "💵 Target Price Point"
            }
        },
        {
            "type": "input",
            "block_id": "min_rating",
            "element": {
                "type": "number_input",
                "action_id": "rating_input",
                "is_decimal_allowed": True,
                "min_value": "1",
                "max_value": "5",
                "initial_value": "4.0"
            },
            "label": {
                "type": "plain_text",
                "text": "⭐ Minimum Rating"
            }
        },
        {
            "type": "input",
            "block_id": "supplier_email",
            "element": {
                "type": "email_text_input",
                "action_id": "supplier_email_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "supplier@manufacturer.com"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "📧 Supplier Contact Email"
            },
            "optional": True
        },
        {
            "type": "input",
            "block_id": "analysis_schedule",
            "element": {
                "type": "timepicker",
                "action_id": "schedule_time",
                "initial_time": "09:00",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Daily analysis time"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "⏰ Daily Analysis Schedule"
            },
            "optional": True
        }
    ]


def create_market_trends_visualization() -> List[Dict[str, Any]]:
    """Create rich visualization for market trends"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📈 Market Trends Analysis"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Category: ",
                            "style": {"bold": True}
                        },
                        {
                            "type": "text",
                            "text": "Wireless Earbuds",
                            "style": {"code": True}
                        }
                    ]
                },
                {
                    "type": "rich_text_list",
                    "style": "ordered",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Market Size: ",
                                    "style": {"bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": "$2.3B",
                                    "style": {"code": True, "bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": " (↑ 23% YoY)"
                                }
                            ]
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Competition: ",
                                    "style": {"bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": "HIGH",
                                    "style": {"code": True, "bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": " (1,234 sellers)"
                                }
                            ]
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "text": "Avg Price: ",
                                    "style": {"bold": True}
                                },
                                {
                                    "type": "text",
                                    "text": "$49.99",
                                    "style": {"code": True}
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "rich_text_quote",
                    "elements": [
                        {
                            "type": "text",
                            "text": "💡 Opportunity Score: 8.5/10",
                            "style": {"bold": True}
                        },
                        {
                            "type": "text",
                            "text": " - High demand with room for differentiation"
                        }
                    ]
                }
            ]
        }
    ]


def create_competitor_analysis_matrix() -> List[Dict[str, Any]]:
    """Create a competitor analysis matrix with rich formatting"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🎯 Competitor Analysis Matrix"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_preformatted",
                    "elements": [
                        {
                            "type": "text",
                            "text": "┌─────────────┬───────┬────────┬─────────┐\n│ Competitor  │ Price │ Rating │ Revenue │\n├─────────────┼───────┼────────┼─────────┤\n│ Brand A     │ $39   │ 4.5⭐  │ $125K   │\n│ Brand B     │ $49   │ 4.3⭐  │ $98K    │\n│ Your Product│ $45   │ 4.6⭐  │ $0      │\n└─────────────┴───────┴────────┴─────────┘"
                        }
                    ]
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Key Differentiators to Consider:*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "💰 Price Strategy"},
                    "action_id": "price_strategy",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🌟 Quality Focus"},
                    "action_id": "quality_focus"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🚀 Feature Innovation"},
                    "action_id": "feature_innovation"
                }
            ]
        }
    ]


def create_sales_forecast_dashboard() -> List[Dict[str, Any]]:
    """Create a sales forecast dashboard with advanced elements"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "💹 Sales Forecast Dashboard"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Based on ",
                            "style": {"italic": True}
                        },
                        {
                            "type": "text",
                            "text": "AI analysis",
                            "style": {"bold": True, "italic": True}
                        },
                        {
                            "type": "text",
                            "text": " of similar products:"
                        }
                    ]
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Month 1*\n`50-100 units`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Month 3*\n`200-400 units`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Month 6*\n`500-800 units`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Year 1*\n`$125K-$250K`"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "📊 *Confidence Level:* 85% | 🔄 *Last Updated:* Just now"
                }
            ]
        }
    ]


def create_product_research_video_block() -> Dict[str, Any]:
    """Create a video block for product research tutorials"""
    return {
        "type": "video",
        "title": {
            "type": "plain_text",
            "text": "Amazon FBA Product Research Masterclass"
        },
        "title_url": "https://junglescout.com/academy",
        "description": {
            "type": "plain_text",
            "text": "Learn advanced product research techniques"
        },
        "video_url": "https://www.youtube.com/embed/product-research-tutorial",
        "alt_text": "Product research tutorial",
        "thumbnail_url": "https://junglescout.com/tutorial-thumb.jpg",
        "author_name": "Jungle Scout",
        "provider_name": "YouTube"
    }
}


def create_profit_calculator_form() -> List[Dict[str, Any]]:
    """Create an advanced profit calculator form"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "💰 FBA Profit Calculator"
            }
        },
        {
            "type": "input",
            "block_id": "product_cost",
            "element": {
                "type": "number_input",
                "action_id": "cost_input",
                "is_decimal_allowed": True,
                "min_value": "0.01",
                "placeholder": {
                    "type": "plain_text",
                    "text": "10.00"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Product Cost"
            }
        },
        {
            "type": "input",
            "block_id": "shipping_cost",
            "element": {
                "type": "number_input",
                "action_id": "shipping_input",
                "is_decimal_allowed": True,
                "min_value": "0",
                "placeholder": {
                    "type": "plain_text",
                    "text": "2.50"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Shipping Cost per Unit"
            }
        },
        {
            "type": "input",
            "block_id": "selling_price",
            "element": {
                "type": "number_input",
                "action_id": "price_input",
                "is_decimal_allowed": True,
                "min_value": "0.01",
                "placeholder": {
                    "type": "plain_text",
                    "text": "29.99"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Selling Price"
            }
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "📊 Estimated Profit Margin: ",
                            "style": {"bold": True}
                        },
                        {
                            "type": "text",
                            "text": "35%",
                            "style": {"code": True, "bold": True}
                        }
                    ]
                }
            ]
        }
    ]
}