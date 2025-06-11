from slack_bolt import App
from .notion_shortcuts import (
    handle_quick_note_shortcut,
    handle_search_notion_shortcut,
    handle_create_page_from_message_shortcut,
    handle_save_to_notion_shortcut,
    handle_notion_workspace_overview_shortcut,
    handle_quick_note_modal_submission,
    handle_search_notion_modal_submission,
    handle_create_page_from_message_modal_submission,
    handle_save_to_notion_modal_submission
)


def register(app: App):
    # Global shortcuts (accessible from anywhere in Slack)
    app.shortcut("quick_note")(handle_quick_note_shortcut)
    app.shortcut("search_notion")(handle_search_notion_shortcut)
    app.shortcut("notion_workspace_overview")(handle_notion_workspace_overview_shortcut)
    
    # Message shortcuts (accessible from message context menu)
    app.shortcut("create_page_from_message")(handle_create_page_from_message_shortcut)
    app.shortcut("save_to_notion")(handle_save_to_notion_shortcut)
    
    # Modal submission handlers
    app.view("quick_note_modal")(handle_quick_note_modal_submission)
    app.view("search_notion_modal")(handle_search_notion_modal_submission)
    app.view("create_page_from_message_modal")(handle_create_page_from_message_modal_submission)
    app.view("save_to_notion_modal")(handle_save_to_notion_modal_submission)