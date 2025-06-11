"""
Slack Assistant message handler with enhanced UI
"""
from slack_bolt import App, BoltContext, Say
from slack_sdk.web import WebClient
from typing import Dict, Any
import re

from listeners.slack_assistant import SlackAssistant
from listeners.ui_components import (
    create_assistant_welcome_blocks,
    create_assistant_status_blocks,
    get_suggested_prompts
)


slack_assistant = SlackAssistant()


def handle_slack_assistant_message(
    body: Dict[str, Any],
    context: BoltContext,
    say: Say,
    client: WebClient,
    logger
):
    """Handle messages directed to the Slack AI Assistant"""
    logger.info(f"Received message: {body.get('text', '')}")
    logger.debug(f"Full body: {body}")
    
    try:
        message_text = body.get("text", "").strip()
        channel_type = body.get("channel_type", "")
        
        # Check for greeting or help request
        if re.search(r'\b(help|hi|hello|hey|start)\b', message_text.lower()):
            # Determine context for suggested prompts
            prompt_context = "dm" if channel_type == "im" else "channel"
            suggested_prompts = get_suggested_prompts(prompt_context)
            
            # Send welcome message with rich UI
            say(blocks=create_assistant_welcome_blocks())
            
            # Set suggested prompts if this is an assistant thread
            try:
                if hasattr(client, 'assistant_threads_setSuggestedPrompts'):
                    thread_ts = body.get("thread_ts") or body.get("ts")
                    if thread_ts:
                        client.assistant_threads_setSuggestedPrompts(
                            channel_id=body["channel"]["id"],
                            thread_ts=thread_ts,
                            prompts=suggested_prompts
                        )
            except Exception as e:
                logger.debug(f"Could not set suggested prompts: {e}")
            
            return
        
        # Check if message is empty or just bot mention
        if not message_text or re.match(r'^<@[A-Z0-9]+>$', message_text):
            say(blocks=create_assistant_welcome_blocks())
            return
        
        # Show processing status for complex commands
        if any(cmd in message_text.lower() for cmd in ['summarize', 'search', 'analyze', 'create']):
            say(blocks=create_assistant_status_blocks("thinking", "Processing your request..."))
        
        # Process the command through the slack assistant
        slack_assistant.process_slack_command(
            body=body,
            context=context,
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in slack assistant handler: {e}")
        say(blocks=create_assistant_status_blocks("error", "Sorry, I encountered an error processing your request."))


def register(app: App):
    """Register the slack assistant message handler"""
    # Handle direct messages to the bot
    app.message("")(handle_slack_assistant_message)