# Analysis of AI Agents Structure and Features

## Overview
This document analyzes the structure and features of three AI agents in the Agno project:
1. **notion-ai-assistant**: Notion integration with Composio API
2. **slack-ai-assistant**: General Slack operations
3. **jungle-scout-ai**: Amazon seller analytics with Jungle Scout API

## Common Architecture Pattern

### 1. Core Structure (Bolt + FastAPI)
All three agents share the same base architecture:

```
app-name/
├── app.py              # Main entry (standard Slack app)
├── main.py             # Production entry (notion-ai-assistant only)
├── listeners/
│   ├── __init__.py     # Register all listeners
│   ├── assistant.py    # 2024 Assistant API handler
│   ├── actions/        # Button/interactive handlers
│   ├── commands/       # Slash command handlers
│   ├── events/         # Event handlers
│   ├── messages/       # Message handlers
│   ├── shortcuts/      # Shortcut handlers
│   └── views/          # Modal view handlers
├── requirements.txt
└── manifest.json
```

### 2. Slack 2024 AI Assistant Features

All three agents implement the new Slack AI Assistant features:

#### Assistant API Pattern
```python
# Common pattern across all agents
from slack_bolt import Assistant
assistant = Assistant()

@assistant.thread_started
def start_assistant_thread(say, set_suggested_prompts, ...):
    # Show welcome UI
    # Set context-aware prompts

@assistant.user_message
def respond_in_assistant_thread(payload, set_status, say, ...):
    # Process message
    # Show status updates
    # Return rich responses
```

#### Block Kit UI Components
- **Welcome blocks** with action buttons
- **Status blocks** for processing feedback
- **Result blocks** with structured data
- **Modal forms** for complex inputs
- **Action handlers** for interactivity

#### Canvas Integration
Each agent has its own canvas manager:
- `notion-ai-assistant/listeners/notion_canvas.py`
- `slack-ai-assistant/listeners/canvas_integration.py`
- `jungle-scout-ai/listeners/jungle_scout_canvas.py`

## Agent-Specific Features

### 1. notion-ai-assistant

**Primary Purpose**: Notion workspace management via Composio API

**Key Files**:
- `main.py`: Production entry with health monitoring
- `listeners/agno_integration.py`: Agno framework integration
- `listeners/delegate_to_agent.py`: Agent delegation
- `config.py`: Comprehensive configuration

**Unique Features**:
- Production-ready with health checks and monitoring
- Composio API integration for Notion operations
- Agno framework for enhanced agent capabilities
- Advanced error handling and security middleware
- Database health monitoring

**API Used**: Composio (for Notion)
```python
from composio_agno import ComposioToolSet
composio_client = ComposioToolSet(api_key=config.composio.api_key)
```

**Canvas Types**:
- Workspace summaries
- Database schemas
- Project templates
- Workflow documentation

### 2. slack-ai-assistant

**Primary Purpose**: General Slack workspace automation

**Key Files**:
- `app.py`: Simple entry point
- `listeners/slack_assistant.py`: Core assistant logic
- `listeners/canvas_integration.py`: Canvas creation
- `listeners/workflow_manager.py`: Workflow automation

**Unique Features**:
- Channel summarization
- Smart reminders with date/time pickers
- Message search and analysis
- Workflow automation templates
- Lists and bookmarks management

**API Used**: Slack API only
```python
from slack_sdk import WebClient
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
```

**Canvas Types**:
- Channel summaries
- Meeting notes
- Project plans
- Task lists

### 3. jungle-scout-ai

**Primary Purpose**: Amazon seller intelligence and analytics

**Key Files**:
- `app.py`: Simple entry point
- `listeners/jungle_scout_assistant.py`: Core logic (1068 lines!)
- `listeners/jungle_scout_ui.py`: Advanced product UI
- `listeners/jungle_scout_canvas.py`: Research canvases

**Unique Features**:
- Product research with opportunity scoring
- Keyword analysis for SEO
- Competitor intelligence
- Sales analytics dashboards
- Market trend analysis
- Product validation scoring

