from .assistant import assistant
from .delegate_to_agent import register_listeners as register_agent_listeners


def register_listeners(app):
    # Using assistant middleware is the recommended way.
    app.assistant(assistant)
    
    # Register agent delegation handlers
    register_agent_listeners(app)

    # The following event listeners demonstrate how to implement the same on your own.
    # from listeners import events
    # events.register(app)


def create_production_app(config):
    """Create production-ready Slack app with all middleware"""
    from slack_bolt import App
    from utils.errors import error_handler
    from utils.security import SecurityMiddleware
    from utils.monitoring import metrics
    
    # Initialize Slack app
    app = App(
        token=config.slack.bot_token,
        signing_secret=config.slack.signing_secret
    )
    
    # Initialize security middleware
    security = SecurityMiddleware(
        signing_secret=config.slack.signing_secret,
        rate_limit_per_minute=config.security.rate_limit_per_minute,
        max_message_length=config.security.max_message_length,
        allowed_users=config.security.allowed_users,
        allowed_channels=config.security.allowed_channels
    )
    
    # Add production middleware
    @app.middleware
    def security_middleware(body, next):
        """Security validation middleware"""
        try:
            # Extract request info
            user_id = body.get("event", {}).get("user") or body.get("user_id")
            channel_id = body.get("event", {}).get("channel") or body.get("channel_id")
            text = body.get("event", {}).get("text", "")
            
            if user_id and channel_id:
                # Validate request
                security.validate_request(
                    user_id=user_id,
                    channel_id=channel_id,
                    message=text
                )
            
            # Continue to next middleware
            next()
            
        except Exception as e:
            app_error = error_handler.handle_error(e, context={"middleware": "security"})
            error_handler.logger.error(f"Security middleware error: {app_error.message}")
            # Don't continue processing if security check fails
            return
    
    @app.middleware
    def metrics_middleware(body, next):
        """Metrics collection middleware"""
        with metrics.timer("slack.request_duration"):
            metrics.increment("slack.requests")
            try:
                next()
                metrics.increment("slack.requests.success")
            except Exception as e:
                metrics.increment("slack.requests.error")
                raise
    
    @app.middleware
    def error_handling_middleware(body, next):
        """Global error handling middleware"""
        try:
            next()
        except Exception as e:
            user_id = body.get("event", {}).get("user") or body.get("user_id")
            channel_id = body.get("event", {}).get("channel") or body.get("channel_id")
            
            app_error = error_handler.handle_error(
                e, 
                context={"body": body},
                user_id=user_id,
                channel_id=channel_id
            )
            
            # Send user-friendly error message
            if channel_id:
                try:
                    app.client.chat_postMessage(
                        channel=channel_id,
                        text=f"❌ {app_error.user_message}"
                    )
                except Exception as send_error:
                    error_handler.logger.error(f"Failed to send error message: {send_error}")
    
    # Add health check endpoint
    @app.event("url_verification")
    def handle_url_verification(body, ack):
        """Handle Slack URL verification"""
        ack(body["challenge"])
    
    # Add custom health endpoint for Docker health checks
    from flask import Flask, jsonify
    from utils.monitoring import health_monitor
    
    # Create a simple Flask app for health checks
    health_app = Flask(__name__)
    
    @health_app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            overall_health = health_monitor.get_overall_health()
            status_code = 200 if overall_health.status.value == "healthy" else 503
            
            return jsonify({
                "status": overall_health.status.value,
                "message": overall_health.message,
                "timestamp": overall_health.last_checked.isoformat() if overall_health.last_checked else None,
                "checks": {
                    name: {
                        "status": check.status.value,
                        "message": check.message,
                        "response_time_ms": check.response_time_ms
                    }
                    for name, check in health_monitor.last_results.items()
                }
            }), status_code
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": None
            }), 503
    
    # Start health app in a separate thread
    import threading
    def start_health_server():
        health_app.run(host='0.0.0.0', port=3001, debug=False)
    
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Register all listeners
    register_listeners(app)
    
    return app
