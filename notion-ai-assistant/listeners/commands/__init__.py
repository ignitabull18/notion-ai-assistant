from slack_bolt import App
from .notion_bookmarks_commands import (
    handle_notion_bookmarks_command,
    handle_notion_bookmark_action,
    handle_add_notion_bookmark_modal_submission
)


def register(app: App):
    # Register Notion bookmarks command
    app.command("/notion-bookmarks")(handle_notion_bookmarks_command)
    
    # Register bookmark actions
    import re
    app.action(re.compile(r"add_notion_templates_.*"))(handle_notion_bookmark_action)
    app.action(re.compile(r"sync_notion_workspace_.*"))(handle_notion_bookmark_action)
    app.action(re.compile(r"add_notion_bookmark_.*"))(handle_notion_bookmark_action)
    
    # Register modal handler
    app.view("add_notion_bookmark_modal")(handle_add_notion_bookmark_modal_submission)