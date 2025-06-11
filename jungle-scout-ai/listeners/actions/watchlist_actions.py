"""
Action handlers for Jungle Scout watchlist and list management
"""
from slack_bolt import Ack, Say
from slack_sdk.web import WebClient
from typing import Dict, Any
import json

from listeners.lists_integration import jungle_scout_lists_manager, create_list_preview_blocks
from utils.logging import logger


def handle_create_product_watchlist(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient):
    """Handle create product watchlist button click"""
    ack()
    
    try:
        # Parse action value
        action_data = json.loads(body["actions"][0]["value"])
        products = action_data.get("products", [])
        query = action_data.get("query", "Products")
        
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Initialize lists manager with client
        if not jungle_scout_lists_manager.client:
            jungle_scout_lists_manager.client = client
        
        # Create watchlist
        list_name = f"🔍 {query.title()} Research"
        list_id = jungle_scout_lists_manager.create_product_watchlist(
            channel_id=channel_id,
            list_name=list_name,
            products=products
        )
        
        if list_id:
            # Show success message
            blocks = create_list_preview_blocks("watchlist", len(products))
            say(blocks=blocks)
        else:
            say("❌ Sorry, I couldn't create the watchlist right now.")
            
    except Exception as e:
        logger.error(f"Error creating product watchlist: {e}")
        say("❌ An error occurred while creating the watchlist.")


def handle_create_keyword_list(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient):
    """Handle create keyword tracking list"""
    ack()
    
    try:
        # Parse action value
        action_data = json.loads(body["actions"][0]["value"])
        keywords = action_data.get("keywords", [])
        
        channel_id = body["channel"]["id"]
        
        # Initialize lists manager
        if not jungle_scout_lists_manager.client:
            jungle_scout_lists_manager.client = client
        
        # Create keyword list
        list_id = jungle_scout_lists_manager.create_keyword_tracking_list(
            channel_id=channel_id,
            keywords=keywords
        )
        
        if list_id:
            blocks = create_list_preview_blocks("keywords", len(keywords))
            say(blocks=blocks)
        else:
            say("❌ Sorry, I couldn't create the keyword list.")
            
    except Exception as e:
        logger.error(f"Error creating keyword list: {e}")
        say("❌ An error occurred while creating the keyword list.")


def handle_create_competitor_list(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient):
    """Handle create competitor tracking list"""
    ack()
    
    try:
        action_data = json.loads(body["actions"][0]["value"])
        competitors = action_data.get("competitors", [])
        
        channel_id = body["channel"]["id"]
        
        # Initialize lists manager
        if not jungle_scout_lists_manager.client:
            jungle_scout_lists_manager.client = client
        
        # Create competitor list
        list_id = jungle_scout_lists_manager.create_competitor_tracking_list(
            channel_id=channel_id,
            competitors=competitors
        )
        
        if list_id:
            blocks = create_list_preview_blocks("competitors", len(competitors))
            say(blocks=blocks)
        else:
            say("❌ Sorry, I couldn't create the competitor list.")
            
    except Exception as e:
        logger.error(f"Error creating competitor list: {e}")
        say("❌ An error occurred while creating the competitor list.")


def handle_create_launch_checklist(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient):
    """Handle create product launch checklist"""
    ack()
    
    try:
        trigger_id = body["trigger_id"]
        
        # Open modal to get product name
        modal = {
            "type": "modal",
            "callback_id": "launch_checklist_modal",
            "title": {
                "type": "plain_text",
                "text": "🚀 Launch Checklist"
            },
            "submit": {
                "type": "plain_text",
                "text": "Create Checklist"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "product_name",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "name_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "e.g., Wireless Earbuds Pro"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Product Name"
                    }
                },
                {
                    "type": "input",
                    "block_id": "launch_date",
                    "element": {
                        "type": "datepicker",
                        "action_id": "date_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select launch date"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Target Launch Date"
                    },
                    "optional": True
                }
            ]
        }
        
        client.views_open(
            trigger_id=trigger_id,
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening launch checklist modal: {e}")


def handle_launch_checklist_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient):
    """Handle launch checklist modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        product_name = values["product_name"]["name_input"]["value"]
        launch_date = values.get("launch_date", {}).get("date_input", {}).get("selected_date")
        
        channel_id = body["view"].get("private_metadata") or body["user"]["id"]
        
        # Initialize lists manager
        if not jungle_scout_lists_manager.client:
            jungle_scout_lists_manager.client = client
        
        # Create launch checklist
        list_id = jungle_scout_lists_manager.create_product_launch_checklist(
            channel_id=channel_id,
            product_name=product_name
        )
        
        if list_id:
            # Post success message
            client.chat_postMessage(
                channel=channel_id,
                blocks=[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚀 Launch Checklist Created"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Product:* {product_name}\n"
                                   f"*Launch Date:* {launch_date or 'Not set'}\n"
                                   f"*Tasks:* 24 tasks across 6 categories\n\n"
                                   f"Your launch checklist is ready with all essential tasks!"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "📋 View Checklist"
                                },
                                "style": "primary",
                                "action_id": "view_checklist"
                            }
                        ]
                    }
                ]
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Sorry, I couldn't create the launch checklist."
            )
            
    except Exception as e:
        logger.error(f"Error processing launch checklist modal: {e}")


def handle_view_list(ack: Ack, body: Dict[str, Any], client: WebClient):
    """Handle view list button - opens list in Slack"""
    ack()
    
    # This would typically open the list view
    # For now, acknowledge the action
    try:
        client.chat_postMessage(
            channel=body["user"]["id"],
            text="📋 Your list has been created! You can view and manage it in the Lists section of this channel."
        )
    except Exception as e:
        logger.error(f"Error handling view list: {e}")


def handle_configure_alerts(ack: Ack, body: Dict[str, Any], client: WebClient):
    """Handle configure alerts button"""
    ack()
    
    try:
        trigger_id = body["trigger_id"]
        
        # Open alert configuration modal
        modal = {
            "type": "modal",
            "callback_id": "configure_alerts_modal",
            "title": {
                "type": "plain_text",
                "text": "🔔 Configure Alerts"
            },
            "submit": {
                "type": "plain_text",
                "text": "Save Settings"
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Price Alerts*"
                    }
                },
                {
                    "type": "input",
                    "block_id": "price_drop",
                    "element": {
                        "type": "number_input",
                        "action_id": "price_drop_percent",
                        "is_decimal_allowed": True,
                        "min_value": "1",
                        "max_value": "100",
                        "initial_value": "10"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Alert when price drops by (%):"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Rank Alerts*"
                    }
                },
                {
                    "type": "input",
                    "block_id": "rank_improve",
                    "element": {
                        "type": "number_input",
                        "action_id": "rank_positions",
                        "min_value": "10",
                        "max_value": "1000",
                        "initial_value": "50"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Alert when BSR improves by positions:"
                    }
                },
                {
                    "type": "input",
                    "block_id": "alert_frequency",
                    "element": {
                        "type": "radio_buttons",
                        "action_id": "frequency_select",
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
                                    "text": "Hourly summary"
                                },
                                "value": "hourly"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Daily summary"
                                },
                                "value": "daily"
                            }
                        ],
                        "initial_option": {
                            "text": {
                                "type": "plain_text",
                                "text": "Hourly summary"
                            },
                            "value": "hourly"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Alert Frequency"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=trigger_id,
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening alerts modal: {e}")