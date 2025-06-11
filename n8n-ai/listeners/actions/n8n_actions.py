"""
N8N Action Handlers - Handle button clicks and interactions
"""
import json
import logging
from typing import Dict, Any
from slack_bolt import Ack, Say, BoltContext
from slack_sdk import WebClient

from listeners.n8n_assistant import get_n8n_assistant
from listeners.n8n_ui import (
    create_import_modal,
    create_workflow_builder_modal,
    create_workflow_blocks
)
from tools.n8n_tools import (
    ListWorkflowsTool,
    GetWorkflowTool,
    ExecuteWorkflowTool,
    ExportWorkflowTool,
    ImportWorkflowTool
)

logger = logging.getLogger(__name__)


def register_n8n_actions(app):
    """Register all N8N action handlers"""
    
    @app.action("list_workflows")
    def handle_list_workflows(ack: Ack, say: Say, client: WebClient):
        """Handle list workflows button"""
        ack()
        
        try:
            # List workflows
            tool = ListWorkflowsTool()
            result = tool.run()
            
            if result["success"]:
                assistant = get_n8n_assistant()
                response = assistant.agent.run(
                    f"Format this workflow list nicely: {json.dumps(result)}",
                    session_id="system"
                )
                
                from listeners.n8n_formatter import format_workflow_response
                formatted = format_workflow_response(response)
                say(blocks=formatted["blocks"])
            else:
                say(f"❌ Error: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            say(f"❌ Error listing workflows: {str(e)}")
    
    @app.action("create_workflow")
    def handle_create_workflow(ack: Ack, client: WebClient, body: Dict[str, Any]):
        """Handle create workflow button"""
        ack()
        
        try:
            # Open workflow builder modal
            client.views_open(
                trigger_id=body["trigger_id"],
                view=create_workflow_builder_modal()
            )
        except Exception as e:
            logger.error(f"Error opening create workflow modal: {e}")
    
    @app.action("import_workflow")
    def handle_import_workflow(ack: Ack, client: WebClient, body: Dict[str, Any]):
        """Handle import workflow button"""
        ack()
        
        try:
            # Open import modal
            client.views_open(
                trigger_id=body["trigger_id"],
                view=create_import_modal()
            )
        except Exception as e:
            logger.error(f"Error opening import modal: {e}")
    
    @app.action("show_templates")
    def handle_show_templates(ack: Ack, say: Say):
        """Handle show templates button"""
        ack()
        
        # Show available templates
        say(blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 Workflow Templates"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Choose a template to get started:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📧 Slack to Email*\nForward important Slack messages to email"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Use Template"
                    },
                    "action_id": "use_template_slack_email"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*📊 Daily Report*\nGenerate and send daily reports from multiple sources"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Use Template"
                    },
                    "action_id": "use_template_daily_report"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔄 Data Sync*\nSync data between Google Sheets and database"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Use Template"
                    },
                    "action_id": "use_template_data_sync"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🤖 AI Processing*\nProcess data with AI and store results"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Use Template"
                    },
                    "action_id": "use_template_ai_processing"
                }
            }
        ])
    
    # Workflow-specific actions
    @app.action(re.compile("view_workflow_(.+)"))
    def handle_view_workflow(ack: Ack, say: Say, action: Dict[str, Any]):
        """Handle view workflow button"""
        ack()
        
        workflow_id = action["action_id"].replace("view_workflow_", "")
        
        try:
            # Get workflow details
            tool = GetWorkflowTool()
            result = tool.run(workflow_id)
            
            if result["success"]:
                say(blocks=create_workflow_blocks(result["workflow"]))
            else:
                say(f"❌ Error: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error viewing workflow: {e}")
            say(f"❌ Error viewing workflow: {str(e)}")
    
    @app.action(re.compile("execute_workflow_(.+)"))
    def handle_execute_workflow(ack: Ack, say: Say, action: Dict[str, Any]):
        """Handle execute workflow button"""
        ack()
        
        workflow_id = action["action_id"].replace("execute_workflow_", "")
        
        try:
            say("🔄 Executing workflow...")
            
            # Execute workflow
            tool = ExecuteWorkflowTool()
            result = tool.run(workflow_id)
            
            if result["success"]:
                from listeners.n8n_formatter import format_workflow_response
                formatted = format_workflow_response(result)
                say(blocks=formatted["blocks"])
            else:
                say(f"❌ Error: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            say(f"❌ Error executing workflow: {str(e)}")
    
    @app.action(re.compile("export_workflow_(.+)"))
    def handle_export_workflow(
        ack: Ack,
        say: Say,
        client: WebClient,
        action: Dict[str, Any],
        context: BoltContext
    ):
        """Handle export workflow button"""
        ack()
        
        workflow_id = action["action_id"].replace("export_workflow_", "")
        
        try:
            say("📤 Exporting workflow...")
            
            # Export workflow
            tool = ExportWorkflowTool()
            result = tool.run(workflow_id)
            
            if result["success"]:
                # Create canvas with export
                assistant = get_n8n_assistant()
                canvas_response = assistant.canvas_manager.create_workflow_canvas(
                    workflow=result["workflow_data"],
                    channel_id=context.channel_id,
                    thread_ts=context.get("thread_ts")
                )
                
                say(blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ Workflow exported to canvas!"
                        }
                    }
                ])
            else:
                say(f"❌ Error: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error exporting workflow: {e}")
            say(f"❌ Error exporting workflow: {str(e)}")
    
    # Modal submissions
    @app.view("import_workflow_modal")
    def handle_import_workflow_submission(ack: Ack, body: Dict[str, Any], say: Say):
        """Handle import workflow modal submission"""
        ack()
        
        try:
            values = body["view"]["state"]["values"]
            workflow_json = values["workflow_json"]["workflow_json_input"]["value"]
            workflow_name = values.get("workflow_name", {}).get("workflow_name_input", {}).get("value")
            
            # Import workflow
            tool = ImportWorkflowTool()
            result = tool.run(workflow_json)
            
            if result["success"]:
                say(f"✅ Workflow imported successfully!")
                say(blocks=create_workflow_blocks(result["workflow"]))
            else:
                say(f"❌ Error: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error importing workflow: {e}")
            say(f"❌ Error importing workflow: {str(e)}")
    
    @app.view("build_workflow_modal")
    def handle_build_workflow_submission(
        ack: Ack,
        body: Dict[str, Any],
        say: Say,
        client: WebClient,
        context: BoltContext
    ):
        """Handle build workflow modal submission"""
        ack()
        
        try:
            values = body["view"]["state"]["values"]
            description = values["workflow_description"]["description_input"]["value"]
            name = values["workflow_name"]["name_input"]["value"]
            
            say(f"🔨 Building workflow: {name}...")
            
            # Build workflow with assistant
            assistant = get_n8n_assistant()
            response = assistant.agent.run(
                f"Build an N8N workflow named '{name}' that does: {description}",
                session_id=context.user_id
            )
            
            from listeners.n8n_formatter import format_workflow_response
            formatted = format_workflow_response(response)
            say(blocks=formatted["blocks"])
            
        except Exception as e:
            logger.error(f"Error building workflow: {e}")
            say(f"❌ Error building workflow: {str(e)}")


# Import regex at the top of the file
import re