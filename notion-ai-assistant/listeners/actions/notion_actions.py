"""
Action handlers for Notion AI Assistant interactive components
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any
import asyncio

from listeners.agno_integration import process_with_agent
from listeners.notion_canvas import NotionCanvasManager
from listeners.ui_components import (
    create_notion_status_blocks,
    create_canvas_preview_blocks,
    create_page_creation_modal,
    create_database_creation_modal
)
from utils.logging import logger


def handle_open_database(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle open database button click"""
    ack()
    
    try:
        # Extract database ID from action_id
        action_id = body["actions"][0]["action_id"]
        db_id = action_id.replace("open_db_", "")
        user_id = body["user"]["id"]
        
        # Show thinking status
        say(blocks=create_notion_status_blocks("processing", f"Fetching database details..."))
        
        # Process with agent
        command = f"Show me the details of database with ID {db_id}"
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command,
                channel_id=body.get("channel", {}).get("id"),
                thread_ts=body.get("message", {}).get("ts")
            )
        )
        
        # Send response (format_agent_response already returns blocks)
        if isinstance(response, dict) and 'blocks' in response:
            say(blocks=response['blocks'], text=response.get('text', 'Database details'))
        else:
            say(text=response)
        
    except Exception as e:
        logger.error(f"Error opening database: {e}")
        say("❌ Sorry, I couldn't fetch the database details.")


