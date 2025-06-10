# Notion AI Assistant for Slack

A powerful Slack bot that integrates with Notion using Agno framework and Composio tools.

## Features

- **Complete Notion Integration**: Access all 20 Notion actions through Slack
- **Long-term Memory**: Remembers user preferences and past interactions
- **AI-Powered**: Uses OpenAI's o4-mini model for intelligent responses
- **Slack Assistant Framework**: Native Slack assistant experience

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Slack workspace with admin access
- Notion account
- OpenAI API key

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file with:

```bash
# Slack credentials
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...

# Optional OAuth (for multi-workspace)
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...

# AI and integrations
OPENAI_API_KEY=sk-...
COMPOSIO_TOKEN=...
```

### 4. Connect Notion

1. Go to https://app.composio.dev
2. Connect your Notion account
3. Copy the API key to `COMPOSIO_TOKEN`

### 5. Run the Bot

```bash
python main.py
```

## Architecture

The project follows a clean, organized structure:

```
notion-ai-assistant/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── listeners/              # Core bot logic
│   ├── assistant.py        # Slack assistant handler
│   ├── agno_integration.py # Agno agent with memory
│   ├── slack_formatter.py  # Beautiful Slack UI formatting
│   └── events/             # Event handlers
├── data/                   # Local storage
│   └── notion_memories.db  # Agent memory database
├── docs/                   # Documentation
│   ├── ONBOARDING_GUIDE.md # User guide
│   ├── ASSISTANT_PROFILE.md # Features
│   └── CLAUDE.md           # Dev notes
├── scripts/                # Utility scripts
│   ├── checks/             # Validation tools
│   └── development/        # Dev helpers
└── tests/                  # Test suite
    ├── unit/               # Component tests
    └── integration/        # Workflow tests
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization.

## Available Commands

Ask the bot naturally about:
- Creating, reading, updating, deleting Notion pages
- Managing databases and adding items
- Searching across your workspace
- Managing comments and users
- Working with blocks and properties

Examples:
- "Create a page called Project Notes"
- "Search for Q4 planning documents"
- "List all my databases"
- "Add content to the weekly report page"

## Memory Features

The bot remembers:
- Your frequently accessed pages and databases
- Preferred formatting and organization patterns
- Past interactions and context
- User-specific preferences

## Troubleshooting

- **"Notion is not connected"**: Connect Notion at https://app.composio.dev
- **"Unhandled event"**: Make sure you're using Socket Mode
- **Memory not working**: Check that `./data` directory exists and is writable

## Development

Run all tests:
```bash
python run_tests.py
```

Check code style and naming conventions:
```bash
python scripts/checks/check_style.py
```

Or run individual tests:
```bash
python tests/test_all_notion_actions.py          # Test all Notion actions
python tests/test_composio.py                    # Test Composio connection
python tests/integration/test_simple_notion.py   # Test without Slack
python scripts/checks/check_actions.py           # Check available actions
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards and naming conventions.