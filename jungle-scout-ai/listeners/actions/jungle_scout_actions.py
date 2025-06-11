"""
Action handlers for Jungle Scout AI Assistant interactive components
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any
import json

from listeners.jungle_scout_assistant import jungle_scout_assistant
from listeners.jungle_scout_canvas import JungleScoutCanvasManager
from listeners.jungle_scout_ui import (
    create_product_tracking_modal,
    create_status_blocks
)
from jungle_scout_ai.logging import logger

# Import extended actions
from .jungle_scout_actions_extended import *


def handle_quick_product_research(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle quick product research button click"""
    ack()
    
    try:
        # Open modal for research parameters
        trigger_id = body["trigger_id"]
        
        modal = {
            "type": "modal",
            "callback_id": "product_research_modal",
            "title": {
                "type": "plain_text",
                "text": "🔍 Product Research"
            },
            "submit": {
                "type": "plain_text",
                "text": "Start Research"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "search_query",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "query_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "e.g., wireless earbuds, kitchen gadgets"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Product Keyword or Category"
                    }
                },
                {
                    "type": "input",
                    "block_id": "research_depth",
                    "element": {
                        "type": "radio_buttons",
                        "action_id": "depth_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Quick overview (5 products)"
                                },
                                "value": "quick"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Detailed analysis (15 products)"
                                },
                                "value": "detailed"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Comprehensive report (25+ products)"
                                },
                                "value": "comprehensive"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Research Depth"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=trigger_id,
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening product research modal: {e}")