def handle_open_page(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle open page button click"""
    ack()
    
    try:
        # Extract page ID from action_id or value
        action = body["actions"][0]
        page_id = action.get("value") or action["action_id"].replace("open_", "")
        user_id = body["user"]["id"]
        
        # Show thinking status
        say(blocks=create_notion_status_blocks("processing", f"Fetching page content..."))
        
        # Process with agent
        command = f"Show me the content of Notion page {page_id}"
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command,
                channel_id=body.get("channel", {}).get("id"),
                thread_ts=body.get("message", {}).get("ts")
            )
        )
        
        # Send response
        if isinstance(response, dict) and 'blocks' in response:
            say(blocks=response['blocks'], text=response.get('text', 'Page content'))
        else:
            say(text=response)
        
    except Exception as e:
        logger.error(f"Error opening page: {e}")
        say("❌ Sorry, I couldn't fetch the page content.")


def handle_create_workspace_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create workspace summary canvas button"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show thinking status
        say(blocks=create_notion_status_blocks("processing", "Creating workspace summary canvas..."))
        
        # Get workspace data from agent
        workspace_data = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message="List all databases and recent pages in my Notion workspace with their details",
                channel_id=channel_id
            )
        )
        
        # Parse the response to extract databases and pages
        # This is a simplified version - in production you'd parse more carefully
        databases = []
        pages = []
        
        # Create canvas
        canvas_manager = NotionCanvasManager(client)
        response = canvas_manager.create_workspace_summary_canvas(
            channel_id=channel_id,
            workspace_name="Your Notion Workspace",
            databases=databases,
            pages=pages,
            insights={
                "active_users": "Team Members",
                "last_activity": "Today",
                "storage_used": "Premium Plan",
                "workspace_age": "6 months"
            }
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            if canvas_url:
                say(blocks=create_canvas_preview_blocks(
                    canvas_url,
                    "Workspace Summary Canvas",
                    "Your Notion workspace overview has been created as a collaborative canvas."
                ))
            else:
                say("✅ Canvas created successfully!")
        else:
            say("❌ Failed to create canvas.")
            
    except Exception as e:
        logger.error(f"Error creating workspace canvas: {e}")
        say("❌ Sorry, I couldn't create the workspace summary canvas.")


def handle_create_database_schema_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create database schema canvas button"""
    ack()
    
    try:
        # Extract database info from button value
        action = body["actions"][0]
        db_info = action.get("value", "").split("|")
        db_id = db_info[0] if db_info else ""
        db_name = db_info[1] if len(db_info) > 1 else "Database"
        
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show thinking status  
        say(blocks=create_notion_status_blocks("processing", f"Creating schema documentation for {db_name}..."))
        
        # Get database schema from agent
        schema_data = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=f"Get the complete schema and properties for database {db_id}",
                channel_id=channel_id
            )
        )
        
        # Create canvas
        canvas_manager = NotionCanvasManager(client)
        
        # Mock properties for now - in production, parse from agent response
        properties = [
            {"name": "Title", "type": "title", "description": "Main title"},
            {"name": "Status", "type": "select", "config": {"options": ["To Do", "In Progress", "Done"]}},
            {"name": "Assignee", "type": "person", "description": "Task owner"},
            {"name": "Due Date", "type": "date", "description": "Deadline"}
        ]
        
        response = canvas_manager.create_database_schema_canvas(
            channel_id=channel_id,
            database_name=db_name,
            database_id=db_id,
            properties=properties
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            if canvas_url:
                say(blocks=create_canvas_preview_blocks(
                    canvas_url,
                    f"Database Schema: {db_name}",
                    "Database schema documentation has been created."
                ))
            else:
                say("✅ Schema canvas created successfully!")
        else:
            say("❌ Failed to create schema canvas.")
            
    except Exception as e:
        logger.error(f"Error creating database schema canvas: {e}")
        say("❌ Sorry, I couldn't create the database schema canvas.")


def handle_create_project_template(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create project template button"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        template_type = body["actions"][0].get("value", "general")
        
        # Show thinking status
        say(blocks=create_notion_status_blocks("processing", f"Creating {template_type} project template..."))
        
        # Create canvas
        canvas_manager = NotionCanvasManager(client)
        
        # Define structure based on template type
        structure = {
            "databases": ["Tasks", "Team", "Documents"],
            "pages": ["Project Home", "Meeting Notes", "Resources"],
            "views": ["Kanban Board", "Calendar", "Timeline"]
        }
        
        tasks = [
            {"name": "Project Kickoff", "category": "Planning", "duration": "1 day"},
            {"name": "Requirements Gathering", "category": "Planning", "duration": "1 week"},
            {"name": "Design Phase", "category": "Development", "duration": "2 weeks"},
            {"name": "Implementation", "category": "Development", "duration": "4 weeks"},
            {"name": "Testing", "category": "QA", "duration": "1 week"},
            {"name": "Deployment", "category": "Release", "duration": "2 days"}
        ]
        
        response = canvas_manager.create_project_template_canvas(
            channel_id=channel_id,
            project_name=f"{template_type.title()} Project",
            template_type=template_type,
            structure=structure,
            tasks=tasks
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            if canvas_url:
                say(blocks=create_canvas_preview_blocks(
                    canvas_url,
                    f"{template_type.title()} Project Template",
                    "Your project template has been created. Customize it for your needs!"
                ))
            else:
                say("✅ Project template created successfully!")
        else:
            say("❌ Failed to create project template.")
            
    except Exception as e:
        logger.error(f"Error creating project template: {e}")
        say("❌ Sorry, I couldn't create the project template.")


def handle_open_page_modal(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle opening the page creation modal"""
    ack()
    
    try:
        # Open modal for page creation
        client.views_open(
            trigger_id=body["trigger_id"],
            view=create_page_creation_modal()
        )
    except Exception as e:
        logger.error(f"Error opening page modal: {e}")


def handle_open_database_modal(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle opening the database creation modal"""
    ack()
    
    try:
        # Open modal for database creation
        client.views_open(
            trigger_id=body["trigger_id"],
            view=create_database_creation_modal()
        )
    except Exception as e:
        logger.error(f"Error opening database modal: {e}")


def handle_page_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle page creation modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        title = values["title_block"]["page_title"]["value"]
        parent_type = values["parent_block"]["parent_type"]["selected_option"]["value"]
        content = values.get("content_block", {}).get("page_content", {}).get("value", "")
        
        user_id = body["user"]["id"]
        
        # Create the page using the agent
        command = f"Create a new Notion page titled '{title}' "
        if parent_type == "workspace":
            command += "in the workspace root"
        else:
            command += f"as a {parent_type}"
        
        if content:
            command += f" with this content: {content}"
        
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command
            )
        )
        
        # Post response to the channel where modal was triggered
        channel_id = body.get("view", {}).get("private_metadata", "")
        if channel_id:
            if isinstance(response, dict) and 'blocks' in response:
                client.chat_postMessage(
                    channel=channel_id,
                    blocks=response['blocks'],
                    text=response.get('text', 'Page created')
                )
            else:
                client.chat_postMessage(
                    channel=channel_id,
                    text=response
                )
        
    except Exception as e:
        logger.error(f"Error handling page modal submission: {e}")


def handle_database_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle database creation modal submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        name = values["name_block"]["db_name"]["value"]
        db_type = values["type_block"]["db_type"]["selected_option"]["value"]
        properties = values.get("properties_block", {}).get("db_properties", {}).get("value", "")
        
        user_id = body["user"]["id"]
        
        # Create the database using the agent
        command = f"Create a new Notion database called '{name}' for {db_type}"
        
        if properties:
            command += f" with these properties: {properties}"
        
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=command
            )
        )
        
        # Post response to the channel
        channel_id = body.get("view", {}).get("private_metadata", "")
        if channel_id:
            if isinstance(response, dict) and 'blocks' in response:
                client.chat_postMessage(
                    channel=channel_id,
                    blocks=response['blocks'],
                    text=response.get('text', 'Database created')
                )
            else:
                client.chat_postMessage(
                    channel=channel_id,
                    text=response
                )
        
    except Exception as e:
        logger.error(f"Error handling database modal submission: {e}")


