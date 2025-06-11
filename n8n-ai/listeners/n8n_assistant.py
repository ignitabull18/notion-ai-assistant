"""
N8N Assistant - Core assistant logic for workflow automation
"""
import os
import re
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from slack_sdk import WebClient
from slack_bolt import Say, Ack
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory

from tools import ALL_N8N_TOOLS
from listeners.n8n_formatter import format_workflow_response
from listeners.n8n_ui import (
    create_welcome_blocks,
    create_workflow_blocks,
    create_execution_blocks,
    create_workflow_canvas_blocks
)
from listeners.n8n_canvas import N8NCanvasManager

logger = logging.getLogger(__name__)

# N8N-specific patterns
N8N_PATTERNS = [
    r'\bn8n\b',
    r'\bworkflow\b',
    r'\bautomation\b',
    r'\bnode\b',
    r'\btrigger\b',
    r'\bwebhook\b',
    r'\bintegration\b',
    r'\bexecute\b',
    r'\bschedule\b',
    r'\bautomate\b',
]


def detect_n8n_intent(message: str) -> bool:
    """Detect if message is related to N8N workflows"""
    message_lower = message.lower()
    return any(re.search(pattern, message_lower) for pattern in N8N_PATTERNS)


class N8NAssistant:
    """N8N workflow automation assistant"""
    
    def __init__(self):
        """Initialize N8N Assistant"""
        self.agent = self._create_agent()
        self.canvas_manager = None
        
    def _create_agent(self) -> Agent:
        """Create Agno agent with N8N tools"""
        # Create OpenAI model
        model = OpenAIChat(
            id="o3",
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=65536  # o3 has 200k context window, using 64k for output
        )
        
        # Create storage
        storage = SqliteStorage(table_name="n8n_sessions")
        
        # Create memory
        memory_db = SqliteMemoryDb(
            table_name="n8n_memories",
            db_file="./data/n8n_memories.db"
        )
        memory = Memory(db=memory_db, store_messages=True, num_messages=50)
        
        # Use all tools
        all_tools = ALL_N8N_TOOLS
        
        # Create agent
        agent = Agent(
            agent_id="n8n-assistant",
            model=model,
            tools=all_tools,
            storage=storage,
            memory=memory,
            system_prompt="""You are an expert N8N workflow automation assistant.
            
            You help users:
            - Build and design workflows from descriptions or screenshots
            - Import and export workflow JSON files
            - Execute and monitor workflows
            - Troubleshoot workflow issues
            - Optimize workflow performance
            - Create workflow documentation
            
            Key capabilities:
            - Access to 400+ N8N integrations
            - Visual workflow analysis from screenshots
            - Natural language to workflow conversion
            - Real-time execution monitoring
            - Workflow optimization suggestions
            
            Always:
            - Suggest best practices for workflow design
            - Include error handling in workflows
            - Optimize for performance and reliability
            - Provide clear documentation
            - Format responses for Slack readability
            """
        )
        
        return agent
    
    async def handle_message(
        self,
        message: str,
        say: Say,
        client: WebClient,
        context: Dict[str, Any]
    ) -> None:
        """Handle user message"""
        try:
            # Initialize canvas manager if needed
            if not self.canvas_manager:
                self.canvas_manager = N8NCanvasManager(client)
            
            # Show processing status
            say(text="Processing your N8N request...", blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🔄 *Processing your N8N workflow request...*"
                    }
                }
            ])
            
            # Check for screenshot in message
            if "files" in context:
                # Handle screenshot analysis
                response = await self._handle_screenshot(context["files"], message)
            else:
                # Process with agent
                response = await self.agent.run(
                    message,
                    session_id=context.get("user_id", "default")
                )
            
            # Format response
            formatted_response = format_workflow_response(response)
            
            # Send response
            say(blocks=formatted_response["blocks"], text=formatted_response.get("text", "N8N Response"))
            
            # Check if we should create a canvas
            if self._should_create_canvas(response):
                canvas_response = await self._create_workflow_canvas(response, client, context)
                if canvas_response:
                    say(blocks=canvas_response["blocks"])
                    
        except Exception as e:
            logger.error(f"Error handling N8N message: {e}")
            say(text=f"❌ Error: {str(e)}", blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"❌ *Error processing N8N request:*\n```{str(e)}```"
                    }
                }
            ])
    
    async def _handle_screenshot(self, files: List[Dict], message: str) -> Dict[str, Any]:
        """Handle screenshot analysis"""
        # Download and save screenshot
        # Analyze with workflow builder tool
        # Return structured workflow
        pass
    
    def _should_create_canvas(self, response: Any) -> bool:
        """Determine if we should create a canvas for the response"""
        # Check if response contains workflow data
        if hasattr(response, "data") and isinstance(response.data, dict):
            return "workflow" in response.data or "documentation" in response.data
        return False
    
    async def _create_workflow_canvas(
        self,
        response: Any,
        client: WebClient,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a canvas for workflow documentation or export"""
        try:
            if hasattr(response, "data") and isinstance(response.data, dict):
                data = response.data
                
                if "workflow" in data:
                    # Create workflow export canvas
                    canvas_response = await self.canvas_manager.create_workflow_canvas(
                        workflow=data["workflow"],
                        channel_id=context["channel_id"],
                        thread_ts=context.get("thread_ts")
                    )
                    return create_workflow_canvas_blocks(
                        canvas_response["file"]["permalink"],
                        data["workflow"].get("name", "Workflow"),
                        "Workflow exported to canvas"
                    )
                elif "documentation" in data:
                    # Create documentation canvas
                    canvas_response = await self.canvas_manager.create_documentation_canvas(
                        documentation=data["documentation"],
                        workflow_name=data.get("workflow_name", "Workflow"),
                        channel_id=context["channel_id"],
                        thread_ts=context.get("thread_ts")
                    )
                    return create_workflow_canvas_blocks(
                        canvas_response["file"]["permalink"],
                        f"{data.get('workflow_name', 'Workflow')} Documentation",
                        "Documentation created"
                    )
        except Exception as e:
            logger.error(f"Failed to create canvas: {e}")
        
        return None


# Singleton instance
_assistant_instance = None


def get_n8n_assistant() -> N8NAssistant:
    """Get or create N8N assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = N8NAssistant()
    return _assistant_instance


def register_n8n_assistant(app, assistant):
    """Register N8N assistant handlers"""
    n8n_assistant = get_n8n_assistant()
    
    @assistant.thread_started
    def handle_thread_started(event: Dict[str, Any], say: Say, set_suggested_prompts, set_title):
        """Handle assistant thread started"""
        user_id = event["user"]
        channel_id = event["channel"]
        
        # Set title
        set_title("N8N Workflow Assistant")
        
        # Set suggested prompts
        prompts = [
            {
                "title": "Build a Slack to Email workflow",
                "message": "Can you help me build a workflow that sends Slack messages to email?"
            },
            {
                "title": "Import workflow JSON",
                "message": "I have a workflow JSON file I'd like to import"
            },
            {
                "title": "Show my workflows",
                "message": "Can you show me all my active workflows?"
            },
            {
                "title": "Create webhook automation",
                "message": "Help me create a webhook that triggers a workflow"
            }
        ]
        set_suggested_prompts(prompts=prompts)
        
        # Send welcome message
        say(blocks=create_welcome_blocks())
    
    @assistant.user_message
    def handle_user_message(
        event: Dict[str, Any],
        say: Say,
        client: WebClient,
        context: Dict[str, Any],
        set_status
    ):
        """Handle user messages in assistant thread"""
        message = event.get("text", "")
        user_id = context.get("user_id", event.get("user"))
        
        # Set processing status
        set_status("Processing your N8N request...")
        
        # Handle with assistant
        asyncio.run(n8n_assistant.handle_message(
            message=message,
            say=say,
            client=client,
            context={
                "user_id": user_id,
                "channel_id": context.get("channel_id", event.get("channel")),
                "thread_ts": context.get("thread_ts"),
                "files": event.get("files", [])
            }
        ))
        
        # Clear status
        set_status("")