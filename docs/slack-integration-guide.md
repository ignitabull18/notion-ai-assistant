# Slack Integration Architecture Guide

This document explains the two-layer Slack integration strategy in the Agno project.

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Slack Workspace                 │
│  ┌────────────┐    ┌─────────────┐    │
│  │  Events    │    │ Slash Cmds  │    │
│  └─────┬──────┘    └──────┬──────┘    │
└────────┼──────────────────┼───────────┘
         │                  │
         ▼                  ▼
┌─────────────────────────────────────────┐
│      Slack CLI / Bolt App               │
│   (notion-ai-assistant/)                │
│  ┌─────────────────────────────────┐   │
│  │  AI Agents API Integration      │   │
│  │  Interactive Blocks & Modals    │   │
│  │  Advanced Event Handling        │   │
│  └─────────────────────────────────┘   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│      FastAPI Gateway (src/app/)         │
│  ┌─────────────────────────────────┐   │
│  │  SlackClientWrapper             │   │
│  │  - Signature Verification       │   │
│  │  - Rate Limit Handling         │   │
│  │  - Retry Logic                 │   │
│  └─────────────────────────────────┘   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         Agno Agent (src/agent/)         │
│  ┌─────────────────────────────────┐   │
│  │  ComposioTools (Simple Slack)   │   │
│  │  ReasoningTools                 │   │
│  │  KnowledgeTools (Qdrant)        │   │
│  │  Crawl4aiTools                  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Two-Layer Strategy

### Layer 1: Slack CLI / Bolt App (`notion-ai-assistant/`)
**Use for:**
- Slack AI Agents API (beta)
- Interactive components (blocks, modals, canvases, lists)
- Per-agent or per-team dedicated Slack Apps
- Advanced event subscriptions
- Socket Mode for development

**Key Files:**
- `app.py` - Main Bolt application
- `listeners/assistant.py` - AI Agent handlers
- `manifest.json` - Slack app manifest

### Layer 2: FastAPI + SlackClientWrapper (`src/`)
**Use for:**
- HTTP-based event handling (production)
- Integration with Agno Agent
- Signature verification
- Rate limit handling with exponential backoff
- Slash command routing

**Key Files:**
- `src/app/server.py` - FastAPI endpoints
- `src/slack_client.py` - Slack SDK wrapper with retry logic

## When to Use What

### Use Slack SDK / Bolt when you need:
- AI Agents API functionality
- Interactive UI elements (modals, blocks)
- Custom slash commands with complex flows
- Per-workspace app customization
- Real-time Socket Mode during development

### Use ComposioTools when you need:
- Simple message sending
- Basic channel operations
- Integration with other SaaS tools (Notion, GitHub)
- Unified API access across multiple services

## Development Workflow

1. **Local Development with Socket Mode:**
   ```bash
   cd notion-ai-assistant/
   slack run  # Starts Socket Mode connection
   ```

2. **Production with HTTP Mode:**
   ```bash
   cd /path/to/agno
   uvicorn src.app.server:app --host 0.0.0.0 --port 8000
   ```

3. **Testing the Integration:**
   ```bash
   # Test Slack client wrapper
   python -m pytest tests/test_slack_client.py -v
   
   # Test integration
   python test_slack_integration.py
   ```

## Environment Variables

Both layers require:
- `SLACK_BOT_TOKEN` - Bot user OAuth token
- `SLACK_SIGNING_SECRET` - Request signature verification

Bolt app additionally needs:
- `SLACK_APP_TOKEN` - For Socket Mode (development)

## Migration Path

Current state:
- FastAPI handles HTTP events with SlackClientWrapper
- Bolt app exists but runs separately

Future state:
- Bolt app becomes primary event handler
- FastAPI remains as thin API layer for Agno Agent
- ComposioTools continues handling simple operations

## Error Handling

The SlackClientWrapper implements:
- Exponential backoff for transient errors
- Respect for Slack's Retry-After headers
- No retry for client errors (4xx) except rate limits
- Maximum retry limit to prevent infinite loops

## Security

- All requests verified using `SignatureVerifier`
- 3-second ACK requirement for webhooks
- Environment-based credential management
- No hardcoded tokens or secrets