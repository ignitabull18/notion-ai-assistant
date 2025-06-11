from slack_bolt import App
from .sample_shortcut import sample_shortcut_callback
from .jungle_scout_shortcuts import (
    handle_quick_product_lookup_shortcut,
    handle_analyze_from_clipboard_shortcut,
    handle_market_snapshot_shortcut,
    handle_analyze_product_from_message_shortcut,
    handle_create_research_report_shortcut,
    handle_quick_product_lookup_modal_submission,
    handle_analyze_clipboard_modal_submission,
    handle_market_snapshot_modal_submission,
    handle_analyze_message_product_modal_submission
)


def register(app: App):
    # Sample shortcut
    app.shortcut("sample_shortcut_id")(sample_shortcut_callback)
    
    # Global shortcuts (accessible from anywhere in Slack)
    app.shortcut("quick_product_lookup")(handle_quick_product_lookup_shortcut)
    app.shortcut("analyze_from_clipboard")(handle_analyze_from_clipboard_shortcut)
    app.shortcut("market_snapshot")(handle_market_snapshot_shortcut)
    
    # Message shortcuts (accessible from message context menu)
    app.shortcut("analyze_product_from_message")(handle_analyze_product_from_message_shortcut)
    app.shortcut("create_research_report")(handle_create_research_report_shortcut)
    
    # Modal submission handlers
    app.view("quick_product_lookup_modal")(handle_quick_product_lookup_modal_submission)
    app.view("analyze_clipboard_modal")(handle_analyze_clipboard_modal_submission)
    app.view("market_snapshot_modal")(handle_market_snapshot_modal_submission)
    app.view("analyze_message_product_modal")(handle_analyze_message_product_modal_submission)
