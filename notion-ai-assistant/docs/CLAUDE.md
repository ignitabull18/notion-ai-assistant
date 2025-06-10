# Notion AI Assistant - Claude Development Notes

## Project Overview
This is a Slack-based AI assistant that integrates with Notion using the Composio framework and Agno agent. The assistant can manage Notion workspaces through natural language commands in Slack.

## Key Technologies
- **Agno Framework**: AI agent framework for building intelligent assistants
- **Composio**: Tool integration framework that provides Notion API access
- **Slack Bolt**: Python framework for building Slack apps
- **OpenAI o4-mini**: LLM model with 200K context window and 100K output tokens

## Recent Enhancements & Configuration

### 1. Model Configuration (o4-mini)
- **Context Window**: 200K tokens (input)
- **Output Capacity**: 100K tokens (using 50K)
- **Conversation History**: 50 turns (maximized from default ~15)
- **Parameter**: Uses `max_completion_tokens` instead of `max_tokens`

### 2. Enhanced System Prompt
The agent now acts as a strategic partner with:
- Comprehensive Notion tool knowledge
- Strategic workspace planning capabilities
- Detailed response formatting (up to 50K tokens)
- Natural language understanding for all database queries
- Automatic Notion URL formatting

### 3. Beautiful Slack UI
Implemented Slack Block Kit formatting (`listeners/slack_formatter.py`) with:
- **Database Listings**: Clean cards with database names, IDs, and "Open" buttons
- **Markdown Conversion**: Headers, lists, code blocks converted to Slack blocks
- **Clickable Links**: All Notion URLs automatically become buttons
- **Smart Truncation**: Handles Slack's 50-block limit gracefully
- **Special Database Parser**: Detects and formats multi-line database listings

### 4. Composio Integration
- Uses `composio-agno` package (not `composio`)
- Tools are loaded via `composio_toolset.get_tools(apps=[App.NOTION])`
- No dedicated "list all databases" action - agent uses available tools intelligently
- Natural language processing handles all queries

## Important Technical Details

### Error Handling
- **Validation Errors**: Never pass `None` for optional parameters - omit them entirely
- **Context Limits**: Slack blocks limited to 50 per message, text fields to 2000 chars
- **Database Queries**: Agent interprets "databases" as Notion databases (not MCP/system)

### Key Files
- `listeners/agno_integration.py`: Core agent setup and configuration
- `listeners/slack_formatter.py`: Beautiful Slack UI formatting
- `listeners/assistant.py`: Slack event handling and response routing
- `requirements.txt`: Dependencies including composio-agno

### Environment Variables
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
COMPOSIO_TOKEN=...
OPENAI_API_KEY=...
```

## Common Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the assistant
python main.py

# Test Notion tools directly (without Slack)
python test_simple_notion.py
```

## Troubleshooting

### "No module named 'composio_agno'"
- Run `pip install -r requirements.txt`
- Ensure you're in the virtual environment

### Slack formatting errors
- Check for text over 2000 characters
- Ensure no more than 50 blocks per message
- Context elements limited to 150 characters

### Agent not finding databases
- Agent uses natural language - just ask normally
- "MCP databases" still means Notion databases
- No special patterns needed

## Architecture Notes
- **Singleton Agent**: One agent instance with session-based separation
- **Memory**: SQLite-based long-term memory enabled
- **Tool Loading**: 11 specific Notion tools loaded at startup
- **Response Flow**: Agent → Format response → Convert to Slack blocks → Send

## Future Considerations
- Separate agents for privacy (different databases per team)
- Enhanced database consolidation features
- Workspace organization automation

Last Updated: 2025-06-09