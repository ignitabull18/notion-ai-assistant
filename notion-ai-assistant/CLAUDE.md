# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready Slack bot that integrates with Notion using the Agno framework and Composio tools. It uses Slack's 2024 Assistant API for native assistant experiences with rich Block Kit UI components, suggested prompts, and status indicators.

## Common Commands

**Development & Testing:**
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python tests/test_all_notion_actions.py          # Test all Notion actions
python tests/test_composio.py                    # Test Composio connection
python tests/integration/test_simple_notion.py   # Test without Slack

# Code quality checks
python scripts/checks/check_style.py             # Check code style/naming
python scripts/checks/check_actions.py           # Check available actions
python scripts/checks/check_composio_api.py      # Test Composio API
```

**Running the Application:**
```bash
# Start the bot (requires .env file)
python main.py

# Development utilities
python scripts/development/get_action_schemas.py  # Get Composio action schemas
python scripts/development/inspect_tools.py      # Inspect available tools
```

## Architecture Overview

**Core Components:**
- `main.py`: Production entry point with health monitoring, error handling, and graceful shutdown
- `config.py`: Comprehensive configuration management with validation
- `listeners/assistant.py`: Slack Assistant API integration with thread management
- `listeners/agno_integration.py`: Agno agent with long-term memory for context retention
- `listeners/ui_components.py` & `ui_components_advanced.py`: Rich Block Kit UI components

**Integration Layer:**
- Uses Composio for Notion API access (20 available actions)
- Agno framework for AI agent capabilities with memory
- OpenAI o3 model for LLM responses (65k token context)
- SQLite database for persistent memory storage

**Key Patterns:**
1. **Assistant API Pattern**: Uses `@assistant.thread_started` and `@assistant.user_message` decorators
2. **Memory Integration**: Agno agent remembers user preferences and past interactions
3. **Error Handling**: Comprehensive error handling with monitoring and metrics
4. **UI Components**: Rich Block Kit formatting for tables, buttons, and interactive elements

## Configuration Requirements

**Required Environment Variables:**
```bash
SLACK_BOT_TOKEN=xoxb-...        # Slack bot token
SLACK_APP_TOKEN=xapp-...        # Slack app token (Socket Mode)
SLACK_SIGNING_SECRET=...        # Slack signing secret
OPENAI_API_KEY=sk-...          # OpenAI API key
COMPOSIO_TOKEN=...             # Composio API token
```

**Optional Variables:**
```bash
ENVIRONMENT=production          # Environment (development/production)
LOG_LEVEL=INFO                 # Logging level
DATABASE_URL=sqlite:///...     # Database URL (defaults to local SQLite)
```

## Data Flow

1. **Slack Event** → `assistant.py` (Assistant API handlers)
2. **Intent Detection** → `agno_integration.py` (Agno agent processes with memory)
3. **Notion Actions** → Composio tools execute API calls
4. **Response Formatting** → `slack_formatter.py` & UI components
5. **Memory Storage** → Agno framework stores context in SQLite

## Critical Implementation Details

**Memory Management:**
- Agno agent maintains conversation context and user preferences
- SQLite database stores memories at `./data/notion_memories.db`
- Memory retrieval influences response personalization

**Error Handling:**
- All API calls wrapped with retry logic and error boundaries
- Health checks for OpenAI, Composio, and database connections
- Structured logging with metrics collection

**UI Architecture:**
- Block Kit components in `ui_components.py` for standard layouts
- Advanced components in `ui_components_advanced.py` for complex interactions
- Notion-specific formatters handle tables, pages, and database views

**Production Features:**
- Health monitoring with configurable checks
- Graceful shutdown with signal handlers
- Comprehensive configuration validation
- Metrics collection and structured logging

## Testing Strategy

Tests are organized by integration level:
- `tests/unit/`: Component-level tests
- `tests/integration/`: Full workflow tests
- `tests/test_all_notion_actions.py`: Comprehensive Notion API validation

Run tests frequently during development to ensure Notion integration stability.