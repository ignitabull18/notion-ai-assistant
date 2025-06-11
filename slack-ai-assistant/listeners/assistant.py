"""
Slack AI Assistant using the Assistant API
"""
import logging
from typing import List, Dict
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .llm_caller_openai import LLMCallerOpenAI
from .slack_assistant import SlackAssistant
from .slack_formatter import SlackFormatter
from .canvas_integration import CanvasManager
from utils.errors import handle_errors
from utils.logging import logger

# Initialize the Assistant
assistant = Assistant()

# Initialize our Slack assistant handler
slack_assistant_handler = SlackAssistant()
llm_caller = LLMCallerOpenAI()


@assistant.thread_started
def start_assistant_thread(
    say: Say,
    context: BoltContext,
    get_thread_context: GetThreadContext,
    set_suggested_prompts: SetSuggestedPrompts,
    logger: logging.Logger,
):
    """Handle when a user starts a new assistant thread"""
    try:
        # Use rich welcome message
        blocks = SlackFormatter.format_welcome_message(context.user_id)
        say(blocks=blocks, text="Welcome to Slack AI Assistant!")

        # Set suggested prompts
        prompts: List[Dict[str, str]] = [
            {
                "title": "Summarize recent discussions",
                "message": "Can you summarize the important discussions from this channel in the last 24 hours?",
            },
            {
                "title": "Set a reminder",
                "message": "Remind me to review the team's pull requests tomorrow at 10am",
            },
            {
                "title": "Search for information",
                "message": "Search for messages about the latest deployment issues",
            },
        ]

        # Add context-specific prompt if we have thread context
        thread_context = get_thread_context()
        if thread_context is not None and thread_context.channel_id is not None:
            prompts.append({
                "title": "Summarize the referred channel",
                "message": "Can you generate a brief summary of the referred channel?",
            })

        set_suggested_prompts(prompts=prompts)
        
    except Exception as e:
        logger.error(f"Error in thread_started: {e}")
        blocks = SlackFormatter.format_error_message(str(e))
        say(blocks=blocks, text="Something went wrong!")


@assistant.user_message
def respond_in_assistant_thread(
    payload: dict,
    logger: logging.Logger,
    context: BoltContext,
    set_status: SetStatus,
    get_thread_context: GetThreadContext,
    set_suggested_prompts: SetSuggestedPrompts,
    client: WebClient,
    say: Say,
):
    """Handle user messages in assistant threads"""
    try:
        user_message = payload["text"]
        
        # Show processing status
        set_status("Processing your request...")
        
        # Send initial status update with Block Kit
        status_blocks = SlackFormatter.format_status_update(
            "Processing request", 
            "in_progress", 
            "Analyzing your message..."
        )
        status_message = say(blocks=status_blocks, text="Processing...")
        
        # Check if this is a channel summary request
        if user_message == "Can you generate a brief summary of the referred channel?":
            thread_context = get_thread_context()
            referred_channel_id = thread_context.get("channel_id")
            
            if referred_channel_id:
                try:
                    # Get channel history
                    channel_history = client.conversations_history(
                        channel=referred_channel_id,
                        limit=50
                    )
                    
                    # Build prompt with channel messages
                    prompt = f"Can you generate a brief summary of these messages in Slack channel <#{referred_channel_id}>?\n\n"
                    for message in reversed(channel_history.get("messages", [])):
                        if message.get("user") is not None:
                            prompt += f"\n<@{message['user']}> says: {message['text']}\n"
                    
                    # Generate summary using LLM  
                    summary = llm_caller.call([{"role": "user", "content": prompt}])
                    
                    # Format with rich UI
                    blocks = SlackFormatter.format_channel_summary(
                        referred_channel_id, 
                        channel_history.get("messages", []), 
                        summary
                    )
                    say(blocks=blocks, text=f"Channel summary for <#{referred_channel_id}>")
                    return
                    
                except SlackApiError as e:
                    if e.response["error"] == "not_in_channel":
                        # Try joining the channel first
                        try:
                            client.conversations_join(channel=referred_channel_id)
                            channel_history = client.conversations_history(
                                channel=referred_channel_id,
                                limit=50
                            )
                            # Proceed with summary...
                        except:
                            say("I need to be added to that channel to summarize it. Please invite me first!")
                            return
                    else:
                        raise
        
        # Check for specific commands in the message
        if any(cmd in user_message.lower() for cmd in ["summarize", "remind", "search", "schedule", "analyze"]):
            # Process through our Slack assistant handler
            slack_assistant_handler.process_slack_command(
                body=payload,
                context=context,
                say=say,
                client=client
            )
        else:
            # Use LLM for general conversation
            # Get thread history for context
            try:
                replies = client.conversations_replies(
                    channel=context.channel_id,
                    ts=context.thread_ts,
                    oldest=context.thread_ts,
                    limit=10,
                )
                
                # Build conversation history
                messages_in_thread: List[Dict[str, str]] = []
                for message in replies["messages"]:
                    role = "user" if message.get("bot_id") is None else "assistant"
                    messages_in_thread.append({"role": role, "content": message["text"]})
                
                # Generate response
                response = llm_caller.call(messages_in_thread)
                
                # Format with Block Kit
                blocks = SlackFormatter.format_assistant_response(response)
                say(blocks=blocks, text=response[:150] + "..." if len(response) > 150 else response)
                
            except Exception as e:
                logger.error(f"Error getting thread context: {e}")
                # Fallback to responding without context
                response = llm_caller.call([{"role": "user", "content": user_message}])
                
                # Format with Block Kit
                blocks = SlackFormatter.format_assistant_response(response)
                say(blocks=blocks, text=response[:150] + "..." if len(response) > 150 else response)
        
        # Update suggested prompts based on the conversation
        set_suggested_prompts(prompts=[
            {
                "title": "Get more details",
                "message": "Can you provide more information about that?"
            },
            {
                "title": "Try another command",
                "message": "What other Slack automation tasks can you help with?"
            },
            {
                "title": "Create a reminder",
                "message": "Remind me about this tomorrow"
            }
        ])
        
    except Exception as e:
        logger.error(f"Error in user_message handler: {e}")
        try:
            blocks = SlackFormatter.format_error_message(str(e))
            say(blocks=blocks, text="Sorry, I encountered an error")
        except Exception as say_error:
            logger.error(f"Error sending error message: {say_error}")
            # Try a simpler response without metadata
            try:
                client.chat_postMessage(
                    channel=context.channel_id,
                    thread_ts=context.thread_ts,
                    text=f"Sorry, I encountered an error: {str(e)}"
                )
            except:
                pass