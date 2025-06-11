"""
Enhanced shortcuts for Notion AI Assistant with global and message shortcuts
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any
import json
import asyncio

from listeners.agno_integration import process_with_agent
from listeners.ui_components import create_notion_status_blocks
from listeners.notion_canvas import NotionCanvasManager


def handle_quick_note_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for quick note creation"""
    ack()
    
    try:
        # Open modal for quick note
        modal = {
            "type": "modal",
            "callback_id": "quick_note_modal",
            "title": {
                "type": "plain_text",
                "text": "📝 Quick Notion Note"
            },
            "submit": {
                "type": "plain_text",
                "text": "Create Note"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "note_title",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Note title"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Title"
                    }
                },
                {
                    "type": "input",
                    "block_id": "note_content",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "content_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Start typing your note..."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Content"
                    }
                },
                {
                    "type": "input",
                    "block_id": "note_database",
                    "element": {
                        "type": "static_select",
                        "action_id": "database_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a database"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Personal Notes"
                                },
                                "value": "personal_notes"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Meeting Notes"
                                },
                                "value": "meeting_notes"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Quick Ideas"
                                },
                                "value": "quick_ideas"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Workspace Root"
                                },
                                "value": "workspace_root"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Location"
                    }
                },
                {
                    "type": "input",
                    "block_id": "note_tags",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "tags_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "tag1, tag2, tag3"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Tags (comma-separated)"
                    },
                    "optional": True
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening quick note modal: {e}")


def handle_search_notion_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for Notion search"""
    ack()
    
    try:
        # Open search modal
        modal = {
            "type": "modal",
            "callback_id": "search_notion_modal",
            "title": {
                "type": "plain_text",
                "text": "🔍 Search Notion"
            },
            "submit": {
                "type": "plain_text",
                "text": "Search"
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
                            "text": "Enter search terms..."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Search Query"
                    }
                },
                {
                    "type": "input",
                    "block_id": "search_type",
                    "element": {
                        "type": "checkboxes",
                        "action_id": "type_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Pages"
                                },
                                "value": "pages"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Databases"
                                },
                                "value": "databases"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Comments"
                                },
                                "value": "comments"
                            }
                        ],
                        "initial_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Pages"
                                },
                                "value": "pages"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Databases"
                                },
                                "value": "databases"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Search In"
                    }
                },
                {
                    "type": "input",
                    "block_id": "search_filters",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "filters_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "e.g., created:last-week, author:john"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Filters (optional)"
                    },
                    "optional": True
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening Notion search modal: {e}")


def handle_create_page_from_message_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle message shortcut to create Notion page from message"""
    ack()
    
    try:
        # Get the message
        message = body.get("message", {})
        message_text = message.get("text", "")
        user = message.get("user", "")
        channel_id = body.get("channel", {}).get("id")
        
        # Open modal with pre-filled content
        modal = {
            "type": "modal",
            "callback_id": "create_page_from_message_modal",
            "title": {
                "type": "plain_text",
                "text": "📄 Create Notion Page"
            },
            "submit": {
                "type": "plain_text",
                "text": "Create Page"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "private_metadata": json.dumps({
                "message_text": message_text,
                "user": user,
                "channel_id": channel_id
            }),
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message Preview:*\n```{message_text[:200]}{'...' if len(message_text) > 200 else ''}```"
                    }
                },
                {
                    "type": "input",
                    "block_id": "page_title",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title_input",
                        "initial_value": f"Message from Slack - {message_text[:50]}...",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Page title"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Page Title"
                    }
                },
                {
                    "type": "input",
                    "block_id": "page_location",
                    "element": {
                        "type": "static_select",
                        "action_id": "location_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select location"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Meeting Notes"
                                },
                                "value": "meeting_notes"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Project Docs"
                                },
                                "value": "project_docs"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Ideas & Brainstorming"
                                },
                                "value": "ideas"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Workspace Root"
                                },
                                "value": "workspace_root"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Parent Location"
                    }
                },
                {
                    "type": "input",
                    "block_id": "include_context",
                    "element": {
                        "type": "checkboxes",
                        "action_id": "context_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Include thread context"
                                },
                                "value": "thread"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Include channel info"
                                },
                                "value": "channel"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Include timestamp"
                                },
                                "value": "timestamp"
                            }
                        ],
                        "initial_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Include channel info"
                                },
                                "value": "channel"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Include timestamp"
                                },
                                "value": "timestamp"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Additional Context"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening create page from message modal: {e}")


