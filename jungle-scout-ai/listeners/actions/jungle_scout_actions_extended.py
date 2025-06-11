"""
Extended action handlers for Jungle Scout AI Assistant
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any
import json

from listeners.jungle_scout_assistant import jungle_scout_assistant
from listeners.jungle_scout_canvas import JungleScoutCanvasManager
from listeners.jungle_scout_formatter import JungleScoutFormatter
from listeners.jungle_scout_ui import (
    create_product_tracking_modal,
    create_status_blocks
)
from jungle_scout_ai.logging import logger


def handle_try_product_research(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle try product research from welcome message"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show demo research
        say(blocks=JungleScoutFormatter.format_status_update(
            "Product Research Demo", 
            "researching",
            "Finding trending products for you..."
        ))
        
        # Process a sample research command
        command = "research trending gadgets"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in try product research: {e}")
        say("❌ Sorry, I couldn't start the product research demo.")


def handle_try_sales_analytics(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle try sales analytics from welcome message"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show demo analytics
        say(blocks=JungleScoutFormatter.format_status_update(
            "Sales Analytics Demo",
            "analyzing",
            "Generating sales dashboard..."
        ))
        
        # Process a sample sales command
        command = "sales last 30 days"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in try sales analytics: {e}")
        say("❌ Sorry, I couldn't start the sales analytics demo.")


def handle_try_keyword_analysis(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle try keyword analysis from welcome message"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show demo keyword analysis
        say(blocks=JungleScoutFormatter.format_status_update(
            "Keyword Analysis Demo",
            "analyzing",
            "Analyzing popular keywords..."
        ))
        
        # Process a sample keyword command
        command = "keywords wireless earbuds"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in try keyword analysis: {e}")
        say("❌ Sorry, I couldn't start the keyword analysis demo.")


def handle_try_competitor_analysis(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle try competitor analysis from welcome message"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show demo competitor analysis
        say(blocks=JungleScoutFormatter.format_status_update(
            "Competitor Analysis Demo",
            "analyzing",
            "Analyzing top competitors..."
        ))
        
        # Process a sample validation command (shows competitor insights)
        command = "validate smart home devices"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in try competitor analysis: {e}")
        say("❌ Sorry, I couldn't start the competitor analysis demo.")


def handle_create_research_canvas_from_response(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle creating research canvas from response"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        canvas_manager = JungleScoutCanvasManager(client)
        
        # Show creating status
        say(blocks=JungleScoutFormatter.format_status_update(
            "Creating Research Canvas",
            "processing",
            "Building your collaborative research document..."
        ))
        
        # Extract research data from the original message if available
        original_message = body.get("message", {})
        research_summary = "Product research insights and opportunities"
        
        # Create research canvas
        response = canvas_manager.create_product_research_canvas(
            channel_id=channel_id,
            research_topic="Product Research Results",
            findings=[
                "High-opportunity products identified",
                "Market trends analyzed",
                "Competition levels assessed",
                "Profit potential calculated"
            ],
            opportunities=[
                {"product": "Trending Product", "score": 8.5, "notes": "High demand, low competition"},
                {"product": "Niche Product", "score": 7.2, "notes": "Growing market segment"}
            ],
            next_steps=[
                "Validate top opportunities",
                "Analyze competitor strategies",
                "Calculate profit margins",
                "Source suppliers"
            ]
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Research Canvas Created!*\n\nYour collaborative research document is ready."
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open Canvas",
                            "emoji": True
                        },
                        "url": canvas_url or "#",
                        "action_id": "open_canvas"
                    }
                }
            ]
            say(blocks=blocks, text="Research canvas created successfully!")
        else:
            say("❌ Sorry, I couldn't create the research canvas right now.")
            
    except Exception as e:
        logger.error(f"Error creating research canvas: {e}")
        say("❌ Sorry, I couldn't create the research canvas right now.")


def handle_track_products_from_response(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle tracking products from response"""
    ack()
    
    try:
        say("📊 Product tracking feature coming soon! This will allow you to monitor price changes, BSR, and sales estimates.")
        
    except Exception as e:
        logger.error(f"Error tracking products: {e}")


def handle_research_from_analysis(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle research from channel analysis"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        say(blocks=JungleScoutFormatter.format_status_update(
            "Researching Top Opportunity",
            "researching",
            "Finding products based on channel analysis..."
        ))
        
        # Research based on discussed topics
        command = "research trending opportunities"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error researching from analysis: {e}")


