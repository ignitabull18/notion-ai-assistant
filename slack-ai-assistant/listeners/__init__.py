from listeners import actions
from listeners import commands
from listeners import events
from listeners import messages
from listeners import shortcuts
from listeners import views
from .assistant import assistant


def register_listeners(app):
    # Use assistant middleware for handling assistant threads
    app.assistant(assistant)
    
    # Register other listeners
    actions.register(app)
    commands.register(app)
    events.register(app)
    messages.register(app)
    shortcuts.register(app)
    views.register(app)
    
    # Register link unfurling
    from .link_unfurling import register_link_unfurling
    register_link_unfurling(app, app.client)
