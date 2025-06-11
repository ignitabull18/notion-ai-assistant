"""
Slash commands for Slack AI Assistant
"""
from slack_bolt import Ack, Say
from slack_sdk.web import WebClient
from typing import Dict, Any

from listeners.slack_assistant import SlackAssistant


slack_assistant = SlackAssistant()


def summarize_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /summarize command"""
    ack()
    command = f"summarize {body.get('text', '')}"
    slack_assistant.process_slack_command(
        body=body,
        context=body.get("context", {}),
        say=say,
        client=client
    )


def remind_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /remind command"""
    ack()
    command = f"remind {body.get('text', '')}"
    slack_assistant.process_slack_command(
        body=body,
        context=body.get("context", {}),
        say=say,
        client=client
    )


def search_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /search command"""
    ack()
    command = f"search {body.get('text', '')}"
    slack_assistant.process_slack_command(
        body=body,
        context=body.get("context", {}),
        say=say,
        client=client
    )


def schedule_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /schedule command"""
    ack()
    command = f"schedule {body.get('text', '')}"
    slack_assistant.process_slack_command(
        body=body,
        context=body.get("context", {}),
        say=say,
        client=client
    )


def analyze_command(ack: Ack, body: Dict[str, Any], say: Say, client: WebClient, logger):
    """Handle /analyze command"""
    ack()
    command = f"analyze {body.get('text', '')}"
    slack_assistant.process_slack_command(
        body=body,
        context=body.get("context", {}),
        say=say,
        client=client
    )