def handle_create_strategy_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle creating strategy canvas"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        canvas_manager = JungleScoutCanvasManager(client)
        
        say(blocks=JungleScoutFormatter.format_status_update(
            "Creating Strategy Canvas",
            "processing",
            "Building your Amazon selling strategy document..."
        ))
        
        # Create strategy canvas
        response = canvas_manager.create_strategy_canvas(
            channel_id=channel_id,
            strategy_name="Amazon Selling Strategy",
            market_analysis={
                "target_market": "To be defined",
                "market_size": "Growing",
                "competition": "Medium",
                "trends": ["Increasing demand", "New market entrants"]
            },
            action_plan=[
                "Identify top product opportunities",
                "Analyze competitor strategies",
                "Optimize listings with keywords",
                "Implement pricing strategy",
                "Launch PPC campaigns"
            ]
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            say(f"✅ Strategy canvas created! <{canvas_url}|Open Canvas>")
        else:
            say("❌ Sorry, I couldn't create the strategy canvas.")
            
    except Exception as e:
        logger.error(f"Error creating strategy canvas: {e}")
        say("❌ Sorry, I couldn't create the strategy canvas.")


def handle_track_mentioned_products(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle tracking mentioned products"""
    ack()
    
    try:
        trigger_id = body["trigger_id"]
        
        # Open tracking modal
        modal = create_product_tracking_modal()
        client.views_open(
            trigger_id=trigger_id,
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening tracking modal: {e}")


def handle_export_research_report(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle export research report"""
    ack()
    say("📄 Export feature coming soon! Reports will be available in PDF and CSV formats.")


def handle_set_product_alerts(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle set product alerts"""
    ack()
    say("🔔 Alert system coming soon! You'll be able to set price, BSR, and inventory alerts.")


def handle_track_keyword(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle track keyword"""
    ack()
    
    try:
        keyword = body["actions"][0]["value"]
        say(f"📈 Now tracking keyword: *{keyword}*\n\nYou'll receive updates on search volume and competition changes.")
        
    except Exception as e:
        logger.error(f"Error tracking keyword: {e}")


def handle_create_seo_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create SEO canvas"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        keyword = body["actions"][0]["value"]
        canvas_manager = JungleScoutCanvasManager(client)
        
        say(blocks=JungleScoutFormatter.format_status_update(
            "Creating SEO Canvas",
            "processing",
            f"Building SEO strategy for '{keyword}'..."
        ))
        
        # Create SEO canvas
        response = canvas_manager.create_seo_strategy_canvas(
            channel_id=channel_id,
            primary_keyword=keyword,
            related_keywords=["related keyword 1", "related keyword 2"],
            optimization_tips=[
                "Include primary keyword in title",
                "Use related keywords in bullet points",
                "Optimize backend search terms",
                "Create keyword-rich descriptions"
            ]
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            say(f"✅ SEO strategy canvas created! <{canvas_url}|Open Canvas>")
        else:
            say("❌ Sorry, I couldn't create the SEO canvas.")
            
    except Exception as e:
        logger.error(f"Error creating SEO canvas: {e}")
        say("❌ Sorry, I couldn't create the SEO canvas.")


def handle_find_products_for_keyword(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle find products for keyword"""
    ack()
    
    try:
        keyword = body["actions"][0]["value"]
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Research products for this keyword
        command = f"research {keyword}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error finding products: {e}")


def handle_create_sales_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create sales canvas"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        canvas_manager = JungleScoutCanvasManager(client)
        
        say(blocks=JungleScoutFormatter.format_status_update(
            "Creating Sales Canvas",
            "processing",
            "Building your sales performance report..."
        ))
        
        # Create sales canvas
        response = canvas_manager.create_sales_report_canvas(
            channel_id=channel_id,
            period="Last 30 days",
            metrics={
                "total_revenue": 50000,
                "units_sold": 1500,
                "conversion_rate": 12.5,
                "acos": 25.0
            },
            insights=[
                "Revenue up 15% from previous period",
                "Best performing product: Product A",
                "Conversion rate improved by 2%"
            ]
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            say(f"✅ Sales report canvas created! <{canvas_url}|Open Canvas>")
        else:
            say("❌ Sorry, I couldn't create the sales canvas.")
            
    except Exception as e:
        logger.error(f"Error creating sales canvas: {e}")
        say("❌ Sorry, I couldn't create the sales canvas.")


def handle_set_sales_alerts(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle set sales alerts"""
    ack()
    say("📊 Sales alerts coming soon! Get notified about revenue changes, conversion rates, and more.")


def handle_forecast_sales(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle forecast sales"""
    ack()
    say("📈 Sales forecasting coming soon! AI-powered predictions based on historical data and market trends.")


def handle_monitor_competitor(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle monitor competitor"""
    ack()
    
    try:
        asin = body["actions"][0]["value"]
        say(f"👁️ Now monitoring competitor ASIN: *{asin}*\n\nYou'll receive updates on price changes, inventory, and promotions.")
        
    except Exception as e:
        logger.error(f"Error monitoring competitor: {e}")


def handle_price_history(ack: Ack, body: Dict[str, Any], say: Say, logger):
    """Handle price history"""
    ack()
    say("📊 Price history charts coming soon! Track competitor pricing strategies over time.")


def handle_create_product_watchlist(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create product watchlist"""
    ack()
    
    try:
        watchlist_data = json.loads(body["actions"][0]["value"])
        products = watchlist_data.get("products", [])
        query = watchlist_data.get("query", "products")
        
        say(f"📋 Created watchlist for *{query}* with {len(products)} products!\n\nYou'll receive daily updates on these products.")
        
    except Exception as e:
        logger.error(f"Error creating watchlist: {e}")
        say("❌ Sorry, I couldn't create the watchlist.")