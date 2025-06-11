"""
Slash commands for Jungle Scout AI Assistant
"""
from slack_bolt import Ack, Say
from slack_sdk.web import WebClient
from typing import Dict, Any

from listeners.jungle_scout_assistant import jungle_scout_assistant


def research_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /research command"""
    ack()
    command = f"research {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )


def keywords_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /keywords command"""
    ack()
    command = f"keywords {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )


def competitor_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /competitor command"""
    ack()
    command = f"competitor {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )


def sales_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /sales command"""
    ack()
    command = f"sales {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )


def trends_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /trends command"""
    ack()
    command = f"trends {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )


def validate_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /validate command"""
    ack()
    command = f"validate {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )


def dashboard_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /dashboard command"""
    ack()
    command = f"dashboard {body.get('text', '')}"
    jungle_scout_assistant.process_jungle_scout_command(
        body={"text": command, "channel": body.get("channel", {}), "user": body.get("user", {})},
        context=body.get("context", {}),
        say=say,
        client=client
    )