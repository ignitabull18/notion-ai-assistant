"""
N8N AI Assistant Listeners
Register all event handlers and middleware
"""
import logging
from slack_bolt import App

from .n8n_assistant import register_n8n_assistant
from .actions.n8n_actions import register_n8n_actions

logger = logging.getLogger(__name__)


def register_listeners(app: App, assistant):
    """Register all listeners for the N8N AI Assistant"""
    logger.info("Registering N8N AI Assistant listeners...")
    
    # Register assistant handlers
    register_n8n_assistant(app, assistant)
    
    # Register action handlers
    register_n8n_actions(app)
    
    # Register slash commands
    @app.command("/n8n")
    def handle_n8n_command(ack, command, say):
        """Handle /n8n command"""
        ack()
        
        text = command.get("text", "").strip()
        
        if not text or text == "help":
            say(blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*N8N Commands:*\n"
                               "• `/n8n` - Show this help\n"
                               "• `/n8n list` - List your workflows\n"
                               "• `/n8n create` - Create a new workflow\n"
                               "• `/n8n import` - Import a workflow\n"
                               "• `/n8n execute [id]` - Execute a workflow\n"
                               "• `/n8n help` - Show this help"
                    }
                }
            ])
        elif text == "list":
            # Trigger list workflows action
            from listeners.n8n_assistant import get_n8n_assistant
            assistant_instance = get_n8n_assistant()
            assistant_instance.handle_message(
                "list my workflows",
                say=say,
                client=app.client,
                context={"user_id": command["user_id"], "channel_id": command["channel_id"]}
            )
        elif text == "create":
            say("Use the assistant to describe what workflow you want to create!")
        elif text == "import":
            say("Send me the workflow JSON you want to import!")
        elif text.startswith("execute"):
            parts = text.split()
            if len(parts) > 1:
                workflow_id = parts[1]
                from listeners.n8n_assistant import get_n8n_assistant
                assistant_instance = get_n8n_assistant()
                assistant_instance.handle_message(
                    f"execute workflow {workflow_id}",
                    say=say,
                    client=app.client,
                    context={"user_id": command["user_id"], "channel_id": command["channel_id"]}
                )
            else:
                say("Please provide a workflow ID: `/n8n execute [workflow-id]`")
    
    # Register event handlers
    @app.event("app_home_opened")
    def handle_app_home_opened(event, client):
        """Handle app home opened event"""
        try:
            user_id = event["user"]
            
            # Publish app home view
            client.views_publish(
                user_id=user_id,
                view={
                    "type": "home",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "🔧 N8N Workflow Assistant"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Welcome to your N8N automation hub!"
                            }
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Quick Stats:*\n"
                                       "• Active Workflows: Loading...\n"
                                       "• Recent Executions: Loading...\n"
                                       "• Total Automations: Loading..."
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View Workflows"
                                    },
                                    "action_id": "list_workflows",
                                    "style": "primary"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Create Workflow"
                                    },
                                    "action_id": "create_workflow"
                                }
                            ]
                        }
                    ]
                }
            )
        except Exception as e:
            logger.error(f"Error handling app home opened: {e}")
    
    logger.info("N8N AI Assistant listeners registered successfully")