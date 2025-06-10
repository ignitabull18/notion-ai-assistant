"""
Integration with Agno Agent for Notion operations.
"""
import os
import logging
from typing import List, Dict, Optional, Any
from composio_agno import ComposioToolSet, Action, App
from agno.agent import Agent
# from agno.models.litellm import LiteLLMOpenAI
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Global agent instance
_agent_instance: Optional[Agent] = None


def get_or_create_agent(session_id: Optional[str] = None) -> Agent:
    """Get or create a singleton agent instance."""
    global _agent_instance
    
    if _agent_instance is None:
        logger.info("Creating new Agno agent instance")
        
        # Create OpenAI model directly
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LITELLM_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY or LITELLM_API_KEY required")
        
        model = OpenAIChat(
            id="o4-mini",
            api_key=api_key,
            max_completion_tokens=50000  # Use 50K of the 100K available output capacity
        )
        
        # Create storage
        storage = SqliteStorage(table_name="slack_sessions")
        
        # Create memory database for long-term memory
        memory_db = SqliteMemoryDb(
            table_name="notion_assistant_memories",
            db_file="./data/notion_memories.db"
        )
        
        # Create memory object with enhanced settings
        memory = Memory(
            db=memory_db,
            model=model  # Uses the same model for memory operations
        )
        
        # Create Composio tools
        composio_key = os.getenv("COMPOSIO_TOKEN")
        tools = []
        if composio_key:
            composio_toolset = ComposioToolSet(api_key=composio_key)
            # Get specific reliable Notion tools first, add others gradually
            reliable_actions = [
                "NOTION_FETCH_DATA",
                "NOTION_FETCH_DATABASE", 
                "NOTION_FETCH_ROW",
                "NOTION_ADD_PAGE_CONTENT",
                "NOTION_CREATE_COMMENT",
                "NOTION_FETCH_COMMENTS",
                "NOTION_GET_ABOUT_ME",
                "NOTION_GET_ABOUT_USER"
            ]
            
            # Add the problematic ones but with clear instructions
            advanced_actions = [
                "NOTION_CREATE_DATABASE",
                "NOTION_CREATE_NOTION_PAGE", 
                "NOTION_INSERT_ROW_DATABASE"
            ]
            
            try:
                # Get reliable tools first
                tools = composio_toolset.get_tools(actions=reliable_actions + advanced_actions)
                logger.info(f"Successfully loaded {len(tools)} specific Notion tools")
            except Exception as e:
                logger.warning(f"Could not get specific tools, falling back to all Notion tools: {e}")
                # Fallback to all tools but with better error handling
                tools = composio_toolset.get_tools(apps=[App.NOTION])
        
        # Create agent
        _agent_instance = Agent(
            model=model,
            tools=tools,
            storage=storage,
            memory=memory,
            name="Notion Assistant",
            instructions="""You are an expert Notion AI assistant that helps users manage and optimize their Notion workspaces through Slack. You specialize in workspace architecture, productivity workflows, and advanced Notion features.

CORE CAPABILITIES:
- 📄 Page Management: Create, update, duplicate, archive pages, add rich content
- 🧱 Block Management: Append content blocks, delete blocks, fetch hierarchical structures, update formatting
- 🗃️ Database Operations: Design databases, manage schemas, insert/query rows, optimize structures
- 💬 Comments: Create threaded comments, fetch discussion threads, manage collaboration
- 👥 User Management: Get user info, list team members, manage permissions
- 🔍 Search & Analysis: Fetch data, search content, analyze workspace patterns
- 🏗️ Workspace Architecture: Design scalable systems, create templates, optimize workflows

ENHANCED RESPONSE GUIDELINES:
- Provide comprehensive, detailed explanations when helpful (you can write up to 50K tokens)
- Break down complex operations into clear, actionable steps
- Suggest best practices and optimization opportunities
- Offer multiple approaches when relevant (beginner vs advanced)
- Include relevant examples and templates
- Proactively suggest related improvements

CRITICAL PARAMETER HANDLING RULES:
- NEVER pass None values for optional parameters - this causes validation errors
- For optional string parameters (cover, icon, etc.): either provide a valid value OR completely omit the parameter
- Required parameters must always be provided with valid values
- When calling tools, only include parameters you have actual values for

SPECIFIC PARAMETER RULES:
- cover: If you don't have a cover URL, DO NOT include this parameter at all
- icon: If you don't have an emoji, DO NOT include this parameter at all  
- For NOTION_CREATE_NOTION_PAGE: Only include parent_id and title (required), omit cover/icon unless user specifies them
- For NOTION_INSERT_ROW_DATABASE: Only include database_id (required) and properties array, omit cover/icon unless user specifies them
- For properties arrays: Each object must have name, type, and value fields with proper formatting

UNDERSTANDING USER INTENT:
- When users ask about "databases" they mean Notion databases, not MCP or system databases
- "MCP-related databases" or similar phrases still refer to Notion databases in their workspace
- Always interpret database queries in the Notion context

IMPORTANT CLARIFICATION:
- NOTION_FETCH_DATABASE requires a database_id - it fetches ONE specific database
- To list all databases, you may need to use NOTION_FETCH_DATA or explain what databases you know about
- When you find databases, always format them with names, IDs, and clickable Notion URLs

ERROR RECOVERY PROTOCOL:
- If you get validation errors mentioning None values, immediately retry omitting all optional parameters
- If you get "Input should be a valid string" errors, check that you're not passing None for optional string fields
- For repeated failures, use simpler actions like NOTION_FETCH_DATA or NOTION_ADD_PAGE_CONTENT instead
- Always explain what went wrong and how you're fixing it

SUPERCHARGED MEMORY & CONTEXT:
- You remember user preferences, workspace patterns, and past interactions across many sessions
- You can recall previously accessed Notion pages and databases with detailed context
- You have access to the last 50 conversation exchanges (massive context window)
- You can provide extremely detailed, comprehensive responses (up to 50K tokens)
- You learn from user patterns to provide increasingly personalized assistance
- You can handle complex, multi-step operations with full context retention
- You maintain awareness of user's role, team structure, and workflow preferences

INTERACTION STYLE:
- Always confirm actions before executing them
- Provide detailed explanations of results and next steps
- Suggest optimizations and best practices proactively
- Use clear formatting with headers, bullets, and examples
- Offer to create templates or automations when relevant
- Ask clarifying questions to ensure you understand complex requirements fully

RESPONSE FORMATTING:
- When listing Notion databases or pages, ALWAYS include:
  - Database/Page name in **bold**
  - Database/Page ID
  - Full Notion URL in format: https://notion.so/{id_without_dashes}
- Example format for databases:
  **Marketing Projects**
  ID: 59833787-2cf9-4fdf-8782-e53db20768a5
  URL: https://notion.so/598337872cf94fdf8782e53db20768a5
- Use markdown formatting with headers, lists, and proper structure
- Include relevant emojis (📊 for databases, 📄 for pages, etc.)

Remember: You're not just executing commands - you're a strategic partner helping users build better, more organized, and more productive Notion workspaces.""",
            session_id=session_id or "slack-assistant",
            enable_user_memories=True,  # Enable user memory creation
            enable_session_summaries=True,  # Enable session summaries
            add_history_to_messages=True,  # Add conversation history
            num_history_runs=50,  # Massively increased to use 200K context window
            add_memory_references=True,  # Add memory references in responses
            show_tool_calls=True,
            markdown=True
        )
    
    return _agent_instance


