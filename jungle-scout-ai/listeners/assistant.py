"""
Jungle Scout AI Assistant using the Slack Assistant API
"""
import logging
from typing import List, Dict
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .llm_caller_openai import LLMCallerOpenAI
from .jungle_scout_assistant import JungleScoutAssistant
from .jungle_scout_formatter import JungleScoutFormatter
from .jungle_scout_canvas import JungleScoutCanvasManager
from .assistant_features import JungleScoutAssistantFeatures
from jungle_scout_ai.errors import handle_errors
from jungle_scout_ai.logging import logger

# Initialize the Assistant
assistant = Assistant()

# Initialize our Jungle Scout assistant handler
jungle_scout = JungleScoutAssistant()
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
        blocks = JungleScoutFormatter.format_welcome_message(context.user_id)
        say(blocks=blocks, text="Welcome to Jungle Scout AI Assistant!")

        # Set suggested prompts for Amazon sellers
        prompts: List[Dict[str, str]] = [
            {
                "title": "🔍 Find product opportunities",
                "message": "research wireless earbuds under $50",
            },
            {
                "title": "📊 Analyze a competitor",
                "message": "competitor B08XXXXXX",
            },
            {
                "title": "🎯 Find keywords",
                "message": "keywords for yoga mat",
            },
        ]

        # Add context-specific prompt if we have thread context
        thread_context = get_thread_context()
        if thread_context is not None and thread_context.channel_id is not None:
            prompts.append({
                "title": "📈 Analyze channel discussions",
                "message": "Can you analyze the product discussions in this channel?",
            })

        set_suggested_prompts(prompts=prompts)
        
    except Exception as e:
        logger.error(f"Error in thread_started: {e}")
        blocks = JungleScoutFormatter.format_error_message(str(e))
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
        set_status("🔍 Analyzing your request...")
        
        # Send initial status update with Block Kit
        status_blocks = JungleScoutFormatter.format_status_update(
            "Processing request", 
            "researching", 
            "Searching Amazon marketplace..."
        )
        status_message = say(blocks=status_blocks, text="Processing...")
        
        # Initialize assistant features with client
        assistant_features = JungleScoutAssistantFeatures(client)
        
        # Check if this is a channel analysis request
        if "analyze the product discussions in this channel" in user_message.lower():
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
                    prompt = f"Analyze these Amazon seller discussions from channel <#{referred_channel_id}> and identify:\n"
                    prompt += "1. Product opportunities mentioned\n"
                    prompt += "2. Market trends discussed\n"
                    prompt += "3. Common challenges\n"
                    prompt += "4. Actionable insights\n\n"
                    
                    for message in reversed(channel_history.get("messages", [])):
                        if message.get("user") is not None:
                            prompt += f"\n<@{message['user']}> says: {message['text']}\n"
                    
                    # Generate analysis using LLM
                    messages = [{"role": "user", "content": prompt}]
                    analysis = llm_caller.call(messages)
                    
                    # Format with rich UI
                    blocks = JungleScoutFormatter.format_channel_analysis(
                        referred_channel_id,
                        analysis
                    )
                    say(blocks=blocks, text="Channel analysis complete")
                    
                    # Set smart suggestions based on analysis
                    assistant_features.set_suggested_prompts(
                        channel_id=context.channel_id,
                        thread_ts=context.thread_ts,
                        prompts=[
                            {
                                "title": "🔍 Research mentioned products",
                                "message": "research the top product opportunity from the analysis"
                            },
                            {
                                "title": "📈 Check market trends",
                                "message": "trends for the main category discussed"
                            },
                            {
                                "title": "🎯 Find related keywords",
                                "message": "keywords for the niche mentioned"
                            }
                        ]
                    )
                    return
                    
                except SlackApiError as e:
                    if e.response["error"] == "not_in_channel":
                        say("I need to be added to that channel to analyze it. Please invite me first!")
                        return
                    else:
                        raise
        
        # Check for Jungle Scout commands
        commands = ["research", "competitor", "keywords", "sales", "trends", "validate", "dashboard"]
        has_command = any(cmd in user_message.lower() for cmd in commands)
        
        if has_command:
            # Animate processing for complex operations
            if any(cmd in user_message.lower() for cmd in ["research", "competitor", "trends"]):
                assistant_features.animate_processing(
                    channel_id=context.channel_id,
                    thread_ts=context.thread_ts,
                    steps=[
                        "🔍 Searching Amazon marketplace",
                        "📊 Analyzing sales data",
                        "🧮 Calculating opportunity scores",
                        "📝 Generating insights"
                    ],
                    delay=1.0
                )
            
            # Process through our Jungle Scout assistant handler
            jungle_scout.process_jungle_scout_command(
                body=payload,
                context=context,
                say=say,
                client=client
            )
            
            # Set smart suggestions based on command type
            if "research" in user_message.lower():
                context_data = {"type": "product_research", "search_query": user_message}
            elif "competitor" in user_message.lower():
                context_data = {"type": "competitor_analysis", "asin": user_message.split()[-1]}
            elif "keywords" in user_message.lower():
                context_data = {"type": "keyword_analysis", "keyword": user_message.split()[-1]}
            else:
                context_data = {}
            
            suggestions = assistant_features.create_smart_suggestions(context_data)
            if suggestions:
                assistant_features.set_suggested_prompts(
                    channel_id=context.channel_id,
                    thread_ts=context.thread_ts,
                    prompts=suggestions
                )
        else:
            # Use LLM for general Amazon seller questions
            try:
                # Get thread history for context
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
                
                # Add system prompt for Amazon context
                system_prompt = {
                    "role": "system",
                    "content": "You are Jungle Scout AI Assistant, an expert in Amazon selling, product research, and e-commerce optimization. Provide actionable insights for Amazon sellers."
                }
                messages_in_thread.insert(0, system_prompt)
                
                # Generate response
                response = llm_caller.call(messages_in_thread)
                
                # Format with Block Kit
                blocks = JungleScoutFormatter.format_assistant_response(response)
                say(blocks=blocks, text=response[:150] + "..." if len(response) > 150 else response)
                
                # Set general suggestions
                assistant_features.set_suggested_prompts(
                    channel_id=context.channel_id,
                    thread_ts=context.thread_ts,
                    prompts=[
                        {
                            "title": "🔍 Research a product",
                            "message": "research [product keyword]"
                        },
                        {
                            "title": "📊 Analyze competition",
                            "message": "competitor [ASIN]"
                        },
                        {
                            "title": "🎯 Find keywords",
                            "message": "keywords [search term]"
                        },
                        {
                            "title": "📈 View market trends",
                            "message": "trends [category]"
                        }
                    ]
                )
                
            except Exception as e:
                logger.error(f"Error getting thread context: {e}")
                # Fallback to responding without context
                response = llm_caller.call([{"role": "user", "content": user_message}])
                
                # Format with Block Kit
                blocks = JungleScoutFormatter.format_assistant_response(response)
                say(blocks=blocks, text=response[:150] + "..." if len(response) > 150 else response)
        
    except Exception as e:
        logger.error(f"Error in user_message handler: {e}")
        try:
            blocks = JungleScoutFormatter.format_error_message(str(e))
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