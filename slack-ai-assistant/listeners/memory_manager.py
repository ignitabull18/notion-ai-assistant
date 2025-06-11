"""
Memory management for Slack AI Assistant
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from slack_sdk.web import WebClient
from slack_bolt import BoltContext

from .events.thread_context_store import get_thread_context, save_thread_context
from utils.logging import logger


class MemoryManager:
    """Manages conversation memory and context for Slack AI Assistant"""
    
    def __init__(self, client: WebClient):
        self.client = client
        self.max_history_messages = 50  # Keep last 50 messages for context
        
    def get_conversation_history(
        self,
        channel_id: str,
        thread_ts: str,
        context: BoltContext
    ) -> List[Dict[str, str]]:
        """Get conversation history from thread"""
        try:
            # Get thread context
            thread_context = get_thread_context(
                context=context,
                client=self.client,
                channel_id=channel_id,
                thread_ts=thread_ts
            )
            
            if thread_context and "message_history" in thread_context:
                return thread_context["message_history"][-self.max_history_messages:]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def add_to_history(
        self,
        channel_id: str,
        thread_ts: str,
        context: BoltContext,
        role: str,
        content: str
    ) -> None:
        """Add a message to conversation history"""
        try:
            # Get existing context
            thread_context = get_thread_context(
                context=context,
                client=self.client,
                channel_id=channel_id,
                thread_ts=thread_ts
            ) or {}
            
            # Initialize message history if needed
            if "message_history" not in thread_context:
                thread_context["message_history"] = []
                thread_context["created_at"] = datetime.now().isoformat()
            
            # Add new message
            thread_context["message_history"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last N messages
            thread_context["message_history"] = thread_context["message_history"][-self.max_history_messages:]
            
            # Update last activity
            thread_context["last_activity"] = datetime.now().isoformat()
            
            # Save updated context
            save_thread_context(
                context=context,
                client=self.client,
                channel_id=channel_id,
                thread_ts=thread_ts,
                new_context=thread_context
            )
            
        except Exception as e:
            logger.error(f"Error adding to history: {e}")
    
    def get_context_summary(
        self,
        channel_id: str,
        thread_ts: str,
        context: BoltContext
    ) -> Dict[str, Any]:
        """Get a summary of the conversation context"""
        try:
            thread_context = get_thread_context(
                context=context,
                client=self.client,
                channel_id=channel_id,
                thread_ts=thread_ts
            ) or {}
            
            return {
                "message_count": len(thread_context.get("message_history", [])),
                "created_at": thread_context.get("created_at"),
                "last_activity": thread_context.get("last_activity"),
                "has_context": bool(thread_context.get("message_history"))
            }
            
        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return {"has_context": False}
    
    def clear_history(
        self,
        channel_id: str,
        thread_ts: str,
        context: BoltContext
    ) -> None:
        """Clear conversation history for a thread"""
        try:
            save_thread_context(
                context=context,
                client=self.client,
                channel_id=channel_id,
                thread_ts=thread_ts,
                new_context={
                    "message_history": [],
                    "cleared_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
    
    def format_history_for_llm(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format conversation history for LLM context"""
        formatted = []
        for msg in history:
            formatted.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return formatted