def handle_show_workflows(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle show workflows button click"""
    ack()
    
    try:
        from listeners.workflow_manager import NotionWorkflowManager
        from listeners.ui_components import create_workflow_template_blocks
        
        workflow_manager = NotionWorkflowManager()
        workflows = workflow_manager.list_workflows()
        
        blocks = create_workflow_template_blocks(workflows)
        say(blocks=blocks)
        
    except Exception as e:
        logger.error(f"Error showing workflows: {e}")
        say("❌ Sorry, I couldn't load the workflow templates.")


def handle_use_workflow_template(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle workflow template selection"""
    ack()
    
    try:
        template_id = body["actions"][0]["value"]
        
        # Open modal to configure the workflow
        from listeners.ui_components import create_workflow_builder_modal
        
        client.views_open(
            trigger_id=body["trigger_id"],
            view=create_workflow_builder_modal()
        )
        
    except Exception as e:
        logger.error(f"Error using workflow template: {e}")


def handle_execute_workflow(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle workflow execution"""
    ack()
    
    try:
        from listeners.workflow_manager import NotionWorkflowManager
        from listeners.ui_components import create_workflow_status_blocks
        
        workflow_id = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Show initial status
        say(text="Starting workflow execution...")
        
        # Execute workflow
        workflow_manager = NotionWorkflowManager()
        context = {
            "user_id": user_id,
            "channel_id": channel_id,
            "trigger": "manual"
        }
        
        # Run workflow asynchronously
        import asyncio
        from listeners.agno_integration import process_with_agent
        
        result = asyncio.run(
            workflow_manager.execute_workflow(
                workflow_id,
                context,
                process_with_agent
            )
        )
        
        # Show status
        status = workflow_manager.get_workflow_status(workflow_id)
        if status:
            blocks = create_workflow_status_blocks(status)
            say(blocks=blocks)
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        say("❌ Sorry, the workflow execution failed.")


def handle_get_page_info(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle get page info from link unfurl"""
    ack()
    
    try:
        action = body["actions"][0]
        page_id = action["value"]
        user_id = body["user"]["id"]
        
        # Use agent to get page info
        import asyncio
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=f"Get information about Notion page {page_id}",
                channel_id=body.get("channel", {}).get("id")
            )
        )
        
        if isinstance(response, dict) and 'blocks' in response:
            say(blocks=response['blocks'], text=response.get('text', 'Page info'))
        else:
            say(text=response)
            
    except Exception as e:
        logger.error(f"Error getting page info: {e}")
        say("❌ Sorry, I couldn't get the page information.")


