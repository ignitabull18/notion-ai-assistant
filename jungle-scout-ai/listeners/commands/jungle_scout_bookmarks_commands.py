"""
Jungle Scout bookmarks command handlers
"""
from slack_bolt import Ack, Say
from slack_sdk.web import WebClient
from typing import Dict, Any
import re

from listeners.jungle_scout_bookmarks import (
    JungleScoutBookmarksManager,
    create_product_bookmarks_blocks,
    create_add_product_bookmark_modal
)
from listeners.jungle_scout_ui import create_status_blocks
from jungle_scout_ai.logging import logger


def handle_product_bookmarks_command(ack: Ack, command: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /product-bookmarks command"""
    ack()
    
    try:
        channel_id = command["channel_id"]
        text = command.get("text", "").strip()
        
        bookmarks_manager = JungleScoutBookmarksManager(client)
        
        if not text or text == "list":
            # List product bookmarks
            bookmarks = bookmarks_manager.get_product_bookmarks(channel_id)
            blocks = create_product_bookmarks_blocks(bookmarks, channel_id)
            say(blocks=blocks)
            
        elif text == "resources":
            # Add market resources
            say(blocks=create_status_blocks("processing", "Adding market research resources..."))
            created = bookmarks_manager.create_market_resource_bookmarks(channel_id)
            
            if created:
                say(f"✅ Added {len(created)} market research resources!")
            else:
                say("❌ Failed to add resource bookmarks.")
                
        elif text == "organize":
            # Organize research bookmarks
            organized = bookmarks_manager.organize_research_bookmarks(channel_id)
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 Research Bookmarks Organized"
                    }
                }
            ]
            
            for category, items in organized.items():
                if not items:
                    continue
                    
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{category}* ({len(items)})"
                    }
                })
                
                for bookmark in items[:3]:
                    blocks.append({
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": f"{bookmark.get('emoji', '🛍️')} <{bookmark['link']}|{bookmark['title']}>"
                        }]
                    })
                    
                if len(items) > 3:
                    blocks.append({
                        "type": "context",
                        "elements": [{
                            "type": "mrkdwn",
                            "text": f"_...and {len(items) - 3} more_"
                        }]
                    })
            
            say(blocks=blocks)
            
        elif text.startswith("add "):
            # Quick add product by ASIN or URL
            product_input = text[4:].strip()
            
            # Extract ASIN from input
            asin_match = re.search(r'B[0-9A-Z]{9}', product_input)
            if asin_match:
                asin = asin_match.group(0)
                
                # Mock product data (in production, fetch from API)
                product_data = {
                    "asin": asin,
                    "title": f"Product {asin}",
                    "url": f"https://amazon.com/dp/{asin}",
                    "price": 29.99,
                    "rating": 4.5,
                    "opportunity_score": 7
                }
                
                bookmark = bookmarks_manager.add_product_bookmark(channel_id, product_data)
                
                if bookmark:
                    say(f"✅ Added product bookmark: {bookmark['title']}")
                else:
                    say("❌ Failed to add product bookmark.")
            else:
                say("Please provide a valid ASIN or Amazon URL. Example: `/product-bookmarks add B08N5WRWNW`")
                
        elif text == "export":
            # Export bookmarks list
            bookmarks = bookmarks_manager.get_product_bookmarks(channel_id)
            
            if bookmarks:
                export_text = "📊 Product Bookmarks Export\n\n"
                for bookmark in bookmarks:
                    export_text += f"{bookmark.get('emoji', '🛍️')} {bookmark['title']}\n"
                    export_text += f"   URL: {bookmark['link']}\n\n"
                
                # Create a snippet
                client.files_upload_v2(
                    channel=channel_id,
                    initial_comment="Here's your product bookmarks export:",
                    filename="product_bookmarks.txt",
                    content=export_text
                )
            else:
                say("No bookmarks to export.")
                
        elif text == "help":
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🛍️ Product Bookmarks Help"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Available commands:*\n"
                                "• `/product-bookmarks` - List all product bookmarks\n"
                                "• `/product-bookmarks add <ASIN>` - Quick add product\n"
                                "• `/product-bookmarks resources` - Add research resources\n"
                                "• `/product-bookmarks organize` - View by category\n"
                                "• `/product-bookmarks export` - Export bookmarks list\n"
                                "• `/product-bookmarks help` - Show this help"
                    }
                }
            ]
            say(blocks=blocks)
            
        else:
            say("Unknown command. Try `/product-bookmarks help`")
            
    except Exception as e:
        logger.error(f"Error handling product bookmarks command: {e}")
        say("❌ Sorry, I couldn't process the bookmarks command.")


def handle_product_bookmark_action(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle product bookmark button actions"""
    ack()
    
    try:
        action = body["actions"][0]
        action_id = action["action_id"]
        channel_id = body["channel"]["id"]
        
        bookmarks_manager = JungleScoutBookmarksManager(client)
        
        if action_id.startswith("add_market_resources_"):
            # Add market resources
            created = bookmarks_manager.create_market_resource_bookmarks(channel_id)
            
            # Update the message
            bookmarks = bookmarks_manager.get_product_bookmarks(channel_id)
            blocks = create_product_bookmarks_blocks(bookmarks, channel_id)
            
            client.chat_update(
                channel=channel_id,
                ts=body["message"]["ts"],
                blocks=blocks
            )
            
        elif action_id.startswith("add_product_bookmark_"):
            # Open modal to add product
            client.views_open(
                trigger_id=body["trigger_id"],
                view=create_add_product_bookmark_modal(channel_id)
            )
            
        elif action_id.startswith("analyze_bookmark_"):
            # Analyze bookmarked product
            bookmark_link = action.get("value", "")
            
            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', bookmark_link)
            if asin_match:
                asin = asin_match.group(1)
                
                # Show analysis (simplified)
                client.chat_postMessage(
                    channel=body["user"]["id"],
                    blocks=create_status_blocks("processing", f"Analyzing product {asin}...")
                )
                
                # In production, call the Jungle Scout assistant to analyze
                client.chat_postMessage(
                    channel=body["user"]["id"],
                    text=f"To analyze this product, use: `/analyze {asin}`"
                )
                
        elif action_id.startswith("view_all_bookmarks_"):
            # Show all bookmarks
            bookmarks = bookmarks_manager.get_product_bookmarks(channel_id)
            organized = bookmarks_manager.organize_research_bookmarks(channel_id)
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 All Research Bookmarks"
                    }
                }
            ]
            
            total_count = sum(len(items) for items in organized.values())
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total bookmarks:* {total_count}"
                }
            })
            
            for category, items in organized.items():
                if items:
                    blocks.append({"type": "divider"})
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{category}*"
                        }
                    })
                    
                    for bookmark in items:
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"{bookmark.get('emoji', '🛍️')} <{bookmark['link']}|{bookmark['title']}>"
                            }
                        })
            
            client.chat_postMessage(
                channel=body["user"]["id"],
                blocks=blocks
            )
            
        elif action_id.startswith("export_bookmarks_"):
            # Export bookmarks
            bookmarks = bookmarks_manager.get_product_bookmarks(channel_id)
            
            if bookmarks:
                export_text = "📊 Product Research Bookmarks Export\n" + "=" * 50 + "\n\n"
                
                organized = bookmarks_manager.organize_research_bookmarks(channel_id)
                for category, items in organized.items():
                    if items:
                        export_text += f"\n{category}\n" + "-" * len(category) + "\n"
                        for bookmark in items:
                            export_text += f"\n{bookmark.get('emoji', '🛍️')} {bookmark['title']}\n"
                            export_text += f"   URL: {bookmark['link']}\n"
                            if bookmark.get('entity_id', '').startswith('product_'):
                                asin = bookmark['entity_id'].replace('product_', '')
                                export_text += f"   ASIN: {asin}\n"
                
                # Upload as file
                client.files_upload_v2(
                    channel=channel_id,
                    initial_comment="📊 Your product bookmarks export is ready!",
                    filename="product_research_bookmarks.txt",
                    content=export_text
                )
            
    except Exception as e:
        logger.error(f"Error handling product bookmark action: {e}")


