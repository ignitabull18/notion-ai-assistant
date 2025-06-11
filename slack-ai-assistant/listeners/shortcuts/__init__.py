from slack_bolt import App
from .sample_shortcut import sample_shortcut_callback
from .slack_assistant_shortcuts import (
    handle_quick_reminder_shortcut,
    handle_search_workspace_shortcut,
    handle_create_summary_shortcut,
    handle_analyze_message_shortcut,
    handle_quick_task_shortcut,
    handle_quick_reminder_modal_submission,
    handle_workspace_search_modal_submission,
    handle_analyze_message_modal_submission,
    handle_quick_task_modal_submission
)


def register(app: App):
    # Sample shortcut
    app.shortcut("sample_shortcut_id")(sample_shortcut_callback)
    
    # Global shortcuts (accessible from anywhere in Slack)
    app.shortcut("quick_reminder")(handle_quick_reminder_shortcut)
    app.shortcut("search_workspace")(handle_search_workspace_shortcut)
    app.shortcut("quick_task")(handle_quick_task_shortcut)
    
    # Message shortcuts (accessible from message context menu)
    app.shortcut("create_summary")(handle_create_summary_shortcut)
    app.shortcut("analyze_message")(handle_analyze_message_shortcut)
    
    # Modal submission handlers
    app.view("quick_reminder_modal")(handle_quick_reminder_modal_submission)
    app.view("workspace_search_modal")(handle_workspace_search_modal_submission)
    app.view("analyze_message_modal")(handle_analyze_message_modal_submission)
    app.view("quick_task_modal")(handle_quick_task_modal_submission)
