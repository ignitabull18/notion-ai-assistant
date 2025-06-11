from slack_bolt import App
from .sample_command import sample_command_callback
from .jungle_scout_commands import (
    research_command,
    keywords_command,
    competitor_command,
    sales_command,
    trends_command,
    validate_command,
    dashboard_command
)
from .jungle_scout_bookmarks_commands import (
    handle_product_bookmarks_command,
    handle_product_bookmark_action,
    handle_add_product_bookmark_modal_submission
)


def register(app: App):
    app.command("/sample-command")(sample_command_callback)
    
    # Register Jungle Scout AI Assistant commands
    app.command("/research")(research_command)
    app.command("/keywords")(keywords_command)
    app.command("/competitor")(competitor_command)
    app.command("/sales")(sales_command)
    app.command("/trends")(trends_command)
    app.command("/validate")(validate_command)
    app.command("/dashboard")(dashboard_command)
    app.command("/product-bookmarks")(handle_product_bookmarks_command)
    
    # Register bookmark actions
    import re
    app.action(re.compile(r"add_market_resources_.*"))(handle_product_bookmark_action)
    app.action(re.compile(r"add_product_bookmark_.*"))(handle_product_bookmark_action)
    app.action(re.compile(r"analyze_bookmark_.*"))(handle_product_bookmark_action)
    app.action(re.compile(r"view_all_bookmarks_.*"))(handle_product_bookmark_action)
    app.action(re.compile(r"export_bookmarks_.*"))(handle_product_bookmark_action)
    
    # Register modal handler
    app.view("add_product_bookmark_modal")(handle_add_product_bookmark_modal_submission)
