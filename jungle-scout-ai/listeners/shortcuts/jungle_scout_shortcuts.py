"""
Enhanced shortcuts for Jungle Scout AI Assistant with global and message shortcuts
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any
import json
import re

from listeners.jungle_scout_assistant import jungle_scout_assistant
from listeners.jungle_scout_ui import create_status_blocks
from listeners.jungle_scout_canvas import JungleScoutCanvasManager


def handle_quick_product_lookup_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for quick product lookup"""
    ack()
    
    try:
        # Open modal for product lookup
        modal = {
            "type": "modal",
            "callback_id": "quick_product_lookup_modal",
            "title": {
                "type": "plain_text",
                "text": "🔍 Quick Product Lookup"
            },
            "submit": {
                "type": "plain_text",
                "text": "Analyze"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "product_input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "ASIN, product URL, or keywords"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Product"
                    },
                    "hint": {
                        "type": "plain_text",
                        "text": "Enter an ASIN (e.g., B08N5WRWNW), Amazon URL, or product keywords"
                    }
                },
                {
                    "type": "input",
                    "block_id": "analysis_depth",
                    "element": {
                        "type": "radio_buttons",
                        "action_id": "depth_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Quick overview"
                                },
                                "value": "quick"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Detailed analysis"
                                },
                                "value": "detailed"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Full competitor analysis"
                                },
                                "value": "competitor"
                            }
                        ],
                        "initial_option": {
                            "text": {
                                "type": "plain_text",
                                "text": "Quick overview"
                            },
                            "value": "quick"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Analysis Type"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening quick product lookup modal: {e}")


def handle_analyze_from_clipboard_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut to analyze product from clipboard"""
    ack()
    
    try:
        # Open modal with instructions
        modal = {
            "type": "modal",
            "callback_id": "analyze_clipboard_modal",
            "title": {
                "type": "plain_text",
                "text": "📋 Analyze from Clipboard"
            },
            "submit": {
                "type": "plain_text",
                "text": "Analyze"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Paste product information you've copied from Amazon or elsewhere."
                    }
                },
                {
                    "type": "input",
                    "block_id": "clipboard_content",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "content_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Paste ASIN, URL, or product details here..."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Product Information"
                    }
                },
                {
                    "type": "input",
                    "block_id": "analysis_focus",
                    "element": {
                        "type": "checkboxes",
                        "action_id": "focus_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sales estimation"
                                },
                                "value": "sales"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Keyword analysis"
                                },
                                "value": "keywords"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Competition assessment"
                                },
                                "value": "competition"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Profit calculation"
                                },
                                "value": "profit"
                            }
                        ],
                        "initial_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sales estimation"
                                },
                                "value": "sales"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Competition assessment"
                                },
                                "value": "competition"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Analysis Focus"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening analyze clipboard modal: {e}")


def handle_market_snapshot_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for market snapshot"""
    ack()
    
    try:
        # Open modal for market selection
        modal = {
            "type": "modal",
            "callback_id": "market_snapshot_modal",
            "title": {
                "type": "plain_text",
                "text": "📊 Market Snapshot"
            },
            "submit": {
                "type": "plain_text",
                "text": "Get Snapshot"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "market_category",
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
                                    "text": "Electronics & Accessories"
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
                                    "text": "Health & Personal Care"
                                },
                                "value": "health"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sports & Outdoors"
                                },
                                "value": "sports"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Baby Products"
                                },
                                "value": "baby"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Beauty & Personal Care"
                                },
                                "value": "beauty"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Pet Supplies"
                                },
                                "value": "pet"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Custom Category"
                                },
                                "value": "custom"
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
                    "block_id": "custom_category",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "custom_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter custom category or niche"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Custom Category (if selected above)"
                    },
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "snapshot_type",
                    "element": {
                        "type": "checkboxes",
                        "action_id": "type_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Top sellers"
                                },
                                "value": "top_sellers"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "New releases"
                                },
                                "value": "new_releases"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Trending products"
                                },
                                "value": "trending"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Price analysis"
                                },
                                "value": "pricing"
                            }
                        ],
                        "initial_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Top sellers"
                                },
                                "value": "top_sellers"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Trending products"
                                },
                                "value": "trending"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Include in Snapshot"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening market snapshot modal: {e}")


