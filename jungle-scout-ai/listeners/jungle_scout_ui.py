"""
Jungle Scout UI Components with 2024 Slack AI Assistant Features
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


def create_jungle_scout_welcome_blocks() -> List[Dict[str, Any]]:
    """Create rich welcome message for Jungle Scout AI Assistant"""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🌲 Jungle Scout AI Assistant"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Welcome to your AI-powered Amazon selling assistant! I can help you discover profitable products, analyze competitors, and track market trends."
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*🔍 Product Research*\nFind high-opportunity products"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📊 Sales Analytics*\nTrack performance metrics"
                },
                {
                    "type": "mrkdwn",
                    "text": "*🎯 Keyword Analysis*\nOptimize SEO strategies"
                },
                {
                    "type": "mrkdwn",
                    "text": "*🔬 Competitor Intel*\nAnalyze market competition"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📈 Market Trends*\nSpot emerging opportunities"
                },
                {
                    "type": "mrkdwn",
                    "text": "*✅ Product Validation*\nScore opportunity potential"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Find Products"
                    },
                    "action_id": "quick_product_research",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Sales Dashboard"
                    },
                    "action_id": "create_sales_dashboard"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Trend Analysis"
                    },
                    "action_id": "analyze_trends"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔄 Workflows"
                    },
                    "action_id": "show_workflows"
                }
            ]
        }
    ]


def create_product_research_blocks(
    products: List[Dict[str, Any]], 
    search_query: str
) -> List[Dict[str, Any]]:
    """Create rich product research results with interactive elements"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔍 Product Research: \"{search_query}\""
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Found {len(products)} product opportunities | 🕒 *Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                }
            ]
        }
    ]
    
    for i, product in enumerate(products[:5]):  # Limit to 5 products
        opportunity_score = product.get('opportunity_score', 0)
        monthly_revenue = product.get('monthly_revenue', 0)
        competition_level = product.get('competition_level', 'Unknown')
        
        # Color code based on opportunity score
        score_color = "🟢" if opportunity_score >= 7 else "🟡" if opportunity_score >= 5 else "🔴"
        
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{product.get('title', 'Product')}*\n"
                           f"{score_color} *Opportunity Score:* {opportunity_score}/10\n"
                           f"💰 *Est. Monthly Revenue:* ${monthly_revenue:,}\n"
                           f"⚔️ *Competition:* {competition_level}\n"
                           f"🏷️ *Price Range:* ${product.get('min_price', 0):.2f} - ${product.get('max_price', 0):.2f}"
                },
                "accessory": {
                    "type": "image",
                    "image_url": product.get('image_url', 'https://via.placeholder.com/75x75?text=📦'),
                    "alt_text": f"Product {i+1}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Deep Analyze"
                        },
                        "action_id": f"deep_analyze_{i}",
                        "value": json.dumps({"asin": product.get('asin'), "title": product.get('title')})
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Track Product"
                        },
                        "action_id": f"track_product_{i}",
                        "value": product.get('asin', '')
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Competitor Analysis"
                        },
                        "action_id": f"competitor_analysis_{i}",
                        "value": product.get('asin', '')
                    }
                ]
            }
        ])
    
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Create Research Canvas"
                    },
                    "action_id": "create_research_canvas",
                    "value": search_query,
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Export Report"
                    },
                    "action_id": "export_research_report"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Set Alerts"
                    },
                    "action_id": "set_product_alerts"
                }
            ]
        }
    ])
    
    return blocks