def handle_save_to_notion_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle message shortcut to save content to existing Notion page/database"""
    ack()
    
    try:
        # Get the message
        message = body.get("message", {})
        message_text = message.get("text", "")
        
        # Open save modal
        modal = {
            "type": "modal",
            "callback_id": "save_to_notion_modal",
            "title": {
                "type": "plain_text",
                "text": "💾 Save to Notion"
            },
            "submit": {
                "type": "plain_text",
                "text": "Save"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "private_metadata": json.dumps({
                "message_text": message_text,
                "channel_id": body.get("channel", {}).get("id"),
                "message_ts": message.get("ts")
            }),
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Content to save:*\n```{message_text[:150]}{'...' if len(message_text) > 150 else ''}```"
                    }
                },
                {
                    "type": "input",
                    "block_id": "save_type",
                    "element": {
                        "type": "radio_buttons",
                        "action_id": "type_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Add to existing page"
                                },
                                "value": "append_page"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Create database entry"
                                },
                                "value": "database_entry"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Add as comment"
                                },
                                "value": "comment"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Save As"
                    }
                },
                {
                    "type": "input",
                    "block_id": "notion_id",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "id_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Page or Database ID (or URL)"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Notion Page/Database"
                    },
                    "hint": {
                        "type": "plain_text",
                        "text": "You can paste a Notion URL or ID"
                    }
                }
            ]
        }
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=modal
        )
        
    except Exception as e:
        logger.error(f"Error opening save to Notion modal: {e}")


def handle_notion_workspace_overview_shortcut(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle global shortcut to get Notion workspace overview"""
    ack()
    
    try:
        user_id = body["user"]["id"]
        
        # Show processing status
        client.chat_postMessage(
            channel=user_id,
            blocks=create_notion_status_blocks("processing", "Generating workspace overview...")
        )
        
        # Get workspace overview
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message="Give me an overview of my Notion workspace including recent activity, databases, and key pages"
            )
        )
        
        # Send response
        if isinstance(response, dict) and 'blocks' in response:
            client.chat_postMessage(
                channel=user_id,
                blocks=response['blocks'],
                text=response.get('text', 'Workspace overview')
            )
        else:
            client.chat_postMessage(
                channel=user_id,
                text=response
            )
        
        # Offer to create a canvas
        client.chat_postMessage(
            channel=user_id,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Would you like me to create a collaborative canvas with this overview?"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Canvas"
                        },
                        "action_id": "create_workspace_canvas",
                        "style": "primary"
                    }
                }
            ]
        )
        
    except Exception as e:
        logger.error(f"Error getting workspace overview: {e}")
        client.chat_postMessage(
            channel=body["user"]["id"],
            text="❌ Sorry, I couldn't generate the workspace overview."
        )


# Modal submission handlers
def handle_quick_note_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle quick note modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        title = values["note_title"]["title_input"]["value"]
        content = values["note_content"]["content_input"]["value"]
        database = values["note_database"]["database_input"]["selected_option"]["value"]
        tags = values.get("note_tags", {}).get("tags_input", {}).get("value", "")
        user_id = body["user"]["id"]
        
        # Build command for agent
        command = f"Create a new Notion page titled '{title}' with content: {content}"
        if database != "workspace_root":
            command += f" in the {database.replace('_', ' ')} database"
        if tags:
            command += f" with tags: {tags}"
        
        # Process with agent
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command
            )
        )
        
        # Send response as DM
        if isinstance(response, dict) and 'blocks' in response:
            client.chat_postMessage(
                channel=user_id,
                blocks=response['blocks'],
                text=response.get('text', 'Note created')
            )
        else:
            client.chat_postMessage(
                channel=user_id,
                text=response
            )
        
    except Exception as e:
        logger.error(f"Error creating quick note: {e}")


