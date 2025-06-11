"""
Slack AI Assistant - Intelligent Slack automation and assistance
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from slack_bolt import BoltContext
from slack_sdk.web import WebClient
from composio import ComposioToolSet, AppType

from listeners.llm_caller_openai import LLMCallerOpenAI
from listeners.slack_formatter import format_for_slack
from listeners.memory_manager import MemoryManager
from utils.logging import logger
from utils.errors import handle_errors
from utils.retry import with_retry


class SlackAssistant:
    """Handles Slack AI assistance with channel summaries, reminders, and automation"""
    
    def __init__(self):
        self.llm = LLMCallerOpenAI()
        self.composio_toolset = ComposioToolSet()
        self.memory_manager = None  # Initialized with client
        
    @handle_errors
    def process_slack_command(
        self,
        body: Dict[str, Any],
        context: BoltContext,
        say: Any,
        client: WebClient
    ) -> None:
        """Process Slack assistant commands"""
        try:
            user_id = body.get("user", {}).get("id", "") or body.get("user", "")
            channel_id = body.get("channel", {}).get("id", "") if isinstance(body.get("channel"), dict) else body.get("channel", "")
            text = body.get("text", "").strip()
            thread_ts = body.get("thread_ts") or body.get("ts")
            
            logger.info(f"Processing command: '{text}' from user: {user_id} in channel: {channel_id}")
            
            # Initialize memory manager with client if not already done
            if not self.memory_manager:
                self.memory_manager = MemoryManager(client)
            
            # Extract command from message
            command = self._extract_command(text)
            
            if not command:
                say("I can help you with:\n"
                    "• `summarize` - Summarize channel conversations\n"
                    "• `remind` - Create smart reminders\n"
                    "• `search` - Search across channels\n"
                    "• `schedule` - Schedule messages\n"
                    "• `analyze` - Analyze team activity\n\n"
                    "Just type one of these commands followed by your request!")
                return
                
            # Route to appropriate handler
            if command.startswith("summarize"):
                self._handle_summarize(command, channel_id, say, client, thread_ts, context)
            elif command.startswith("remind"):
                self._handle_reminder(command, user_id, channel_id, say, thread_ts, context)
            elif command.startswith("search"):
                self._handle_search(command, say, thread_ts, context)
            elif command.startswith("schedule"):
                self._handle_schedule(command, channel_id, say, thread_ts, context)
            elif command.startswith("analyze"):
                self._handle_analyze(command, channel_id, say, client, thread_ts, context)
            else:
                say(f"Unknown command: `{command}`. Type `help` for available commands.")
                
        except Exception as e:
            logger.error(f"Error processing Slack command: {e}")
            say("Sorry, I encountered an error processing your request.")
    
    def _extract_command(self, text: str) -> Optional[str]:
        """Extract command from message text"""
        # Remove bot mention if present
        text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
        
        # Check for command keywords
        commands = ["summarize", "remind", "search", "schedule", "analyze", "help"]
        for cmd in commands:
            if text.lower().startswith(cmd):
                return text.lower()
        
        return None
    
    @with_retry(max_attempts=3)
    def _handle_summarize(
        self, 
        command: str, 
        channel_id: str, 
        say: Any,
        client: WebClient,
        thread_ts: str = None,
        context: BoltContext = None
    ) -> None:
        """Handle channel summarization"""
        say("🔄 Fetching channel history...")
        
        # Add user command to memory if in thread
        if thread_ts and self.memory_manager:
            self.memory_manager.add_to_history(
                channel_id=channel_id,
                thread_ts=thread_ts,
                context=context,
                role="user",
                content=command
            )
        
        try:
            # Parse timeframe from command
            timeframe = self._parse_timeframe(command)
            
            # Get connected account
            entity = self.composio_toolset.get_entity()
            
            # Fetch channel history using Composio
            action = self.composio_toolset.get_action(
                action=AppType.SLACK,
                action_name="SLACK_FETCHES_A_CONVERSATIONS_HISTORY"
            )
            
            result = entity.execute(
                action=action,
                params={
                    "channel": channel_id,
                    "limit": 100,  # Adjust based on timeframe
                    "oldest": timeframe["oldest_ts"] if timeframe else None
                }
            )
            
            if result.get("error"):
                say(f"❌ Error fetching history: {result['error']}")
                return
                
            messages = result.get("messages", [])
            
            if not messages:
                say("No messages found in the specified timeframe.")
                return
            
            # Get conversation history for context
            conversation_history = []
            if thread_ts and self.memory_manager:
                conversation_history = self.memory_manager.get_conversation_history(
                    channel_id=channel_id,
                    thread_ts=thread_ts,
                    context=context
                )
            
            # Build messages for LLM with context
            llm_messages = []
            if conversation_history:
                llm_messages = self.memory_manager.format_history_for_llm(conversation_history)
            
            # Generate summary using LLM
            summary_prompt = f"""
            Summarize the following Slack channel conversation:
            
            Messages: {json.dumps(messages[:50], indent=2)}  # Limit for context
            
            Provide:
            1. Key topics discussed
            2. Important decisions or action items
            3. Notable mentions or links
            4. Overall sentiment/tone
            
            Format as a clear, concise summary suitable for Slack.
            """
            
            # Add current request to messages
            llm_messages.append({
                "role": "user",
                "content": summary_prompt
            })
            
            summary = self.llm.call(llm_messages)
            
            # Format and send summary
            formatted_summary = format_for_slack(
                f"📊 **Channel Summary**\n\n{summary}",
                format_type="channel_summary"
            )
            
            say(formatted_summary)
            
            # Save summary to memory
            if thread_ts and self.memory_manager:
                self.memory_manager.add_to_history(
                    channel_id=channel_id,
                    thread_ts=thread_ts,
                    context=context,
                    role="assistant",
                    content=f"Generated channel summary for timeframe: {timeframe.get('description', 'recent')}"
                )
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            say("❌ Failed to generate summary. Please try again.")
    
    @with_retry(max_attempts=3)
    def _handle_reminder(
        self, 
        command: str, 
        user_id: str,
        channel_id: str,
        say: Any,
        thread_ts: str = None,
        context: BoltContext = None
    ) -> None:
        """Handle reminder creation"""
        say("⏰ Creating reminder...")
        
        try:
            # Extract reminder details from command
            reminder_text = command.replace("remind", "").strip()
            
            if not reminder_text:
                say("Please specify what you'd like to be reminded about.\n"
                    "Example: `remind me to review PRs tomorrow at 2pm`")
                return
            
            # Get connected account
            entity = self.composio_toolset.get_entity()
            
            # Create reminder using Composio
            action = self.composio_toolset.get_action(
                action=AppType.SLACK,
                action_name="SLACK_CREATE_A_REMINDER"
            )
            
            result = entity.execute(
                action=action,
                params={
                    "text": reminder_text,
                    "user": user_id,
                    "time": reminder_text  # Slack parses natural language
                }
            )
            
            if result.get("error"):
                say(f"❌ Error creating reminder: {result['error']}")
                return
                
            say(f"✅ Reminder set! I'll remind you: *{reminder_text}*")
            
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            say("❌ Failed to create reminder. Please try again.")
    
    @with_retry(max_attempts=3)
    def _handle_search(self, command: str, say: Any, thread_ts: str = None, context: BoltContext = None) -> None:
        """Handle message search"""
        say("🔍 Searching...")
        
        try:
            # Extract search query
            query = command.replace("search", "").strip()
            
            if not query:
                say("Please specify what you'd like to search for.\n"
                    "Example: `search deployment issues last week`")
                return
            
            # Get connected account
            entity = self.composio_toolset.get_entity()
            
            # Search messages using Composio
            action = self.composio_toolset.get_action(
                action=AppType.SLACK,
                action_name="SLACK_SEARCH_FOR_MESSAGES_WITH_QUERY"
            )
            
            result = entity.execute(
                action=action,
                params={
                    "query": query,
                    "count": 10,
                    "sort": "timestamp"
                }
            )
            
            if result.get("error"):
                say(f"❌ Error searching: {result['error']}")
                return
                
            messages = result.get("messages", {}).get("matches", [])
            
            if not messages:
                say(f"No messages found matching: *{query}*")
                return
            
            # Format search results
            formatted_results = self._format_search_results(messages, query)
            say(formatted_results)
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            say("❌ Failed to search messages. Please try again.")
    
    @with_retry(max_attempts=3)
    def _handle_schedule(
        self, 
        command: str, 
        channel_id: str,
        say: Any,
        thread_ts: str = None,
        context: BoltContext = None
    ) -> None:
        """Handle message scheduling"""
        say("📅 Scheduling message...")
        
        try:
            # Parse schedule details
            parts = command.replace("schedule", "").strip().split(" at ")
            
            if len(parts) < 2:
                say("Please specify message and time.\n"
                    "Example: `schedule Daily standup reminder at tomorrow 9am`")
                return
                
            message_text = parts[0].strip()
            time_spec = parts[1].strip()
            
            # Calculate timestamp
            scheduled_time = self._parse_time_spec(time_spec)
            
            # Get connected account
            entity = self.composio_toolset.get_entity()
            
            # Schedule message using Composio
            action = self.composio_toolset.get_action(
                action=AppType.SLACK,
                action_name="SLACK_SCHEDULES_A_MESSAGE_TO_A_CHANNEL_AT_A_SPECIFIED_TIME"
            )
            
            result = entity.execute(
                action=action,
                params={
                    "channel": channel_id,
                    "text": message_text,
                    "post_at": int(scheduled_time.timestamp())
                }
            )
            
            if result.get("error"):
                say(f"❌ Error scheduling message: {result['error']}")
                return
                
            formatted_time = scheduled_time.strftime("%B %d at %I:%M %p")
            say(f"✅ Message scheduled for *{formatted_time}*:\n_{message_text}_")
            
        except Exception as e:
            logger.error(f"Error scheduling message: {e}")
            say("❌ Failed to schedule message. Please try again.")
    
    def _handle_analyze(
        self, 
        command: str, 
        channel_id: str,
        say: Any,
        client: WebClient,
        thread_ts: str = None,
        context: BoltContext = None
    ) -> None:
        """Handle team activity analysis"""
        say("📈 Analyzing team activity...")
        
        try:
            # Get channel info
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
            
            # Fetch recent history
            entity = self.composio_toolset.get_entity()
            
            action = self.composio_toolset.get_action(
                action=AppType.SLACK,
                action_name="SLACK_FETCHES_A_CONVERSATIONS_HISTORY"
            )
            
            result = entity.execute(
                action=action,
                params={
                    "channel": channel_id,
                    "limit": 200
                }
            )
            
            if result.get("error"):
                say(f"❌ Error fetching data: {result['error']}")
                return
                
            messages = result.get("messages", [])
            
            # Analyze activity
            analysis = self._analyze_activity(messages)
            
            # Generate insights using LLM
            insights_prompt = f"""
            Based on this Slack channel activity analysis:
            {json.dumps(analysis, indent=2)}
            
            Provide:
            1. Team collaboration patterns
            2. Peak activity times
            3. Key contributors
            4. Communication health insights
            5. Recommendations for improvement
            
            Format as actionable insights for team leads.
            """
            
            insights = self.llm.call(insights_prompt)
            
            # Format and send analysis
            formatted_analysis = format_for_slack(
                f"📈 **Team Activity Analysis - #{channel_name}**\n\n"
                f"**Period**: Last {len(messages)} messages\n\n"
                f"{insights}",
                format_type="activity_analysis"
            )
            
            say(formatted_analysis)
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            say("❌ Failed to analyze activity. Please try again.")
    
    def _parse_timeframe(self, command: str) -> Optional[Dict[str, Any]]:
        """Parse timeframe from command"""
        now = datetime.now()
        
        if "today" in command:
            oldest = now.replace(hour=0, minute=0, second=0)
        elif "yesterday" in command:
            oldest = (now - timedelta(days=1)).replace(hour=0, minute=0)
        elif "week" in command:
            oldest = now - timedelta(days=7)
        elif "month" in command:
            oldest = now - timedelta(days=30)
        else:
            return None
            
        return {"oldest_ts": int(oldest.timestamp())}
    
    def _parse_time_spec(self, time_spec: str) -> datetime:
        """Parse natural language time specification"""
        now = datetime.now()
        
        if "tomorrow" in time_spec:
            base = now + timedelta(days=1)
        else:
            base = now
            
        # Extract time
        time_match = re.search(r'(\d{1,2})\s*(am|pm)', time_spec.lower())
        if time_match:
            hour = int(time_match.group(1))
            if time_match.group(2) == "pm" and hour != 12:
                hour += 12
            elif time_match.group(2) == "am" and hour == 12:
                hour = 0
                
            return base.replace(hour=hour, minute=0, second=0)
            
        # Default to next hour
        return base.replace(minute=0, second=0) + timedelta(hours=1)
    
    def _format_search_results(
        self, 
        messages: List[Dict], 
        query: str
    ) -> str:
        """Format search results for Slack"""
        if not messages:
            return f"No results found for: *{query}*"
            
        results = [f"🔍 Search results for: *{query}*\n"]
        
        for i, msg in enumerate(messages[:5], 1):
            timestamp = datetime.fromtimestamp(float(msg.get("ts", 0)))
            text = msg.get("text", "")[:100] + "..."
            user = msg.get("username", "Unknown")
            
            results.append(
                f"{i}. *{user}* - {timestamp.strftime('%b %d at %I:%M %p')}\n"
                f"   _{text}_\n"
            )
            
        return "\n".join(results)
    
    def _analyze_activity(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze channel activity patterns"""
        analysis = {
            "total_messages": len(messages),
            "unique_users": len(set(m.get("user", "") for m in messages)),
            "message_types": {},
            "hourly_distribution": {},
            "top_contributors": {}
        }
        
        for msg in messages:
            # Message types
            msg_type = msg.get("type", "message")
            analysis["message_types"][msg_type] = analysis["message_types"].get(msg_type, 0) + 1
            
            # Hourly distribution
            if "ts" in msg:
                hour = datetime.fromtimestamp(float(msg["ts"])).hour
                analysis["hourly_distribution"][hour] = analysis["hourly_distribution"].get(hour, 0) + 1
            
            # Top contributors
            user = msg.get("user", "unknown")
            analysis["top_contributors"][user] = analysis["top_contributors"].get(user, 0) + 1
        
        # Get top 5 contributors
        analysis["top_contributors"] = dict(
            sorted(analysis["top_contributors"].items(), 
                   key=lambda x: x[1], 
                   reverse=True)[:5]
        )
        
        return analysis


# Initialize assistant
slack_assistant = SlackAssistant()