"""
Jungle Scout AI Assistant message handler with enhanced UI
"""
from slack_bolt import App, BoltContext, Say
from slack_sdk.web import WebClient
from typing import Dict, Any
import re

from listeners.jungle_scout_assistant import jungle_scout_assistant
from listeners.jungle_scout_ui import (
    create_jungle_scout_welcome_blocks,
    create_status_blocks,
    get_jungle_scout_suggested_prompts
)


def handle_jungle_scout_message(
    body: Dict[str, Any],
    context: BoltContext,
    say: Say,
    client: WebClient,
    logger
):
    """Handle messages directed to the Jungle Scout AI Assistant"""
    try:
        message_text = body.get("text", "").strip()
        channel_type = body.get("channel_type", "")
        
        # Check for greeting or help request
        if re.search(r'\b(help|hi|hello|hey|start)\b', message_text.lower()):
            # Determine context for suggested prompts
            prompt_context = "general"
            if "research" in message_text.lower():
                prompt_context = "research"
            elif "keyword" in message_text.lower():
                prompt_context = "keywords"
            elif "sales" in message_text.lower():
                prompt_context = "sales"
            
            suggested_prompts = get_jungle_scout_suggested_prompts(prompt_context)
            
            # Send welcome message with rich UI
            say(blocks=create_jungle_scout_welcome_blocks())
            
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
            say(blocks=create_jungle_scout_welcome_blocks())
            return
        
        # Show processing status for analysis commands
        if any(cmd in message_text.lower() for cmd in ['research', 'analyze', 'competitor', 'trends', 'validate']):
            status_message = "Analyzing market data..."
            if "research" in message_text.lower():
                status_message = "Researching product opportunities..."
            elif "competitor" in message_text.lower():
                status_message = "Analyzing competitor data..."
            elif "trends" in message_text.lower():
                status_message = "Analyzing market trends..."
            elif "validate" in message_text.lower():
                status_message = "Validating product opportunity..."
            
            say(blocks=create_status_blocks("analyzing", status_message))
        
        # Process the command through the jungle scout assistant
        jungle_scout_assistant.process_jungle_scout_command(
            body=body,
            context=context,
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in jungle scout assistant handler: {e}")
        say(blocks=create_status_blocks("error", "Sorry, I encountered an error processing your request."))


def register(app: App):
    """Register the jungle scout assistant message handler"""
    # Handle direct messages to the bot
    app.message("")(handle_jungle_scout_message)