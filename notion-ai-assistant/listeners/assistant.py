import logging
from typing import List, Dict
from slack_bolt import Assistant, BoltContext, Say, SetSuggestedPrompts, SetStatus
from slack_bolt.context.get_thread_context import GetThreadContext
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .llm_caller_litellm import call_llm
from .agno_integration import process_with_agent, detect_notion_intent, format_agent_response
from utils.errors import error_handler, SlackAPIError
from utils.monitoring import metrics
from utils.retry import api_retry

# Refer to https://tools.slack.dev/bolt-python/concepts/assistant/ for more details
assistant = Assistant()


# This listener is invoked when a human user opened an assistant thread
@assistant.thread_started
def start_assistant_thread(
    say: Say,
    get_thread_context: GetThreadContext,
    set_suggested_prompts: SetSuggestedPrompts,
    logger: logging.Logger,
):
    try:
        with metrics.timer("assistant.thread_started"):
            metrics.increment("assistant.threads.started")
            
            say("How can I help you?")

            prompts: List[Dict[str, str]] = [
                {
                    "title": "Create a Notion page",
                    "message": "Can you create a new Notion page for our project meeting notes?",
                },
                {
                    "title": "Search Notion",
                    "message": "Can you search for our Q4 planning documents in Notion?",
                },
                {
                    "title": "Update task status",
                    "message": "Can you update the status of my tasks in our Notion project tracker?",
                },
                {
                    "title": "List Notion databases",
                    "message": "Can you show me all the databases in our Notion workspace?",
                },
            ]

            thread_context = get_thread_context()
            if thread_context is not None and thread_context.channel_id is not None:
                summarize_channel = {
                    "title": "Summarize the referred channel",
                    "message": "Can you generate a brief summary of the referred channel?",
                }
                prompts.append(summarize_channel)

            set_suggested_prompts(prompts=prompts)
            metrics.increment("assistant.threads.started.success")
            
    except Exception as e:
        metrics.increment("assistant.threads.started.error")
        app_error = error_handler.handle_error(e, context={"phase": "thread_started"})
        say(f":warning: {app_error.user_message}")


# This listener is invoked when the human user sends a reply in the assistant thread
@assistant.user_message
def respond_in_assistant_thread(
    payload: dict,
    logger: logging.Logger,
    context: BoltContext,
    set_status: SetStatus,
    get_thread_context: GetThreadContext,
    client: WebClient,
    say: Say,
):
    try:
        with metrics.timer("assistant.user_message"):
            metrics.increment("assistant.messages.received")
            
            user_message = payload["text"]
            set_status("is typing...")

            if user_message == "Can you generate a brief summary of the referred channel?":
                # the logic here requires the additional bot scopes:
                # channels:join, channels:history, groups:history
                with metrics.timer("assistant.channel_summary"):
                    thread_context = get_thread_context()
                    referred_channel_id = thread_context.get("channel_id")
                    
                    @api_retry.retry
                    def get_channel_history():
                        try:
                            return client.conversations_history(channel=referred_channel_id, limit=50)
                        except SlackApiError as e:
                            if e.response["error"] == "not_in_channel":
                                # If this app's bot user is not in the public channel,
                                # we'll try joining the channel and then calling the same API again
                                client.conversations_join(channel=referred_channel_id)
                                return client.conversations_history(channel=referred_channel_id, limit=50)
                            else:
                                raise SlackAPIError(f"Failed to get channel history: {e}", api_error=e.response.get("error"))
                    
                    channel_history = get_channel_history()

                    prompt = f"Can you generate a brief summary of these messages in a Slack channel <#{referred_channel_id}>?\n\n"
                    for message in reversed(channel_history.get("messages")):
                        if message.get("user") is not None:
                            prompt += f"\n<@{message['user']}> says: {message['text']}\n"
                    
                    # Use Agno agent for Notion-related summaries
                    if detect_notion_intent(prompt):
                        import asyncio
                        returned_message = asyncio.run(
                            process_with_agent(
                                user_id=context.user_id,
                                message=prompt,
                                channel_id=context.channel_id,
                                thread_ts=context.thread_ts
                            )
                        )
                        # Handle both dict (with blocks) and string responses
                        if isinstance(returned_message, dict) and 'blocks' in returned_message:
                            say(blocks=returned_message['blocks'], text=returned_message.get('text', 'Response'))
                        else:
                            formatted_response = format_agent_response(returned_message)
                            say(blocks=formatted_response['blocks'], text=formatted_response.get('text', 'Response'))
                        metrics.increment("assistant.channel_summary.agno")
                    else:
                        messages_in_thread = [{"role": "user", "content": prompt}]
                        returned_message = call_llm(messages_in_thread)
                        say(returned_message)
                        metrics.increment("assistant.channel_summary.llm")
                return

            # Check if this is a Notion-related request
            if detect_notion_intent(user_message):
                with metrics.timer("assistant.notion_request"):
                    # Use Agno agent for Notion operations
                    import asyncio
                    returned_message = asyncio.run(
                        process_with_agent(
                            user_id=context.user_id,
                            message=user_message,
                            channel_id=context.channel_id,
                            thread_ts=context.thread_ts
                        )
                    )
                    # Handle both dict (with blocks) and string responses
                    if isinstance(returned_message, dict) and 'blocks' in returned_message:
                        say(blocks=returned_message['blocks'], text=returned_message.get('text', 'Response'))
                    else:
                        formatted_response = format_agent_response(returned_message)
                        say(blocks=formatted_response['blocks'], text=formatted_response.get('text', 'Response'))
                    metrics.increment("assistant.notion_requests")
            else:
                with metrics.timer("assistant.general_request"):
                    # Use regular LLM for general questions
                    @api_retry.retry
                    def get_thread_replies():
                        return client.conversations_replies(
                            channel=context.channel_id,
                            ts=context.thread_ts,
                            oldest=context.thread_ts,
                            limit=10,
                        )
                    
                    replies = get_thread_replies()
                    messages_in_thread: List[Dict[str, str]] = []
                    for message in replies["messages"]:
                        role = "user" if message.get("bot_id") is None else "assistant"
                        messages_in_thread.append({"role": role, "content": message["text"]})
                    returned_message = call_llm(messages_in_thread)
                    say(returned_message)
                    metrics.increment("assistant.general_requests")
            
            metrics.increment("assistant.messages.success")

    except Exception as e:
        metrics.increment("assistant.messages.error")
        app_error = error_handler.handle_error(
            e, 
            context={"user_message": payload.get("text", ""), "user_id": context.user_id},
            user_id=context.user_id,
            channel_id=context.channel_id
        )
        say(f":warning: {app_error.user_message}")