def handle_create_sales_dashboard(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create sales dashboard button click"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show processing status
        say(blocks=create_status_blocks("processing", "Creating sales dashboard..."))
        
        # Process dashboard creation
        command = "dashboard sales"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error creating sales dashboard: {e}")
        say("❌ Sorry, I couldn't create the sales dashboard right now.")


def handle_analyze_trends(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle analyze trends button click"""
    ack()
    
    try:
        # Open modal for trend analysis parameters
        trigger_id = body["trigger_id"]
        
        modal = {
            "type": "modal",
            "callback_id": "trend_analysis_modal",
            "title": {
                "type": "plain_text",
                "text": "📈 Trend Analysis"
            },
            "submit": {
                "type": "plain_text",
                "text": "Analyze Trends"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "trend_category",
                    "element": {
                        "type": "static_select",
                        "action_id": "category_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a category"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Electronics"
                                },
                                "value": "electronics"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Home & Kitchen"
                                },
                                "value": "home_kitchen"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Health & Fitness"
                                },
                                "value": "health_fitness"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Fashion"
                                },
                                "value": "fashion"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sports & Outdoors"
                                },
                                "value": "sports_outdoors"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Product Category"
                    }
                },
                {
                    "type": "input",
                    "block_id": "trend_timeframe",
                    "element": {
                        "type": "radio_buttons",
                        "action_id": "timeframe_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Last 30 days"
                                },
                                "value": "30_days"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Last 3 months"
                                },
                                "value": "3_months"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Last 12 months"
                                },
                                "value": "12_months"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Analysis Timeframe"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=trigger_id,
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening trend analysis modal: {e}")


def handle_deep_analyze(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle deep analyze product button"""
    ack()
    
    try:
        action = body["actions"][0]
        product_data = json.loads(action["value"])
        asin = product_data.get("asin")
        title = product_data.get("title", "Product")
        
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show processing status
        say(blocks=create_status_blocks("analyzing", f"Deep analyzing {title}..."))
        
        # Process competitor analysis
        command = f"competitor {asin}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in deep analyze: {e}")
        say("❌ Sorry, I couldn't perform the deep analysis right now.")


def handle_track_product(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle track product button"""
    ack()
    
    try:
        trigger_id = body["trigger_id"]
        asin = body["actions"][0]["value"]
        
        # Open product tracking modal with pre-filled ASIN
        modal = create_product_tracking_modal()
        # Pre-fill ASIN if available
        if asin:
            modal["blocks"][0]["element"]["initial_value"] = asin
        
        client.views_open(
            trigger_id=trigger_id,
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening product tracking modal: {e}")


def handle_create_research_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create research canvas button"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        search_query = body["actions"][0]["value"]
        canvas_manager = JungleScoutCanvasManager(client)
        
        # Show creating status
        say(blocks=create_status_blocks("processing", "Creating product research canvas..."))
        
        # Create mock product data for canvas
        mock_products = [
            {
                "title": f"Top {search_query.title()} Product",
                "asin": "B08MOCK123",
                "opportunity_score": 8.5,
                "monthly_revenue": 45000,
                "competition_level": "Medium"
            },
            {
                "title": f"Premium {search_query.title()} Option",
                "asin": "B08MOCK456",
                "opportunity_score": 7.2,
                "monthly_revenue": 32000,
                "competition_level": "High"
            }
        ]
        
        # Create product research canvas
        response = canvas_manager.create_product_research_canvas(
            channel_id=channel_id,
            search_query=search_query,
            products=mock_products,
            market_insights={
                "market_size": "Large",
                "competition_level": "Medium",
                "avg_price": 39.99,
                "trend": "Rising"
            }
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            say(
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📝 Research Canvas Created!"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Product Research: {search_query.title()}*\nCollaborative research canvas with market insights and product opportunities."
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Open Canvas"
                            },
                            "url": canvas_url or "#",
                            "style": "primary"
                        }
                    }
                ]
            )
        else:
            say("❌ Sorry, I couldn't create the research canvas right now.")
            
    except Exception as e:
        logger.error(f"Error creating research canvas: {e}")
        say("❌ Sorry, I couldn't create the research canvas right now.")


def handle_product_research_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle product research modal form submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        
        # Extract form data
        search_query = values["search_query"]["query_input"]["value"]
        research_depth = values["research_depth"]["depth_input"]["selected_option"]["value"]
        
        user_id = body["user"]["id"]
        # Get channel from private_metadata or fallback
        channel_id = body["view"].get("private_metadata") or "general"
        
        # Process product research
        command = f"research {search_query}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error processing product research modal: {e}")
        say("❌ Sorry, I couldn't process the product research right now.")


def handle_trend_analysis_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle trend analysis modal form submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        
        # Extract form data
        category = values["trend_category"]["category_input"]["selected_option"]["value"]
        timeframe = values["trend_timeframe"]["timeframe_input"]["selected_option"]["value"]
        
        user_id = body["user"]["id"]
        channel_id = body["view"].get("private_metadata") or "general"
        
        # Process trend analysis
        command = f"trends {category}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error processing trend analysis modal: {e}")
        say("❌ Sorry, I couldn't process the trend analysis right now.")


def handle_product_tracking_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle product tracking modal form submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        
        # Extract form data
        asin = values["product_asin"]["asin_input"]["value"]
        metrics = [option["value"] for option in values["tracking_metrics"]["metrics_input"]["selected_options"]]
        frequency = values["alert_frequency"]["frequency_input"]["selected_option"]["value"]
        
        # Confirm tracking setup
        say(
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Product Tracking Activated"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*ASIN:* `{asin}`\n"
                               f"*Metrics:* {', '.join(metrics)}\n"
                               f"*Frequency:* {frequency.title()}\n\n"
                               f"You'll receive alerts based on your selected frequency."
                    }
                }
            ]
        )
        
    except Exception as e:
        logger.error(f"Error processing product tracking modal: {e}")
        say("❌ Sorry, I couldn't set up product tracking right now.")


def handle_quick_analyze_from_unfurl(ack, body, say, client, logger):
    """Handle quick analysis from link unfurl"""
    ack()
    
    try:
        asin = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Show processing status
        say(blocks=create_status_blocks("processing", f"Analyzing product {asin}..."))
        
        # Process with assistant
        command = f"analyze {asin}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in quick analysis: {e}")
        say("❌ Sorry, I couldn't analyze the product.")


def handle_analyze_keywords_from_unfurl(ack, body, say, client, logger):
    """Handle keyword analysis from link unfurl"""
    ack()
    
    try:
        asin = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Show processing status
        say(blocks=create_status_blocks("processing", f"Analyzing keywords for {asin}..."))
        
        # Process with assistant
        command = f"keywords for {asin}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in keyword analysis: {e}")
        say("❌ Sorry, I couldn't analyze keywords.")


def handle_sales_estimate_from_unfurl(ack, body, say, client, logger):
    """Handle sales estimate from link unfurl"""
    ack()
    
    try:
        asin = body["actions"][0]["value"]
        
        # Show mock sales estimate (in production, would call real API)
        say(blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💰 Sales Estimate for {asin}*\n\n"
                            f"• Monthly Sales: ~1,500 units\n"
                            f"• Monthly Revenue: ~$45,000\n"
                            f"• Daily Average: ~50 units\n"
                            f"• Best Seller Rank: #1,234 in category"
                }
            }
        ])
        
    except Exception as e:
        logger.error(f"Error in sales estimate: {e}")
        say("❌ Sorry, I couldn't estimate sales.")


def handle_find_competitors_from_unfurl(ack, body, say, client, logger):
    """Handle find competitors from link unfurl"""
    ack()
    
    try:
        asin = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Process with assistant
        command = f"competitor {asin}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error finding competitors: {e}")
        say("❌ Sorry, I couldn't find competitors.")


def handle_create_report_from_unfurl(ack, body, say, client, logger):
    """Handle create report from link unfurl"""
    ack()
    
    try:
        asin = body["actions"][0]["value"]
        channel_id = body["channel"]["id"]
        
        # Create a research canvas
        canvas_manager = JungleScoutCanvasManager(client)
        
        # Mock product data for demo
        products = [{
            "asin": asin,
            "title": "Product from Link",
            "opportunity_score": 8,
            "monthly_revenue": 50000
        }]
        
        response = canvas_manager.create_product_research_canvas(
            channel_id=channel_id,
            search_query=f"Analysis of {asin}",
            products=products
        )
        
        if response:
            say("📝 Created research report canvas!")
        
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        say("❌ Sorry, I couldn't create the report.")


def handle_show_workflows(ack, body, say, client, logger):
    """Handle show workflows button click"""
    ack()
    
    try:
        from listeners.workflow_manager import JungleScoutWorkflowManager
        from listeners.jungle_scout_ui import create_workflow_template_blocks
        
        workflow_manager = JungleScoutWorkflowManager()
        workflows = workflow_manager.list_workflows()
        
        blocks = create_workflow_template_blocks(workflows)
        say(blocks=blocks)
        
    except Exception as e:
        logger.error(f"Error showing workflows: {e}")
        say("❌ Sorry, I couldn't load the workflow templates.")


def handle_use_workflow_template(ack, body, say, client, logger):
    """Handle workflow template selection"""
    ack()
    
    try:
        from listeners.workflow_manager import JungleScoutWorkflowManager
        from listeners.jungle_scout_ui import create_workflow_status_blocks
        from listeners.jungle_scout_assistant import JungleScoutAssistant
        
        template_id = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Show initial status
        say(text="Starting workflow execution...")
        
        # Execute workflow
        workflow_manager = JungleScoutWorkflowManager()
        context = {
            "user_id": user_id,
            "channel_id": channel_id,
            "trigger": "manual"
        }
        
        # Run workflow asynchronously
        import asyncio
        
        assistant = JungleScoutAssistant()
        
        result = asyncio.run(
            workflow_manager.execute_workflow(
                template_id,
                context,
                assistant
            )
        )
        
        # Show status
        status = workflow_manager.get_workflow_status(template_id)
        if status:
            blocks = create_workflow_status_blocks(status)
            say(blocks=blocks)
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        say("❌ Sorry, the workflow execution failed.")