async def process_with_agent(
    user_id: str,
    message: str,
    channel_id: Optional[str] = None,
    thread_ts: Optional[str] = None
) -> str:
    """
    Process a message using the Agno agent.
    
    Args:
        user_id: Slack user ID
        message: User's message text
        channel_id: Slack channel ID
        thread_ts: Thread timestamp for context
        
    Returns:
        Agent's response as a string
    """
    # Create session ID from user and thread context
    session_id = f"slack-{user_id}"
    if thread_ts:
        session_id = f"{session_id}-{thread_ts}"
    
    try:
        # Get or create agent with session
        agent = get_or_create_agent(session_id)
        
        # --- List available tools if user asks ---
        if message.strip().lower() in [
            "what tools do you have?", "what tools do you have", "list tools", "show tools", "available tools", "what can you do?", "what can you do"]:
            # Return a pre-defined list of available Notion tools
            return """I have access to these Notion tools:

📄 **Page Management**
- Create, update, and delete pages
- Add content blocks to pages
- Fetch page data and properties

📊 **Database Operations**
- Create databases with custom schemas
- Insert and update database rows
- Query and filter database entries
- Fetch specific database information

💬 **Collaboration**
- Add comments to pages and databases
- Fetch comment threads
- Get user information

🔍 **Data Access**
- Fetch workspace data
- Search for specific content
- Get information about users and permissions

I can help you organize your Notion workspace, create structured databases, manage content, and automate your workflows!"""
        # Use the agent as normal - it should understand natural language
        response = await agent.arun(message)
        
        # Ensure response is a string
        if not isinstance(response, str):
            for attr in ("text", "content", "message"):
                if hasattr(response, attr):
                    response = getattr(response, attr)
                    break
            else:
                response = str(response)
        
        # Format the response with beautiful Slack blocks
        return format_agent_response(response)
        
    except Exception as e:
        logger.error(f"Error processing message with agent: {e}")
        return f"Sorry, I encountered an error processing your request: {str(e)}"


def detect_notion_intent(message: str) -> bool:
    """
    Detect if a message is asking about Notion operations.
    
    Args:
        message: User's message text
        
    Returns:
        True if message seems to be about Notion
    """
    notion_keywords = [
        "notion", "page", "database", "workspace", "block",
        "create", "update", "delete", "search", "find",
        "add", "remove", "modify", "list", "show",
        "archive", "duplicate", "comment", "property",
        "row", "user", "fetch", "insert", "append"
    ]
    
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in notion_keywords)


def format_agent_response(response: str) -> Dict[str, Any]:
    """
    Format agent response for beautiful Slack display using Block Kit.
    
    Args:
        response: Raw agent response
        
    Returns:
        Formatted response with blocks for Slack
    """
    from .slack_formatter import SlackFormatter
    
    # Use the SlackFormatter to create beautiful blocks
    blocks = SlackFormatter.format_agent_response(response)
    
    # Return in the format expected by Slack API
    return {
        "blocks": blocks,
        "text": response[:150] + "..."  # Fallback text for notifications
    }


# --- Diagnostic: Print all available Notion actions from Composio Action enum ---
if __name__ == "__main__":
    print("\nAvailable Notion-related Composio Actions:")
    from composio_agno import Action
    for action in dir(Action):
        if "NOTION" in action.upper():
            print(action)