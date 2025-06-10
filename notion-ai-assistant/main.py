#!/usr/bin/env python3
"""
Production-ready Notion AI Assistant for Slack
"""
import asyncio
import signal
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, init_config
from utils.logging import setup_logging
from utils.errors import error_handler, ConfigurationError
from utils.monitoring import health_monitor, metrics, create_database_health_check, create_api_health_check
from listeners import create_production_app


async def setup_health_checks():
    """Setup health monitoring"""
    config = get_config()
    
    # Database health check
    def test_database():
        import sqlite3
        db_path = config.database.url.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
    
    health_monitor.register_check("database", create_database_health_check(test_database))
    
    # OpenAI API health check
    def test_openai():
        import openai
        client = openai.OpenAI(api_key=config.openai.api_key)
        client.models.list()
    
    health_monitor.register_check("openai", create_api_health_check("OpenAI", test_openai))
    
    # Composio API health check
    def test_composio():
        from composio_agno import ComposioToolSet
        composio = ComposioToolSet(api_key=config.composio.api_key)
        composio.get_tools(apps=["NOTION"], limit=1)
    
    health_monitor.register_check("composio", create_api_health_check("Composio", test_composio))
    
    # Start monitoring
    await health_monitor.start_monitoring()


async def validate_integrations():
    """Validate all integrations are working"""
    logger = error_handler.logger
    config = get_config()
    
    # Test Composio connection
    try:
        from composio_agno import ComposioToolSet
        composio_client = ComposioToolSet(api_key=config.composio.api_key)
        accounts = composio_client.get_connected_accounts()
        
        notion_connected = any(
            (hasattr(acc, 'appName') and acc.appName == "notion") or
            (isinstance(acc, dict) and acc.get("appName") == "notion")
            for acc in accounts
        )
        
        if not notion_connected:
            logger.warning("⚠️ Notion is not connected in Composio!")
            logger.warning("    Connect it at: https://app.composio.dev")
        else:
            logger.info("✅ Notion is connected via Composio")
            
    except Exception as e:
        logger.error(f"❌ Composio connection failed: {e}")
        raise ConfigurationError(f"Composio integration failed: {e}")
    
    # Test Agno import
    try:
        import agno
        logger.info("✅ Agno framework is available")
    except ImportError:
        logger.error("❌ Agno framework not installed")
        raise ConfigurationError("Agno framework not installed. Run: pip install agno")


async def shutdown_handler():
    """Graceful shutdown handler"""
    logger = error_handler.logger
    logger.info("Initiating graceful shutdown...")
    
    # Stop health monitoring
    await health_monitor.stop_monitoring()
    
    # Log final metrics
    metrics_summary = metrics.get_metrics_summary()
    logger.info("Final metrics summary", extra={"metrics": metrics_summary})
    
    logger.info("Shutdown complete")


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger = error_handler.logger
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(shutdown_handler())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Production main entry point"""
    try:
        # Initialize configuration
        config = init_config()
        
        # Setup logging first
        setup_logging(
            config.logging,
            app_name=config.app_name,
            version=config.version,
            environment=config.environment
        )
        
        logger = error_handler.logger
        logger.info(
            "Starting Notion AI Assistant",
            extra={
                "version": config.version,
                "environment": config.environment,
                "debug": config.debug
            }
        )
        
        # Validate integrations
        await validate_integrations()
        
        # Setup health monitoring
        await setup_health_checks()
        
        # Create production Slack app
        app = create_production_app(config)
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Log startup metrics
        metrics.increment("app.startup")
        metrics.gauge("app.version", 1.0, {"version": config.version})
        
        logger.info("⚡️ Notion AI Assistant is running in production mode!")
        
        # Start the app
        if config.slack.app_token:
            from slack_bolt.adapter.socket_mode import SocketModeHandler
            handler = SocketModeHandler(app, config.slack.app_token)
            # Keep the main thread alive
            await asyncio.Event().wait()
        else:
            import threading
            def start_app():
                app.start(port=3000)
            
            app_thread = threading.Thread(target=start_app, daemon=True)
            app_thread.start()
            # Keep the main thread alive
            await asyncio.Event().wait()
        
    except ConfigurationError as e:
        print(f"Configuration error: {e.message}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger = error_handler.logger
        logger.info("👋 Received shutdown signal")
        await shutdown_handler()
    except Exception as e:
        error_handler.handle_error(e, context={"phase": "startup"})
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())