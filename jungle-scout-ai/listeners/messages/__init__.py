import re

from slack_bolt import App
from .sample_message import sample_message_callback
from .jungle_scout_handler import handle_jungle_scout_message


# To receive messages from a channel or dm your app must be a member!
def register(app: App):
    # Register sample message handler for greetings
    app.message(re.compile("(hi|hello|hey)"))(sample_message_callback)
    
    # Register Jungle Scout AI Assistant handler for all other messages
    app.message("")(handle_jungle_scout_message)