def handle_search_notion_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle Notion search modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        query = values["search_query"]["query_input"]["value"]
        search_types = values["search_type"]["type_input"]["selected_options"]
        filters = values.get("search_filters", {}).get("filters_input", {}).get("value", "")
        user_id = body["user"]["id"]
        
        # Build search command
        types = [opt["value"] for opt in search_types]
        command = f"Search Notion for '{query}'"
        if types:
            command += f" in {', '.join(types)}"
        if filters:
            command += f" with filters: {filters}"
        
        # Process search
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command
            )
        )
        
        # Send response as DM
        if isinstance(response, dict) and 'blocks' in response:
            client.chat_postMessage(
                channel=user_id,
                blocks=response['blocks'],
                text=response.get('text', 'Search results')
            )
        else:
            client.chat_postMessage(
                channel=user_id,
                text=response
            )
        
    except Exception as e:
        logger.error(f"Error searching Notion: {e}")


def handle_create_page_from_message_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle create page from message modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        page_title = values["page_title"]["title_input"]["value"]
        location = values["page_location"]["location_input"]["selected_option"]["value"]
        context_options = values["include_context"]["context_input"]["selected_options"]
        
        # Get message data from private metadata
        metadata = json.loads(body["view"]["private_metadata"])
        message_text = metadata["message_text"]
        channel_id = metadata["channel_id"]
        user = metadata["user"]
        user_id = body["user"]["id"]
        
        # Build page content
        content = f"## Message Content\n\n{message_text}\n\n"
        
        # Add context if requested
        context_values = [opt["value"] for opt in context_options]
        if "channel" in context_values:
            content += f"**Channel:** <#{channel_id}>\n"
        if "timestamp" in context_values:
            from datetime import datetime
            content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        if "thread" in context_values:
            content += f"**Author:** <@{user}>\n"
        
        # Create command
        command = f"Create a new Notion page titled '{page_title}' with content: {content}"
        if location != "workspace_root":
            command += f" in the {location.replace('_', ' ')} location"
        
        # Process with agent
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command
            )
        )
        
        # Send response as DM
        if isinstance(response, dict) and 'blocks' in response:
            client.chat_postMessage(
                channel=user_id,
                blocks=response['blocks'],
                text=response.get('text', 'Page created')
            )
        else:
            client.chat_postMessage(
                channel=user_id,
                text=response
            )
        
    except Exception as e:
        logger.error(f"Error creating page from message: {e}")


def handle_save_to_notion_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle save to Notion modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        save_type = values["save_type"]["type_input"]["selected_option"]["value"]
        notion_id = values["notion_id"]["id_input"]["value"]
        
        # Get message data from private metadata
        metadata = json.loads(body["view"]["private_metadata"])
        message_text = metadata["message_text"]
        user_id = body["user"]["id"]
        
        # Build command based on save type
        if save_type == "append_page":
            command = f"Add this content to Notion page {notion_id}: {message_text}"
        elif save_type == "database_entry":
            command = f"Create a new entry in Notion database {notion_id} with content: {message_text}"
        elif save_type == "comment":
            command = f"Add this as a comment to Notion page {notion_id}: {message_text}"
        
        # Process with agent
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command
            )
        )
        
        # Send response as DM
        if isinstance(response, dict) and 'blocks' in response:
            client.chat_postMessage(
                channel=user_id,
                blocks=response['blocks'],
                text=response.get('text', 'Content saved')
            )
        else:
            client.chat_postMessage(
                channel=user_id,
                text=response
            )
        
    except Exception as e:
        logger.error(f"Error saving to Notion: {e}")