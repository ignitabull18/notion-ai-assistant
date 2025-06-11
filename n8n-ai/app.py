"""
N8N AI Assistant - Workflow Automation Assistant for Slack
Build, deploy, and manage n8n workflows through natural language
"""
import os
import logging
from pathlib import Path
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from listeners import register_listeners

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create data directories
Path("./data").mkdir(exist_ok=True)
Path("./logs").mkdir(exist_ok=True)

# Initialize the app with OAuth settings
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    # Enable to use the Events API instead of Socket Mode
    # Make sure to use the OAuth redirect flow for multi-workspace apps!
    # process_before_response=True,
)

# Get assistant ID from environment or use default
assistant_id = os.environ.get("SLACK_ASSISTANT_ID", "default_assistant")

# Register assistant middleware
assistant = app.assistant(assistant_id=assistant_id)

# Register all listeners
register_listeners(app, assistant)

def main():
    """Start the N8N AI Assistant"""
    try:
        # Start the app
        app_token = os.environ.get("SLACK_APP_TOKEN")
        if not app_token:
            raise ValueError("SLACK_APP_TOKEN environment variable is required for Socket Mode")
        
        logger.info("Starting N8N AI Assistant in Socket Mode...")
        handler = SocketModeHandler(app, app_token)
        
        print("""
╔═══════════════════════════════════════════════════════════════╗
║                    N8N AI Assistant                           ║
║               Workflow Automation for Slack                   ║
╠═══════════════════════════════════════════════════════════════╣
║  • Build workflows from natural language                      ║
║  • Import/export workflow JSON                                ║
║  • Replicate workflows from screenshots                       ║
║  • Monitor and manage running workflows                       ║
║  • Access 400+ integrations                                   ║
╚═══════════════════════════════════════════════════════════════╝
        """)
        
        handler.start()
        
    except Exception as e:
        logger.error(f"Failed to start N8N AI Assistant: {e}")
        raise

if __name__ == "__main__":
    main()