**API Used**: Jungle Scout via Composio
```python
from composio import ComposioToolSet
self.composio_toolset = ComposioToolSet()
# Uses Jungle Scout actions like:
# JUNGLESCOUT_QUERY_THE_PRODUCT_DATABASE
# JUNGLESCOUT_RETRIEVE_KEYWORD_DATA_FOR_SPECIFIED_ASINS
```

**Canvas Types**:
- Product research reports
- Competitor analysis
- Keyword strategy
- Sales reports
- Market opportunity validation

## Common UI/UX Patterns

### 1. Welcome Experience
All agents provide rich welcome interfaces:
```python
def create_welcome_blocks():
    return [
        header_block,
        description_section,
        feature_fields,
        action_buttons
    ]
```

### 2. Status Feedback
Real-time processing indicators:
```python
# Show processing
say(blocks=create_status_blocks("processing", "Analyzing..."))
# Update with results
say(blocks=final_result_blocks)
```

### 3. Suggested Prompts
Context-aware prompt suggestions:
```python
set_suggested_prompts(prompts=[
    {"title": "Quick action", "message": "command details"},
    # Context-specific prompts
])
```

### 4. Modal Forms
Interactive forms for complex inputs:
```python
def create_input_modal():
    return {
        "type": "modal",
        "callback_id": "modal_id",
        "blocks": [input_fields]
    }
```

## Key Differences

### 1. Entry Points
- **notion-ai-assistant**: Has both `app.py` and `main.py` (production)
- **Others**: Only `app.py` (simpler structure)

### 2. External APIs
- **notion-ai-assistant**: Composio for Notion
- **slack-ai-assistant**: Slack API only
- **jungle-scout-ai**: Composio for Jungle Scout

### 3. Complexity
- **jungle-scout-ai**: Most complex assistant logic (1068 lines)
- **notion-ai-assistant**: Most production features
- **slack-ai-assistant**: Simplest, focused on Slack

### 4. LLM Integration
- **notion-ai-assistant**: Uses `llm_caller_litellm.py` (but calls OpenAI)
- **Others**: Direct OpenAI via `llm_caller_openai.py`

## Best Practices Observed

### 1. Modular Structure
- Separate files for different listener types
- UI components isolated from logic
- Canvas managers as standalone classes

### 2. Error Handling
```python
@handle_errors  # Decorator pattern
def process_command(...):
    try:
        # Main logic
    except Exception as e:
        logger.error(f"Error: {e}")
        say("User-friendly error message")
```

### 3. Retry Logic
```python
@with_retry(max_attempts=3)
def api_call(...):
    # API call that might fail
```

### 4. Memory Management
- Thread context storage
- Conversation history tracking
- Lists and bookmarks persistence

### 5. Canvas Creation Pattern
```python
def create_canvas(channel_id, content_type, data):
    content = generate_markdown(data)
    response = client.files_upload_v2(
        channels=[channel_id],
        file_uploads=[{
            "file": content.encode('utf-8'),
            "filename": f"{content_type}-{timestamp}.md",
            "title": f"📊 {title}"
        }],
        filetype="canvas"
    )
    return response
```

## Recommendations for New Agents

1. **Start with slack-ai-assistant structure** - It's the simplest
2. **Add domain-specific features** in separate files
3. **Implement all 2024 Slack features**:
   - Assistant API with status updates
   - Rich Block Kit UI
   - Canvas creation
   - Interactive components
4. **Use common patterns**:
   - Welcome blocks
   - Status indicators
   - Suggested prompts
   - Modal forms
5. **Follow naming conventions**:
   - `app_name_feature.py` for feature files
   - `create_X_blocks()` for UI functions
   - `handle_X()` for handlers

## Environment Variables

### Common to all:
- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`
- `OPENAI_API_KEY`

### Agent-specific:
- **notion-ai-assistant**: `COMPOSIO_TOKEN`
- **jungle-scout-ai**: `COMPOSIO_TOKEN` (for Jungle Scout)

## Testing Patterns

All agents have similar test structures:
```
tests/
├── listeners/
│   ├── actions/
│   ├── commands/
│   ├── events/
│   ├── messages/
│   ├── shortcuts/
│   └── views/
└── integration/
```

This consistent structure makes it easy to add new agents following the same patterns.