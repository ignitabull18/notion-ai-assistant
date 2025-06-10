"""
Listener for delegating complex requests to the Agno agent via HTTP bridge.
"""

import os
import logging
from typing import Dict, Any
import httpx
from slack_bolt import App, Ack, Say

logger = logging.getLogger(__name__)

# Configuration from environment
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
AGNO_API_KEY = os.getenv("AGNO_API_KEY")  # Optional API key for security


async def delegate_to_agent(
    user_id: str,
    text: str,
    channel: str,
    session_id: str = None
) -> str:
    """Send request to Agno agent and return response."""
    async with httpx.AsyncClient() as client:
        headers = {}
        if AGNO_API_KEY:
            headers["Authorization"] = f"Bearer {AGNO_API_KEY}"
        
        payload = {
            "user_id": user_id,
            "text": text,
            "channel": channel,
            "session_id": session_id
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/agent/ask",
                json=payload,
                headers=headers,
                timeout=30.0  # 30 second timeout
            )
            response.raise_for_status()
            
            data = response.json()
            return data["response"]
            
        except httpx.TimeoutException:
            logger.error("Timeout waiting for agent response")
            return "Sorry, the request timed out. Please try again."
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from agent: {e}")
            return f"Sorry, there was an error processing your request. (Status: {e.response.status_code})"
        except Exception as e:
            logger.error(f"Unexpected error calling agent: {e}")
            return "Sorry, an unexpected error occurred. Please try again later."


def handle_ask_command(ack: Ack, command: Dict[str, Any], say: Say):
    """Handle /ask slash command."""
    # Acknowledge within 3 seconds
    ack()
    
    user_id = command["user_id"]
    text = command["text"]
    channel = command["channel_id"]
    
    # Show typing indicator
    say(text="🤔 Thinking...", channel=channel)
    
    # Delegate to agent (sync wrapper for async function)
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        response = loop.run_until_complete(
            delegate_to_agent(user_id, text, channel)
        )
        
        # Send the response
        say(
            text=response,
            channel=channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Question:* {text}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response
                    }
                }
            ]
        )
    finally:
        loop.close()


def handle_kb_search_command(ack: Ack, command: Dict[str, Any], say: Say):
    """Handle /kb-search slash command for knowledge base queries."""
    ack()
    
    user_id = command["user_id"]
    query = command["text"]
    channel = command["channel_id"]
    
    # Prefix the query to trigger knowledge base search
    text = f"Search the knowledge base for: {query}"
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        response = loop.run_until_complete(
            delegate_to_agent(user_id, text, channel)
        )
        
        say(
            text=response,
            channel=channel,
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📚 Knowledge Base Search"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Query:* {query}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response
                    }
                }
            ]
        )
    finally:
        loop.close()


def handle_tasks_command(ack: Ack, command: Dict[str, Any], say: Say):
    """Handle /tasks slash command for task management."""
    ack()
    
    user_id = command["user_id"]
    text = command["text"] or "list"  # Default to list if no subcommand
    channel = command["channel_id"]
    
    # Prefix to trigger task management
    agent_query = f"Task management command: {text}"
    
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        response = loop.run_until_complete(
            delegate_to_agent(user_id, agent_query, channel)
        )
        
        say(
            text=response,
            channel=channel,
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📋 Task Management"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": response
                    }
                }
            ]
        )
    finally:
        loop.close()


def register_listeners(app: App):
    """Register all agent delegation listeners."""
    # Slash commands
    app.command("/ask")(handle_ask_command)
    app.command("/kb-search")(handle_kb_search_command)
    app.command("/tasks")(handle_tasks_command)
    
    # You can also add message handlers here if needed
    # For example, to handle direct messages to the bot
    
    logger.info("Agent delegation listeners registered")