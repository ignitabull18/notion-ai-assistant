from slack_bolt import App
from .sample_command import sample_command_callback
from .slack_assistant_commands import (
    summarize_command,
    remind_command,
    search_command,
    schedule_command,
    analyze_command
)
from .bookmarks_commands import (
    handle_bookmarks_command,
    handle_bookmark_action,
    handle_add_bookmark_modal_submission
)
from .lists_commands import (
    handle_lists_command,
    handle_list_action,
    handle_add_list_item_modal_submission
)


def register(app: App):
    app.command("/sample-command")(sample_command_callback)
    
    # Register Slack AI Assistant commands with ai- prefix
    app.command("/ai-summarize")(summarize_command)
    app.command("/ai-remind")(remind_command)
    app.command("/ai-search")(search_command)
    app.command("/ai-schedule")(schedule_command)
    app.command("/ai-analyze")(analyze_command)
    app.command("/ai-bookmarks")(handle_bookmarks_command)
    app.command("/ai-lists")(handle_lists_command)
    
    # Register bookmark actions
    import re
    app.action(re.compile(r"add_default_bookmarks_.*"))(handle_bookmark_action)
    app.action(re.compile(r"add_bookmark_.*"))(handle_bookmark_action)
    app.action(re.compile(r"bookmark_menu_.*"))(handle_bookmark_action)
    app.action(re.compile(r"organize_bookmarks_.*"))(handle_bookmark_action)
    
    # Register list actions
    app.action(re.compile(r"complete_item_.*"))(handle_list_action)
    app.action(re.compile(r"add_list_item_.*"))(handle_list_action)
    app.action(re.compile(r"view_full_list_.*"))(handle_list_action)
    app.action(re.compile(r"list_settings_.*"))(handle_list_action)
    app.action(re.compile(r"use_.*_template"))(handle_list_action)
    
    # Register modal handlers
    app.view("add_bookmark_modal")(handle_add_bookmark_modal_submission)
    app.view("add_list_item_modal")(handle_add_list_item_modal_submission)
