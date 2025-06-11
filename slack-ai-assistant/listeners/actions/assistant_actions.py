"""
Action handlers for Slack AI Assistant interactive components
"""
from slack_bolt import Ack, Say, BoltContext
from slack_sdk.web import WebClient
from typing import Dict, Any

from listeners.slack_assistant import SlackAssistant
from listeners.canvas_integration import CanvasManager
from listeners.ui_components import (
    create_reminder_form_modal,
    create_canvas_preview_blocks,
    create_assistant_status_blocks
)
from utils.logging import logger


slack_assistant = SlackAssistant()


def handle_quick_summarize(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle quick summarize button click"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        user_id = body["user"]["id"]
        
        # Show thinking status
        say(blocks=create_assistant_status_blocks("processing", "Analyzing channel history..."))
        
        # Process summarization
        command = "summarize this channel from today"
        slack_assistant.process_slack_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error in quick summarize: {e}")
        say("❌ Sorry, I couldn't summarize the channel right now.")


def handle_create_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create canvas button click"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        canvas_manager = CanvasManager(client)
        
        # Show creating status
        say(blocks=create_assistant_status_blocks("creating", "Creating collaborative canvas..."))
        
        # Create a general project canvas
        response = canvas_manager.create_project_canvas(
            channel_id=channel_id,
            project_name="Team Collaboration",
            objectives=["Improve team communication", "Track project progress", "Share knowledge"],
            tasks=[
                {"title": "Add project objectives", "status": "todo"},
                {"title": "Define milestones", "status": "todo"},
                {"title": "Assign team members", "status": "todo"}
            ]
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            say(
                blocks=create_canvas_preview_blocks(
                    canvas_url=canvas_url or "#",
                    title="Team Collaboration Canvas",
                    preview="A collaborative workspace for your team projects and planning."
                )
            )
        else:
            say("❌ Sorry, I couldn't create the canvas right now.")
            
    except Exception as e:
        logger.error(f"Error creating canvas: {e}")
        say("❌ Sorry, I couldn't create the canvas right now.")


def handle_quick_reminder(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle quick reminder button click - open modal"""
    ack()
    
    try:
        trigger_id = body["trigger_id"]
        
        # Open reminder form modal
        client.views_open(
            trigger_id=trigger_id,
            view=create_reminder_form_modal()
        )
        
    except Exception as e:
        logger.error(f"Error opening reminder modal: {e}")


def handle_create_summary_canvas(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle create summary canvas button"""
    ack()
    
    try:
        channel_id = body["channel"]["id"]
        canvas_manager = CanvasManager(client)
        
        # Show creating status
        say(blocks=create_assistant_status_blocks("creating", "Creating summary canvas..."))
        
        # Get the summary text from the message that contained the button
        # The summary should be in the blocks of the original message
        original_message = body.get("message", {})
        summary_text = ""
        
        # Extract summary from the message blocks
        for block in original_message.get("blocks", []):
            if block.get("type") == "section" and "Channel Summary" not in block.get("text", {}).get("text", ""):
                summary_text = block.get("text", {}).get("text", "")
                break
        
        if not summary_text:
            summary_text = "Channel summary content"
        
        # Get channel name
        try:
            channel_info = client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
        except:
            channel_name = "channel"
        
        # Create summary canvas
        response = canvas_manager.create_summary_canvas(
            channel_id=channel_id,
            summary=summary_text,
            timeframe="Recent conversations",
            key_topics=["Key discussion points", "Important decisions", "Action items"],
            action_items=["Review summary details", "Follow up on action items", "Schedule next discussion"]
        )
        
        if response:
            canvas_url = canvas_manager.get_canvas_url(response)
            say(
                blocks=create_canvas_preview_blocks(
                    canvas_url=canvas_url or "#",
                    title=f"📊 {channel_name} Summary Canvas",
                    preview=f"Collaborative summary document for {channel_name} discussions."
                )
            )
        else:
            say("❌ Sorry, I couldn't create the summary canvas right now.")
            
    except Exception as e:
        logger.error(f"Error creating summary canvas: {e}")
        say("❌ Sorry, I couldn't create the summary canvas right now.")


def handle_share_summary(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle share summary button"""
    ack()
    
    try:
        # For now, just acknowledge the action
        say("📤 Summary sharing feature coming soon! You can copy the summary text above to share manually.")
        
    except Exception as e:
        logger.error(f"Error sharing summary: {e}")


def handle_set_followup(ack: Ack, body: Dict[str, Any], client: WebClient, logger):
    """Handle set follow-up button"""
    ack()
    
    try:
        trigger_id = body["trigger_id"]
        
        # Open reminder modal for follow-up
        client.views_open(
            trigger_id=trigger_id,
            view=create_reminder_form_modal()
        )
        
    except Exception as e:
        logger.error(f"Error setting follow-up: {e}")


def handle_view_message(ack: Ack, body: Dict[str, Any], logger):
    """Handle view message button from search results"""
    ack()
    
    try:
        action = body["actions"][0]
        permalink = action["value"]
        
        # For now, just acknowledge - in a real app, you might open the message
        logger.info(f"User wants to view message: {permalink}")
        
    except Exception as e:
        logger.error(f"Error viewing message: {e}")


def handle_reminder_modal_submission(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle reminder modal form submission"""
    ack()
    
    try:
        values = body["view"]["state"]["values"]
        
        # Extract form data
        reminder_text = values["reminder_text"]["text_input"]["value"]
        reminder_time = values["reminder_time"]["datetime_input"]["selected_date_time"]
        reminder_target = values["reminder_target"]["target_input"]["selected_option"]["value"]
        
        user_id = body["user"]["id"]
        channel_id = body["view"]["private_metadata"] or body.get("channel", {}).get("id")
        
        # Process reminder creation
        command = f"remind {reminder_text} at {reminder_time}"
        slack_assistant.process_slack_command(
            body={"text": command, "channel": {"id": channel_id}, "user": {"id": user_id}},
            context=BoltContext(),
            say=say,
            client=client
        )
        
    except Exception as e:
        logger.error(f"Error processing reminder modal: {e}")
        say("❌ Sorry, I couldn't create the reminder right now.")


def handle_show_workflows(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle show workflows button click"""
    ack()
    
    try:
        from listeners.workflow_manager import SlackWorkflowManager
        from listeners.ui_components import create_workflow_template_blocks
        
        workflow_manager = SlackWorkflowManager()
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
        from listeners.workflow_manager import SlackWorkflowManager
        from listeners.ui_components import create_workflow_status_blocks
        
        template_id = body["actions"][0]["value"]
        user_id = body["user"]["id"]
        channel_id = body["channel"]["id"]
        
        # Show initial status
        say(text="Starting workflow execution...")
        
        # Execute workflow
        workflow_manager = SlackWorkflowManager()
        context = {
            "user_id": user_id,
            "channel_id": channel_id,
            "trigger": "manual"
        }
        
        # Run workflow asynchronously
        import asyncio
        from listeners.slack_assistant import SlackAssistant
        
        slack_assistant = SlackAssistant()
        
        result = asyncio.run(
            workflow_manager.execute_workflow(
                template_id,
                context,
                client,
                slack_assistant
            )
        )
        
        # Show status
        status = workflow_manager.get_workflow_status(template_id)
        if status:
            blocks = create_workflow_status_blocks(status)
            say(blocks=blocks)
        
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        say("❌ Sorry, the workflow execution failed.")