def handle_add_product_bookmark_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle add product bookmark modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        url = values["product_url"]["url_input"]["value"]
        asin = values.get("product_asin", {}).get("asin_input", {}).get("value", "")
        opportunity_score = values.get("opportunity_score", {}).get("score_input", {}).get("value")
        notes = values.get("notes", {}).get("notes_input", {}).get("value", "")
        channel_id = body["view"]["private_metadata"]
        
        bookmarks_manager = JungleScoutBookmarksManager(client)
        
        # Extract ASIN from URL if not provided
        if not asin:
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            if asin_match:
                asin = asin_match.group(1)
            else:
                # Try to extract from the URL path
                asin_match = re.search(r'B[0-9A-Z]{9}', url)
                if asin_match:
                    asin = asin_match.group(0)
        
        if not asin:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text="❌ Could not extract ASIN from the URL. Please provide a valid Amazon product URL."
            )
            return
        
        # Create product data
        product_data = {
            "asin": asin,
            "title": f"Product {asin} - {notes[:50] if notes else 'Tracked'}",
            "url": url,
            "opportunity_score": float(opportunity_score) if opportunity_score else None
        }
        
        # Add the bookmark
        bookmark = bookmarks_manager.add_product_bookmark(channel_id, product_data)
        
        if bookmark:
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Added product bookmark: {bookmark['title']}"
            )
        else:
            client.chat_postMessage(
                channel=body["user"]["id"],
                text=f"❌ Failed to add bookmark. You may not have permission to add bookmarks to <#{channel_id}>."
            )
            
    except Exception as e:
        logger.error(f"Error adding product bookmark: {e}")