def handle_analyze_product_from_message_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle message shortcut to analyze product mentioned in message"""
    ack()
    
    try:
        # Get the message
        message = body.get("message", {})
        message_text = message.get("text", "")
        user_id = body.get("user", {}).get("id")
        
        # Extract potential ASINs or product URLs from message
        asin_pattern = r'B[0-9A-Z]{9}'
        url_pattern = r'amazon\.com/[^/]+/dp/([A-Z0-9]{10})'
        
        asins = re.findall(asin_pattern, message_text)
        url_matches = re.findall(url_pattern, message_text)
        all_asins = list(set(asins + url_matches))
        
        if all_asins:
            # Found ASINs, analyze them
            for asin in all_asins[:3]:  # Limit to first 3
                client.chat_postMessage(
                    channel=user_id,
                    blocks=create_status_blocks("processing", f"Analyzing product {asin}...")
                )
                
                # Process with assistant
                jungle_scout_assistant.process_jungle_scout_command(
                    body={"text": f"analyze {asin}", "channel": {"id": user_id}, "user": {"id": user_id}},
                    context=BoltContext(),
                    say=lambda text=None, blocks=None: client.chat_postMessage(
                        channel=user_id,
                        text=text,
                        blocks=blocks
                    ),
                    client=client
                )
        else:
            # No ASINs found, open modal to get more info
            modal = {
                "type": "modal",
                "callback_id": "analyze_message_product_modal",
                "title": {
                    "type": "plain_text",
                    "text": "🔍 Analyze Product"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Analyze"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "private_metadata": json.dumps({
                    "message_text": message_text
                }),
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Message:*\n```{message_text[:200]}{'...' if len(message_text) > 200 else ''}```"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "product_identifier",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "identifier_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter ASIN or product name from the message"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Product to Analyze"
                        },
                        "hint": {
                            "type": "plain_text",
                            "text": "No ASIN found in message. Please specify the product."
                        }
                    }
                ]
            }
            
            client.views_open(
                trigger_id=body["trigger_id"],
                view=modal
            )
        
    except Exception as e:
        logger.error(f"Error analyzing product from message: {e}")


def handle_create_research_report_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle message shortcut to create research report from thread"""
    ack()
    
    try:
        # Get the message and thread
        message = body.get("message", {})
        channel_id = body.get("channel", {}).get("id")
        thread_ts = message.get("thread_ts") or message.get("ts")
        user_id = body.get("user", {}).get("id")
        
        # Show processing status
        client.chat_postMessage(
            channel=user_id,
            blocks=create_status_blocks("processing", "Creating research report...")
        )
        
        # Get thread messages if it's a thread
        messages = []
        if thread_ts:
            result = client.conversations_replies(
                channel=channel_id,
                ts=thread_ts,
                limit=100
            )
            messages = result.get("messages", [])
        else:
            messages = [message]
        
        # Extract product information from thread
        all_asins = []
        for msg in messages:
            text = msg.get("text", "")
            asins = re.findall(r'B[0-9A-Z]{9}', text)
            all_asins.extend(asins)
        
        unique_asins = list(set(all_asins))
        
        # Create research canvas
        canvas_manager = JungleScoutCanvasManager(client)
        
        # Mock product data for canvas
        products = []
        for asin in unique_asins[:5]:  # Limit to 5 products
            products.append({
                "asin": asin,
                "title": f"Product {asin}",
                "opportunity_score": 7.5,
                "monthly_revenue": 35000,
                "competition_level": "Medium"
            })
        
        response = canvas_manager.create_product_research_canvas(
            channel_id=user_id,
            search_query="Thread Research Report",
            products=products,
            market_insights={
                "products_analyzed": len(unique_asins),
                "thread_messages": len(messages),
                "date": "Today"
            }
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            client.chat_postMessage(
                channel=user_id,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"📝 Created research report from thread in <#{channel_id}>\n\n*Products found:* {len(unique_asins)}"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Open Report"
                            },
                            "url": canvas_url or "#",
                            "style": "primary"
                        }
                    }
                ]
            )
        
    except Exception as e:
        logger.error(f"Error creating research report: {e}")
        client.chat_postMessage(
            channel=body.get("user", {}).get("id"),
            text="❌ Sorry, I couldn't create the research report."
        )


# Modal submission handlers
def handle_quick_product_lookup_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle quick product lookup modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        product_input = values["product_input"]["input"]["value"]
        analysis_depth = values["analysis_depth"]["depth_input"]["selected_option"]["value"]
        user_id = body["user"]["id"]
        
        # Build command based on analysis depth
        if analysis_depth == "quick":
            command = f"analyze {product_input}"
        elif analysis_depth == "detailed":
            command = f"research {product_input}"
        elif analysis_depth == "competitor":
            command = f"competitor {product_input}"
        
        # Process with assistant
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": user_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=user_id,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error processing product lookup: {e}")


def handle_analyze_clipboard_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle analyze clipboard modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        content = values["clipboard_content"]["content_input"]["value"]
        focus_options = values["analysis_focus"]["focus_input"]["selected_options"]
        user_id = body["user"]["id"]
        
        # Extract ASIN or keywords from content
        asin_match = re.search(r'B[0-9A-Z]{9}', content)
        
        if asin_match:
            # Found ASIN, analyze it
            asin = asin_match.group(0)
            command = f"analyze {asin}"
        else:
            # Use content as keywords
            keywords = content.strip()[:100]  # Limit length
            command = f"research {keywords}"
        
        # Add focus areas to command
        focus_areas = [opt["value"] for opt in focus_options]
        if focus_areas:
            command += f" focusing on {', '.join(focus_areas)}"
        
        # Process with assistant
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": user_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=user_id,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error analyzing clipboard content: {e}")


def handle_market_snapshot_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle market snapshot modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        category = values["market_category"]["category_input"]["selected_option"]["value"]
        custom_category = values.get("custom_category", {}).get("custom_input", {}).get("value", "")
        snapshot_types = values["snapshot_type"]["type_input"]["selected_options"]
        user_id = body["user"]["id"]
        
        # Determine category to use
        if category == "custom" and custom_category:
            market_category = custom_category
        else:
            market_category = category.replace("_", " ")
        
        # Build command
        types = [opt["value"] for opt in snapshot_types]
        command = f"trends {market_category}"
        if "top_sellers" in types:
            command += " including top sellers"
        if "new_releases" in types:
            command += " and new releases"
        if "pricing" in types:
            command += " with price analysis"
        
        # Process with assistant
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": user_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=user_id,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error generating market snapshot: {e}")


def handle_analyze_message_product_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle analyze message product modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        product_identifier = values["product_identifier"]["identifier_input"]["value"]
        user_id = body["user"]["id"]
        
        # Process with assistant
        command = f"analyze {product_identifier}"
        jungle_scout_assistant.process_jungle_scout_command(
            body={"text": command, "channel": {"id": user_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=user_id,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error analyzing product: {e}")