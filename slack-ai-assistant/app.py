import os
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Check environment variables
logger = logging.getLogger(__name__)
logger.info("Checking environment variables...")
logger.info(f"SLACK_BOT_TOKEN: {'✓' if os.environ.get('SLACK_BOT_TOKEN') else '✗'}")
logger.info(f"SLACK_APP_TOKEN: {'✓' if os.environ.get('SLACK_APP_TOKEN') else '✗'}")
logger.info(f"OPENAI_API_KEY: {'✓' if os.environ.get('OPENAI_API_KEY') else '✗'}")
logger.info(f"COMPOSIO_TOKEN: {'✓' if os.environ.get('COMPOSIO_TOKEN') else '✗'}")

# Initialization
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Register Listeners
register_listeners(app)

# Start Bolt app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
