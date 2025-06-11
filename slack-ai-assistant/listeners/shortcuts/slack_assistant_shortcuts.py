"""
Enhanced shortcuts for Slack AI Assistant with global and message shortcuts
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any
import json
from datetime import datetime

from listeners.ui_components import create_status_blocks
from listeners.canvas_integration import CanvasManager
from listeners.slack_assistant import slack_assistant


def handle_quick_reminder_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for quick reminder creation"""
    ack()
    
    try:
        # Open modal for reminder creation
        modal = {
            "type": "modal",
            "callback_id": "quick_reminder_modal",
            "title": {
                "type": "plain_text",
                "text": "⏰ Quick Reminder"
            },
            "submit": {
                "type": "plain_text",
                "text": "Set Reminder"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "reminder_text",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "text_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "What would you like to be reminded about?"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Reminder"
                    }
                },
                {
                    "type": "input",
                    "block_id": "reminder_time",
                    "element": {
                        "type": "datetimepicker",
                        "action_id": "datetime_input",
                        "initial_date_time": int((datetime.now().timestamp() + 3600))  # Default to 1 hour from now
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "When"
                    }
                },
                {
                    "type": "input",
                    "block_id": "reminder_channel",
                    "element": {
                        "type": "channels_select",
                        "action_id": "channel_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a channel (optional)"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Channel (or leave empty for DM)"
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
        logger.error(f"Error opening quick reminder modal: {e}")


def handle_search_workspace_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for workspace search"""
    ack()
    
    try:
        # Open search modal
        modal = {
            "type": "modal",
            "callback_id": "workspace_search_modal",
            "title": {
                "type": "plain_text",
                "text": "🔍 Search Workspace"
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
                    "block_id": "search_filters",
                    "element": {
                        "type": "checkboxes",
                        "action_id": "filter_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Messages"
                                },
                                "value": "messages"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Files"
                                },
                                "value": "files"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Channels"
                                },
                                "value": "channels"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "People"
                                },
                                "value": "people"
                            }
                        ],
                        "initial_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Messages"
                                },
                                "value": "messages"
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
                    "block_id": "search_timeframe",
                    "element": {
                        "type": "static_select",
                        "action_id": "timeframe_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select timeframe"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Any time"
                                },
                                "value": "all"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Past day"
                                },
                                "value": "1d"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Past week"
                                },
                                "value": "7d"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Past month"
                                },
                                "value": "30d"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Past year"
                                },
                                "value": "365d"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Time Range"
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
        logger.error(f"Error opening workspace search modal: {e}")


def handle_create_summary_shortcut(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle message shortcut to create summary from thread"""
    ack()
    
    try:
        # Get the message that triggered the shortcut
        message = body.get("message", {})
        channel_id = body.get("channel", {}).get("id")
        thread_ts = message.get("thread_ts") or message.get("ts")
        
        # Get channel for response
        response_channel = body.get("user", {}).get("id")  # DM the user
        
        # Show processing status
        client.chat_postMessage(
            channel=response_channel,
            blocks=create_status_blocks("processing", "Creating thread summary...")
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
        
        # Create summary using the assistant
        summary_request = f"Create a summary of this thread with {len(messages)} messages"
        if len(messages) > 1:
            # Include message preview
            preview = "\n".join([f"- {msg.get('text', '')[:100]}..." for msg in messages[:5]])
            summary_request += f"\n\nPreview:\n{preview}"
        
        # Process with assistant
        response = slack_assistant.process_slack_command(
            body={"text": summary_request, "channel": {"id": response_channel}, "user": body.get("user")},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=response_channel,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
        # Create canvas with summary
        canvas_manager = CanvasManager(client)
        canvas_response = canvas_manager.create_thread_summary_canvas(
            channel_id=response_channel,
            thread_messages=messages,
            summary="Thread summary created via shortcut"
        )
        
        if canvas_response:
            canvas_url = canvas_manager.get_canvas_url(canvas_response)
            client.chat_postMessage(
                channel=response_channel,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"📝 Created summary canvas for thread in <#{channel_id}>"
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
        
    except Exception as e:
        logger.error(f"Error creating summary: {e}")
        client.chat_postMessage(
            channel=body.get("user", {}).get("id"),
            text="❌ Sorry, I couldn't create the thread summary."
        )


def handle_analyze_message_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle message shortcut to analyze message content"""
    ack()
    
    try:
        # Get the message
        message = body.get("message", {})
        message_text = message.get("text", "")
        user_id = body.get("user", {}).get("id")
        
        # Open analysis modal
        modal = {
            "type": "modal",
            "callback_id": "analyze_message_modal",
            "title": {
                "type": "plain_text",
                "text": "🔍 Analyze Message"
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
                "message_text": message_text,
                "channel_id": body.get("channel", {}).get("id"),
                "message_ts": message.get("ts")
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
                    "block_id": "analysis_type",
                    "element": {
                        "type": "radio_buttons",
                        "action_id": "type_input",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Sentiment Analysis"
                                },
                                "value": "sentiment"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Key Points Extraction"
                                },
                                "value": "key_points"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Action Items"
                                },
                                "value": "action_items"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Translation"
                                },
                                "value": "translate"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Custom Analysis"
                                },
                                "value": "custom"
                            }
                        ]
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Analysis Type"
                    }
                },
                {
                    "type": "input",
                    "block_id": "custom_prompt",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "prompt_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "What would you like to know about this message?"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Custom Prompt (for custom analysis)"
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
        logger.error(f"Error opening analyze message modal: {e}")


def handle_quick_task_shortcut(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle global shortcut for quick task creation"""
    ack()
    
    try:
        # Open task creation modal
        modal = {
            "type": "modal",
            "callback_id": "quick_task_modal",
            "title": {
                "type": "plain_text",
                "text": "✅ Quick Task"
            },
            "submit": {
                "type": "plain_text",
                "text": "Create Task"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "task_title",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "title_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Task title"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Task"
                    }
                },
                {
                    "type": "input",
                    "block_id": "task_description",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "description_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Add more details (optional)"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Description"
                    },
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "task_assignee",
                    "element": {
                        "type": "users_select",
                        "action_id": "assignee_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select assignee"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Assign To"
                    },
                    "optional": True
                },
                {
                    "type": "input",
                    "block_id": "task_due",
                    "element": {
                        "type": "datepicker",
                        "action_id": "due_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select due date"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Due Date"
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
        logger.error(f"Error opening quick task modal: {e}")


# Modal submission handlers
def handle_quick_reminder_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle quick reminder modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        reminder_text = values["reminder_text"]["text_input"]["value"]
        reminder_time = values["reminder_time"]["datetime_input"]["selected_date_time"]
        channel_id = values.get("reminder_channel", {}).get("channel_input", {}).get("selected_channel")
        user_id = body["user"]["id"]
        
        # Set reminder using assistant
        from datetime import datetime
        remind_time = datetime.fromtimestamp(reminder_time).strftime("%Y-%m-%d %H:%M")
        command = f"remind me to {reminder_text} at {remind_time}"
        
        # Process with assistant
        slack_assistant.process_slack_command(
            body={"text": command, "channel": {"id": channel_id or user_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=channel_id or user_id,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error setting reminder: {e}")


def handle_workspace_search_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle workspace search modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        query = values["search_query"]["query_input"]["value"]
        filters = values["search_filters"]["filter_input"]["selected_options"]
        timeframe = values.get("search_timeframe", {}).get("timeframe_input", {}).get("selected_option", {}).get("value", "all")
        user_id = body["user"]["id"]
        
        # Build search command
        filter_types = [opt["value"] for opt in filters]
        search_command = f"search '{query}'"
        if filter_types:
            search_command += f" in {', '.join(filter_types)}"
        if timeframe != "all":
            search_command += f" from last {timeframe}"
        
        # Process search
        slack_assistant.process_slack_command(
            body={"text": search_command, "channel": {"id": user_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=lambda text=None, blocks=None: client.chat_postMessage(
                channel=user_id,
                text=text,
                blocks=blocks
            ),
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error performing search: {e}")


def handle_analyze_message_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle analyze message modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        analysis_type = values["analysis_type"]["type_input"]["selected_option"]["value"]
        custom_prompt = values.get("custom_prompt", {}).get("prompt_input", {}).get("value", "")
        
        # Get message data from private metadata
        metadata = json.loads(body["view"]["private_metadata"])
        message_text = metadata["message_text"]
        user_id = body["user"]["id"]
        
        # Build analysis command
        if analysis_type == "sentiment":
            command = f"analyze sentiment of: {message_text}"
        elif analysis_type == "key_points":
            command = f"extract key points from: {message_text}"
        elif analysis_type == "action_items":
            command = f"find action items in: {message_text}"
        elif analysis_type == "translate":
            command = f"translate: {message_text}"
        elif analysis_type == "custom" and custom_prompt:
            command = f"{custom_prompt}: {message_text}"
        else:
            command = f"analyze: {message_text}"
        
        # Process analysis
        slack_assistant.process_slack_command(
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
        logger.error(f"Error analyzing message: {e}")


def handle_quick_task_modal_submission(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle quick task modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        task_title = values["task_title"]["title_input"]["value"]
        task_description = values.get("task_description", {}).get("description_input", {}).get("value", "")
        assignee = values.get("task_assignee", {}).get("assignee_input", {}).get("selected_user")
        due_date = values.get("task_due", {}).get("due_input", {}).get("selected_date")
        user_id = body["user"]["id"]
        
        # Build task command
        command = f"create task: {task_title}"
        if task_description:
            command += f"\nDescription: {task_description}"
        if assignee:
            command += f"\nAssigned to <@{assignee}>"
        if due_date:
            command += f"\nDue: {due_date}"
        
        # Process task creation
        slack_assistant.process_slack_command(
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
        logger.error(f"Error creating task: {e}")