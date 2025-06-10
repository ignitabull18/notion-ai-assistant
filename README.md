# Notion AI Assistant for Slack

## Overview

A Slack bot that enables users to interact with their Notion workspace through natural language commands. Built using Slack Bolt for Python, it provides seamless integration between Slack conversations and Notion operations.

### Key Features

- **Natural Language Processing**: Understands commands like "create a page called Project Ideas" or "search for meeting notes"
- **Real-time Slack Integration**: Responds instantly to messages using Socket Mode
- **Notion Operations**: Create pages, search content, list databases
- **Interactive UI**: Slack blocks and buttons for better user experience
- **Direct Composio Integration**: Handles Notion API operations through Composio SDK

## Getting Started

### Prerequisites

- Python 3.9+
- Slack workspace with app installation permissions
- Notion workspace
- Composio account for Notion integration

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/notion-ai-assistant.git
cd notion-ai-assistant
```

2. Create virtual environment in the bot directory:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Navigate to the bot directory and install dependencies:
```bash
cd notion-ai-assistant
pip install -r requirements.txt
```

4. Set up environment variables in a `.env` file in the root directory:
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
COMPOSIO_TOKEN=your-composio-token
OPENAI_API_KEY=your-openai-key  # Optional, for enhanced responses
```

### Slack App Setup

1. Create a Slack app at api.slack.com
2. Enable Socket Mode and generate an app token
3. Add Bot Token Scopes: `chat:write`, `im:history`, `channels:history`, `app_mentions:read`
4. Install the app to your workspace
5. Save the tokens to your `.env` file

### Composio Setup

1. Sign up at app.composio.dev
2. Connect your Notion account
3. Copy your API key to `.env`

## Usage

### Running the Bot

```bash
# From the notion-ai-assistant directory
python app.py
```

### Slack Commands

Message the bot directly or mention it in a channel:

- **Create a page**: "Create a page called Meeting Notes"
- **Search content**: "Search for project roadmap in Notion"
- **List databases**: "List my databases" or "Show databases"
- **Get help**: "What can you do?" or "Help"

## Project Structure

```
notion-ai-assistant/
├── app.py              # Main bot application
├── listeners/          # Event handlers and integrations
│   ├── assistant.py    # Slack AI Agents API
│   ├── events/         # Message and thread handlers
│   └── llm_caller_litellm.py  # LLM integration
├── requirements.txt    # Python dependencies
├── manifest.json       # Slack app manifest
└── README.md          # Bot-specific documentation
```

## Features in Detail

### Notion Operations
- **List Databases**: Shows all Notion databases in your workspace
- **Create Pages**: Creates new Notion pages with specified titles
- **Search Content**: Searches across your Notion workspace

### Slack Features
- **Socket Mode**: Real-time connection without public endpoints
- **Interactive Buttons**: Quick actions for common operations
- **Rich Formatting**: Clean Slack blocks for better readability
- **DM Support**: Works in direct messages and channels

## Troubleshooting

### Bot not responding
- Check that both `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` are set
- Ensure Socket Mode is enabled in your Slack app
- Verify the bot is invited to the channel

### Notion operations failing
- Ensure your Notion is connected in Composio
- Check that `COMPOSIO_TOKEN` is valid
- Verify you have access to the Notion workspace

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [Slack Bolt for Python](https://slack.dev/bolt-python/)
- Notion operations powered by [Composio](https://composio.dev/)