def create_keyword_analysis_blocks(
    keyword: str,
    metrics: Dict[str, Any],
    related_keywords: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Create keyword analysis results with trend visualization"""
    search_volume = metrics.get('search_volume', 0)
    difficulty = metrics.get('difficulty', 0)
    cpc = metrics.get('cpc', 0)
    trend = metrics.get('trend', 'stable')
    
    # Trend emoji based on direction
    trend_emoji = "📈" if trend == "rising" else "📉" if trend == "falling" else "➡️"
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🎯 Keyword Analysis: \"{keyword}\""
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*🔍 Search Volume*\n{search_volume:,}/month"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*⚔️ Difficulty Score*\n{difficulty}/100"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*💰 Cost Per Click*\n${cpc:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*{trend_emoji} Trend*\n{trend.title()}"
                }
            ]
        }
    ]
    
    if related_keywords:
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔗 Related Keywords:*"
                }
            }
        ])
        
        # Add related keywords in groups
        for i in range(0, len(related_keywords[:10]), 2):
            fields = []
            for j in range(2):
                if i + j < len(related_keywords):
                    kw = related_keywords[i + j]
                    fields.append({
                        "type": "mrkdwn",
                        "text": f"*{kw.get('keyword', 'Unknown')}*\n{kw.get('volume', 0):,} searches"
                    })
            
            if fields:
                blocks.append({
                    "type": "section",
                    "fields": fields
                })
    
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Track Keyword"
                    },
                    "action_id": "track_keyword",
                    "value": keyword
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "SEO Strategy Canvas"
                    },
                    "action_id": "create_seo_canvas",
                    "value": keyword,
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Find Products"
                    },
                    "action_id": "find_products_for_keyword",
                    "value": keyword
                }
            ]
        }
    ])
    
    return blocks


def create_sales_dashboard_blocks(
    metrics: Dict[str, Any],
    timeframe: str = "last 30 days"
) -> List[Dict[str, Any]]:
    """Create sales performance dashboard"""
    total_revenue = metrics.get('total_revenue', 0)
    total_units = metrics.get('total_units', 0)
    avg_order_value = metrics.get('avg_order_value', 0)
    conversion_rate = metrics.get('conversion_rate', 0)
    top_products = metrics.get('top_products', [])
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Sales Dashboard - {timeframe.title()}"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*💰 Total Revenue*\n${total_revenue:,.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*📦 Units Sold*\n{total_units:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*🛒 Avg Order Value*\n${avg_order_value:.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*🎯 Conversion Rate*\n{conversion_rate:.1f}%"
                }
            ]
        }
    ]
    
    if top_products:
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🏆 Top Performing Products:*"
                }
            }
        ])
        
        for i, product in enumerate(top_products[:3], 1):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*#{i} {product.get('name', 'Product')}*\n"
                           f"💰 ${product.get('revenue', 0):,.2f} | "
                           f"📦 {product.get('units', 0):,} units"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Analyze"
                    },
                    "action_id": f"analyze_product_{i}",
                    "value": product.get('asin', '')
                }
            })
    
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Create Report Canvas"
                    },
                    "action_id": "create_sales_canvas",
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Set Performance Alerts"
                    },
                    "action_id": "set_sales_alerts"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Forecast Trends"
                    },
                    "action_id": "forecast_sales"
                }
            ]
        }
    ])
    
    return blocks


def create_competitor_analysis_blocks(
    competitor: Dict[str, Any],
    comparison_metrics: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Create competitor analysis with comparison data"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔬 Competitor Analysis: {competitor.get('brand', 'Unknown Brand')}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Product:* {competitor.get('title', 'N/A')}\n"
                       f"*ASIN:* `{competitor.get('asin', 'N/A')}`\n"
                       f"*Rating:* ⭐ {competitor.get('rating', 0):.1f} ({competitor.get('review_count', 0):,} reviews)"
            },
            "accessory": {
                "type": "image",
                "image_url": competitor.get('image_url', 'https://via.placeholder.com/75x75?text=🏪'),
                "alt_text": "Competitor Product"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*💰 Price*\n${competitor.get('price', 0):.2f}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*📈 Est. Sales*\n{competitor.get('monthly_sales', 0):,}/mo"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*🎯 BSR*\n#{competitor.get('bsr', 'N/A'):,}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*📦 In Stock*\n{competitor.get('stock_level', 'Unknown')}"
                }
            ]
        }
    ]
    
    # Add comparison metrics if available
    if comparison_metrics:
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Market Position Comparison:*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Price vs Market Avg*\n{comparison_metrics.get('price_comparison', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Sales vs Market Avg*\n{comparison_metrics.get('sales_comparison', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Rating vs Market Avg*\n{comparison_metrics.get('rating_comparison', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Market Share*\n{comparison_metrics.get('market_share', 'N/A')}"
                    }
                ]
            }
        ])
    
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Monitor Competitor"
                    },
                    "action_id": "monitor_competitor",
                    "value": competitor.get('asin', ''),
                    "style": "primary"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Price History"
                    },
                    "action_id": "price_history",
                    "value": competitor.get('asin', '')
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Strategy Canvas"
                    },
                    "action_id": "create_strategy_canvas",
                    "value": competitor.get('asin', '')
                }
            ]
        }
    ])
    
    return blocks


def create_product_tracking_modal() -> Dict[str, Any]:
    """Create modal form for setting up product tracking"""
    return {
        "type": "modal",
        "callback_id": "product_tracking_modal",
        "title": {
            "type": "plain_text",
            "text": "📊 Set Up Product Tracking"
        },
        "submit": {
            "type": "plain_text",
            "text": "Start Tracking"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "product_asin",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "asin_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "e.g., B08N5WRWNW"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Product ASIN"
                }
            },
            {
                "type": "input",
                "block_id": "tracking_metrics",
                "element": {
                    "type": "checkboxes",
                    "action_id": "metrics_input",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Price Changes"
                            },
                            "value": "price"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Sales Rank (BSR)"
                            },
                            "value": "bsr"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Review Count & Rating"
                            },
                            "value": "reviews"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Stock Levels"
                            },
                            "value": "stock"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Sales Estimates"
                            },
                            "value": "sales"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Metrics to Track"
                }
            },
            {
                "type": "input",
                "block_id": "alert_frequency",
                "element": {
                    "type": "radio_buttons",
                    "action_id": "frequency_input",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Real-time alerts"
                            },
                            "value": "realtime"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Daily summary"
                            },
                            "value": "daily"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Weekly report"
                            },
                            "value": "weekly"
                        }
                    ]
                },
                "label": {
                    "type": "plain_text",
                    "text": "Alert Frequency"
                }
            }
        ]
    }


def create_status_blocks(status: str, message: str) -> List[Dict[str, Any]]:
    """Create status blocks for long-running operations"""
    status_emoji = {
        "researching": "🔍",
        "analyzing": "📊",
        "processing": "⚡",
        "tracking": "📈",
        "validating": "✅",
        "complete": "🎉",
        "error": "❌"
    }
    
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{status_emoji.get(status, '🤖')} {message}"
            }
        }
    ]


def get_jungle_scout_suggested_prompts(context: str = "general") -> List[Dict[str, str]]:
    """Get context-appropriate suggested prompts for Jungle Scout"""
    prompts = {
        "general": [
            {"title": "Find trending products", "message": "research wireless earbuds"},
            {"title": "Analyze keyword", "message": "keywords bluetooth speakers"},
            {"title": "Check competitor", "message": "competitor B08N5WRWNW"},
            {"title": "Sales dashboard", "message": "dashboard sales"}
        ],
        "research": [
            {"title": "High-opportunity products", "message": "research kitchen gadgets"},
            {"title": "Validate product idea", "message": "validate ergonomic mouse pad"},
            {"title": "Market size analysis", "message": "trends fitness equipment"},
            {"title": "Competition analysis", "message": "competitor B08N5WRWNW"}
        ],
        "keywords": [
            {"title": "Keyword difficulty", "message": "keywords wireless charger"},
            {"title": "Trending searches", "message": "trends phone accessories"},
            {"title": "SEO opportunities", "message": "keywords gaming chair"},
            {"title": "Search volume data", "message": "keywords coffee maker"}
        ],
        "sales": [
            {"title": "Performance metrics", "message": "sales last 30 days"},
            {"title": "Top products", "message": "dashboard products"},
            {"title": "Revenue trends", "message": "trends revenue this quarter"},
            {"title": "Inventory alerts", "message": "sales inventory status"}
        ]
    }
    
    return prompts.get(context, prompts["general"])


def create_workflow_template_blocks(templates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create blocks for workflow template selection"""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔄 Jungle Scout Workflow Templates"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Select a workflow template to automate your Amazon selling operations:"
            }
        }
    ]
    
    for template in templates:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{template['name']}*\n_{template['description']}_\n📋 {template['steps']} steps"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Use Template"
                },
                "action_id": f"use_workflow_{template['id']}",
                "value": template['id'],
                "style": "primary"
            }
        })
    
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🛠️ Create Custom Workflow"
                },
                "action_id": "create_custom_workflow"
            }
        ]
    })
    
    return blocks


