from slack_bolt import App
from .sample_action import sample_action_callback
from .jungle_scout_actions import (
    handle_quick_product_research,
    handle_create_sales_dashboard,
    handle_analyze_trends,
    handle_deep_analyze,
    handle_track_product,
    handle_create_research_canvas,
    handle_product_research_modal_submission,
    handle_trend_analysis_modal_submission,
    handle_product_tracking_modal_submission,
    handle_try_product_research,
    handle_try_sales_analytics,
    handle_try_keyword_analysis,
    handle_try_competitor_analysis,
    handle_create_research_canvas_from_response,
    handle_track_products_from_response,
    handle_research_from_analysis,
    handle_create_strategy_canvas,
    handle_track_mentioned_products,
    handle_export_research_report,
    handle_set_product_alerts,
    handle_track_keyword,
    handle_create_seo_canvas,
    handle_find_products_for_keyword,
    handle_create_sales_canvas,
    handle_set_sales_alerts,
    handle_forecast_sales,
    handle_monitor_competitor,
    handle_price_history,
    handle_create_product_watchlist,
    handle_show_workflows,
    handle_use_workflow_template,
    handle_quick_analyze_from_unfurl,
    handle_analyze_keywords_from_unfurl,
    handle_sales_estimate_from_unfurl,
    handle_find_competitors_from_unfurl,
    handle_create_report_from_unfurl
)


def register(app: App):
    # Sample action
    app.action("sample_action_id")(sample_action_callback)
    
    # Jungle Scout AI Assistant actions
    app.action("quick_product_research")(handle_quick_product_research)
    app.action("create_sales_dashboard")(handle_create_sales_dashboard)
    app.action("analyze_trends")(handle_analyze_trends)
    app.action("create_research_canvas")(handle_create_research_canvas)
    app.action("track_product")(handle_track_product)
    
    # Welcome actions
    app.action("try_product_research")(handle_try_product_research)
    app.action("try_sales_analytics")(handle_try_sales_analytics)
    app.action("try_keyword_analysis")(handle_try_keyword_analysis)
    app.action("try_competitor_analysis")(handle_try_competitor_analysis)
    
    # Canvas and report actions
    app.action("create_research_canvas_from_response")(handle_create_research_canvas_from_response)
    app.action("track_products_from_response")(handle_track_products_from_response)
    app.action("research_from_analysis")(handle_research_from_analysis)
    app.action("create_strategy_canvas")(handle_create_strategy_canvas)
    app.action("track_mentioned_products")(handle_track_mentioned_products)
    app.action("export_research_report")(handle_export_research_report)
    app.action("set_product_alerts")(handle_set_product_alerts)
    app.action("create_product_watchlist")(handle_create_product_watchlist)
    
    # Keyword actions
    app.action("track_keyword")(handle_track_keyword)
    app.action("create_seo_canvas")(handle_create_seo_canvas)
    app.action("find_products_for_keyword")(handle_find_products_for_keyword)
    
    # Sales actions
    app.action("create_sales_canvas")(handle_create_sales_canvas)
    app.action("set_sales_alerts")(handle_set_sales_alerts)
    app.action("forecast_sales")(handle_forecast_sales)
    
    # Competitor actions
    app.action("monitor_competitor")(handle_monitor_competitor)
    app.action("price_history")(handle_price_history)
    
    # Dynamic actions (using regex for product-specific actions)
    import re
    app.action(re.compile("deep_analyze_.*"))(handle_deep_analyze)
    app.action(re.compile("track_product_.*"))(handle_track_product)
    app.action(re.compile("competitor_analysis_.*"))(handle_deep_analyze)
    app.action(re.compile("analyze_product_.*"))(handle_deep_analyze)
    
    # Modal submissions
    app.view("product_research_modal")(handle_product_research_modal_submission)
    app.view("trend_analysis_modal")(handle_trend_analysis_modal_submission)
    app.view("product_tracking_modal")(handle_product_tracking_modal_submission)
    
    # Workflow actions
    app.action("show_workflows")(handle_show_workflows)
    app.action(re.compile("use_workflow_.*"))(handle_use_workflow_template)
    app.action("create_custom_workflow")(handle_use_workflow_template)
    
    # Link unfurling actions for Amazon products
    app.action(re.compile(r"quick_analyze_.*"))(handle_quick_analyze_from_unfurl)
    app.action(re.compile(r"analyze_keywords_.*"))(handle_analyze_keywords_from_unfurl)
    app.action(re.compile(r"sales_estimate_.*"))(handle_sales_estimate_from_unfurl)
    app.action(re.compile(r"find_competitors_.*"))(handle_find_competitors_from_unfurl)
    app.action(re.compile(r"create_report_.*"))(handle_create_report_from_unfurl)
