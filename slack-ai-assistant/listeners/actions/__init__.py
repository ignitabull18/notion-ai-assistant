from slack_bolt import App
from .sample_action import sample_action_callback
from .assistant_actions import (
    handle_quick_summarize,
    handle_create_canvas,
    handle_quick_reminder,
    handle_create_summary_canvas,
    handle_share_summary,
    handle_set_followup,
    handle_view_message,
    handle_reminder_modal_submission,
    handle_show_workflows,
    handle_use_workflow_template
)


def register(app: App):
    # Sample action
    app.action("sample_action_id")(sample_action_callback)
    
    # AI Assistant actions
    app.action("quick_summarize")(handle_quick_summarize)
    app.action("create_canvas")(handle_create_canvas)
    app.action("quick_reminder")(handle_quick_reminder)
    app.action("create_summary_canvas")(handle_create_summary_canvas)
    app.action("share_summary")(handle_share_summary)
    app.action("set_followup")(handle_set_followup)
    
    # Welcome actions
    app.action("try_summarize")(handle_quick_summarize)
    app.action("try_reminder")(handle_quick_reminder)
    app.action("try_search")(handle_quick_summarize)  # Reuse summarize for now
    app.action("try_analytics")(handle_quick_summarize)  # Reuse summarize for now
    
    # Canvas creation from summaries
    app.action("create_canvas_from_summary")(handle_create_summary_canvas)
    app.action("search_channel")(handle_quick_summarize)  # Reuse summarize for now
    
    # Analytics actions
    app.action("create_analytics_canvas")(handle_create_canvas)
    app.action("export_analytics")(handle_share_summary)  # Reuse share for now
    
    # Reminder actions
    app.action("view_reminders")(handle_quick_reminder)
    app.action("cancel_reminder")(handle_quick_reminder)
    
    # Dynamic actions (using regex)
    import re
    app.action(re.compile("view_message_.*"))(handle_view_message)
    app.action(re.compile("goto_message_.*"))(handle_view_message)
    
    # Modal submissions
    app.view("reminder_modal")(handle_reminder_modal_submission)
    
    # Workflow actions
    app.action("show_workflows")(handle_show_workflows)
    app.action(re.compile("use_workflow_.*"))(handle_use_workflow_template)
    app.action("create_custom_workflow")(handle_use_workflow_template)