def create_workflow_status_blocks(workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create blocks showing workflow execution status"""
    status_emoji = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫"
    }
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{status_emoji.get(workflow['status'], '📋')} {workflow['name']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Status:* {workflow['status'].title()}\n*Progress:* Step {workflow['current_step'] + 1} of {workflow['total_steps']}"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # Add step details
    for step in workflow['steps']:
        step_emoji = status_emoji.get(step['status'], '○')
        text = f"{step_emoji} *{step['name']}*"
        
        if step['status'] == 'failed' and step.get('error'):
            text += f"\n   ❗ Error: _{step['error']}_"
        elif step['status'] == 'completed':
            text += "\n   ✓ Completed successfully"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        })
    
    # Add actions based on status
    if workflow['status'] == 'running':
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "⏸️ Pause"
                    },
                    "action_id": f"pause_workflow_{workflow['workflow_id']}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🚫 Cancel"
                    },
                    "action_id": f"cancel_workflow_{workflow['workflow_id']}",
                    "style": "danger"
                }
            ]
        })
    elif workflow['status'] == 'completed':
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📄 View Results"
                    },
                    "action_id": f"view_results_{workflow['workflow_id']}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔄 Run Again"
                    },
                    "action_id": f"rerun_workflow_{workflow['workflow_id']}"
                }
            ]
        })
    
    return blocks