def handle_add_page_comment(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle adding comment to page from link unfurl"""
    ack()
    
    try:
        # Could open a modal to get comment text
        say("💬 To add a comment, use: `/notion comment [page_id] [your comment]`")
        
    except Exception as e:
        logger.error(f"Error handling comment action: {e}")


def handle_view_db_schema(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle view database schema from link unfurl"""
    ack()
    
    try:
        action = body["actions"][0]
        db_id = action["value"]
        user_id = body["user"]["id"]
        
        # Use agent to get schema
        import asyncio
        response = asyncio.run(
            process_with_agent(
                user_id=user_id,
                message=f"Show me the schema for database {db_id}",
                channel_id=body.get("channel", {}).get("id")
            )
        )
        
        if isinstance(response, dict) and 'blocks' in response:
            say(blocks=response['blocks'], text=response.get('text', 'Database schema'))
        else:
            say(text=response)
            
    except Exception as e:
        logger.error(f"Error getting database schema: {e}")
        say("❌ Sorry, I couldn't get the database schema.")


def register_action_handlers(app):
    """Register all action handlers for the Notion AI Assistant"""
    
    # Database and page actions
    app.action("open_db_")(handle_open_database)
    app.action("open_")(handle_open_page)
    
    # Canvas creation actions
    app.action("create_workspace_canvas")(handle_create_workspace_canvas)
    app.action("create_schema_canvas")(handle_create_database_schema_canvas)
    app.action("create_project_template")(handle_create_project_template)
    
    # Workflow actions
    app.action("show_workflows")(handle_show_workflows)
    app.action("create_custom_workflow")(handle_use_workflow_template)
    
    # Modal actions
    app.action("open_page_modal")(handle_open_page_modal)
    app.action("open_database_modal")(handle_open_database_modal)
    
    # Modal submissions
    app.view("create_page_modal")(handle_page_modal_submission)
    app.view("create_database_modal")(handle_database_modal_submission)
    app.view("workflow_builder_modal")(handle_execute_workflow)
    
    # Pattern matching for dynamic action IDs
    import re
    
    # Match any open_db_{id} pattern
    app.action(re.compile(r"open_db_.*"))(handle_open_database)
    
    # Match any open_{id} pattern for pages
    app.action(re.compile(r"open_[a-f0-9\-]{32,}"))(handle_open_page)
    
    # Match workflow template usage
    app.action(re.compile(r"use_workflow_.*"))(handle_use_workflow_template)
    
    # Match workflow control actions
    app.action(re.compile(r"pause_workflow_.*"))(handle_execute_workflow)
    app.action(re.compile(r"cancel_workflow_.*"))(handle_execute_workflow)
    app.action(re.compile(r"view_results_.*"))(handle_execute_workflow)
    app.action(re.compile(r"rerun_workflow_.*"))(handle_execute_workflow)
    
    # Link unfurling actions
    app.action(re.compile(r"get_page_info_.*"))(handle_get_page_info)
    app.action(re.compile(r"add_page_comment_.*"))(handle_add_page_comment)
    app.action(re.compile(r"duplicate_page_.*"))(handle_open_page)
    app.action(re.compile(r"view_db_schema_.*"))(handle_view_db_schema)
    app.action(re.compile(r"add_db_entry_.*"))(handle_open_database_modal)
    app.action(re.compile(r"query_database_.*"))(handle_open_database)
    app.action(re.compile(r"create_db_canvas_.*"))(handle_create_database_schema_canvas)
    
    logger.info("Notion action handlers registered")