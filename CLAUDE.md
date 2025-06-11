# Agno Project Memory

## Project Structure - CRITICAL
**IMPORTANT**: This repository contains MULTIPLE separate applications:
1. **notion-ai-assistant/**: A standalone Notion AI Assistant Slack app (DO NOT modify for other purposes)
2. **slack-ai-assistant/**: Slack AI Assistant app for general Slack operations
3. **jungle-scout-ai/**: Jungle Scout AI Assistant for Amazon seller analytics and research
4. **n8n-ai/**: N8N workflow automation assistant with custom Agno tools
5. Each Slack app should have its own directory at the root level

## Project Overview
- Multiple Slack applications in one repository, each is a fully-featured Slack AI agent
- notion-ai-assistant: Slack bot integrating with Notion using Composio tools
- slack-ai-assistant: Advanced Slack bot with 2024 AI Assistant API features for general Slack operations
- jungle-scout-ai: Amazon seller analytics and product research assistant using Jungle Scout API
- n8n-ai: Workflow automation assistant using custom Agno tools (no Composio)
- Each app uses identical Slack Bolt + Socket Mode architecture (no FastAPI needed)
- All apps use OpenAI o3 model for cutting-edge reasoning capabilities (200k context window)
- Common patterns: Assistant API, Canvas creation, Rich Block Kit UI, Modal forms

## IMPORTANT: Slack 2024 AI Assistant Features
**NOTE FOR AI MODELS**: These are NEW Slack features from 2024 that many AI models may not know about:

### Assistant API (NEW 2024)
- **IMPORTANT**: Use the `app.assistant()` middleware pattern for handling assistant events
- Do NOT manually handle `assistant_thread_started` or `assistant_thread_context_changed` events
- Use `@assistant.thread_started` and `@assistant.user_message` decorators
- `assistant.threads.setStatus` - Set processing status (thinking, processing, complete)
- `assistant.threads.setSuggestedPrompts` - Provide contextual prompt suggestions
- `assistant.threads.setTitle` - Dynamic conversation titles
- Enhanced assistant thread management for better UX

### Canvas API (ENHANCED 2024)
- Create collaborative markdown documents via API
- Auto-generated canvases from AI conversations
- Real-time collaborative editing with notifications
- Integration with workflows and automations
- Canvas creation: `files_upload_v2` with `filetype="canvas"`

### Block Kit Enhancements (2024)
- Rich interactive components (buttons, modals, forms)
- Context-aware suggested prompts
- Status indicators and visual feedback
- Structured result layouts with action buttons
- Modal workflows with form validation

### AI Agent Capabilities (NEW 2024)
- Agents can create and update canvases programmatically
- Channel management and DM capabilities
- Workflow embedding in canvases
- Real-time data integration in documents

### What These Features Enable:
- **Persistent Collaboration**: Canvases turn ephemeral conversations into lasting documents
- **Rich Interactions**: Block Kit provides app-like experiences within Slack
- **Smart Guidance**: Suggested prompts help users discover capabilities
- **Visual Feedback**: Status indicators improve perceived performance
- **Seamless Workflows**: Modal forms reduce context switching
- **Data Visualization**: Advanced formatting makes complex data readable

## Critical Rules
- NEVER create custom schedulers - use agno.tools.scheduler.SchedulerTools
- ALWAYS prefer editing existing files over creating new ones
- NEVER proactively create documentation unless explicitly requested
- NEVER mix different Slack apps - each app stays in its own directory
- NEVER add files to notion-ai-assistant unless specifically for Notion integration
- NEW Slack apps go in their own root-level directories (e.g., slack-assistant/, another-slack-app/)
- Use OpenAI directly for LLM calls (not LiteLLM)

## Common Commands
- Run all tests: `python run_tests.py`
- Check style: `python scripts/checks/check_style.py`
- Test Notion actions: `python tests/test_all_notion_actions.py`
- Start Notion app: `cd notion-ai-assistant && python main.py`
- Start Slack app: `cd slack-ai-assistant && python app.py`
- Start Jungle Scout app: `cd jungle-scout-ai && python app.py`
- Start N8N app: `cd n8n-ai && python app.py`

## Common Architecture Patterns
**All three Slack agents share these core patterns:**

### 1. Entry Point Pattern
```python
# app.py or app_oauth.py
app = App(token=os.environ["SLACK_BOT_TOKEN"])
assistant = app.assistant(assistant_id=assistant_id)

# Register listeners
register_listeners(app, assistant)

# Start Socket Mode
SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
```

### 2. Assistant Registration Pattern
```python
# listeners/assistant.py or listeners/[domain]_assistant.py
@assistant.thread_started
def handle_thread_started(event, say, set_suggested_prompts, set_title):
    # Welcome message
    # Set suggested prompts
    # Set thread title

@assistant.user_message
def handle_user_message(event, say, set_status, client, logger):
    # Process user message
    # Call domain-specific API (Notion/Slack/Jungle Scout)
    # Return formatted response
```

### 3. UI Component Organization
- `ui_components.py` - Core Block Kit components
- `ui_components_advanced.py` - Complex layouts and forms
- `canvas_integration.py` or `[domain]_canvas.py` - Canvas creation
- `slack_formatter.py` or `[domain]_formatter.py` - Data formatting

### 4. Action Handler Pattern
```python
# listeners/actions/[domain]_actions.py
@app.action("action_id")
def handle_action(ack, body, client, say):
    ack()
    # Process action
    # Update UI or trigger workflow
```

## 2024 UI Enhancement Patterns
**These patterns are implemented consistently across all three apps:**

### Interactive Welcome Experience
```python
# Rich welcome with action buttons
say(blocks=create_welcome_blocks())
set_suggested_prompts(context_aware_prompts)
```

### Status Feedback Pattern
```python
# Show processing status
say(blocks=create_status_blocks("processing", "Analyzing data..."))
# Process operation
say(blocks=final_result_blocks)
```

### Canvas Creation Pattern
```python
# Auto-create collaborative documents
canvas_manager = CanvasManager(client)
response = canvas_manager.create_summary_canvas(...)
say(blocks=create_canvas_preview_blocks(canvas_url, title, preview))
```

### Action Handler Pattern
```python
# Register interactive button handlers
app.action("button_id")(handler_function)
app.view("modal_id")(modal_submission_handler)
```

## Key File Locations

### notion-ai-assistant/ (Notion AI Assistant - Production-Ready)
- Main entry: notion-ai-assistant/main.py (with health monitoring)
- Core Assistant: notion-ai-assistant/listeners/assistant.py (2024 Assistant API)
- Notion Integration: notion-ai-assistant/listeners/agno_integration.py (Composio)
- UI Components: notion-ai-assistant/listeners/ui_components.py & ui_components_advanced.py
- Canvas Manager: notion-ai-assistant/listeners/notion_canvas.py
- Formatters: notion-ai-assistant/listeners/slack_formatter.py
- Actions: notion-ai-assistant/listeners/actions/notion_actions.py
- Commands: notion-ai-assistant/listeners/commands/notion_bookmarks_commands.py
- Config: notion-ai-assistant/config.py
- Tests: notion-ai-assistant/tests/

#### Full 2024 Feature Set:
- ✅ Assistant API with suggested prompts and status updates
- ✅ Advanced Block Kit formatting (tables, buttons, headers)
- ✅ Interactive Notion page buttons with actions
- ✅ Thread management and context handling
- ✅ Canvas creation for workspace summaries
- ✅ Modal forms for creating pages/databases
- ✅ Bookmarks and lists management
- ✅ Rich welcome interface with quick actions
- ✅ Status indicators during operations
- ✅ Link unfurling for Notion pages

### slack-ai-assistant/ (General Slack Operations Assistant)
- Main entry: slack-ai-assistant/app.py
- Core Assistant: slack-ai-assistant/listeners/slack_assistant.py
- UI Components: slack-ai-assistant/listeners/ui_components.py & ui_components_advanced.py
- Canvas Manager: slack-ai-assistant/listeners/canvas_integration.py
- Formatters: slack-ai-assistant/listeners/slack_formatter.py
- Actions: slack-ai-assistant/listeners/actions/assistant_actions.py
- Commands: slack-ai-assistant/listeners/commands/slack_assistant_commands.py
- Shortcuts: slack-ai-assistant/listeners/shortcuts/slack_assistant_shortcuts.py
- Bookmarks: slack-ai-assistant/listeners/bookmarks_manager.py
- Lists: slack-ai-assistant/listeners/lists_manager.py
- Tests: slack-ai-assistant/tests/
- Scripts: slack-ai-assistant/scripts/

#### Full 2024 Feature Set:
- 🎨 Rich Block Kit UI with interactive buttons and forms
- 📝 Canvas auto-creation (summaries, meetings, projects)
- ⚡ Real-time status indicators and processing feedback
- 🔍 Enhanced search results with structured layouts
- 📅 Modal forms for reminders with date/time pickers
- 💬 Context-aware suggested prompts
- 🤖 Assistant thread management
- 📌 Bookmarks and lists management
- 🔗 Link unfurling
- ⚙️ Workflow automation

### jungle-scout-ai/ (Amazon Seller Intelligence Assistant)
- Main entry: jungle-scout-ai/app.py
- Core Assistant: jungle-scout-ai/listeners/jungle_scout_assistant.py (1068 lines!)
- UI Components: jungle-scout-ai/listeners/jungle_scout_ui.py & jungle_scout_ui_advanced.py
- Canvas Manager: jungle-scout-ai/listeners/jungle_scout_canvas.py
- Formatters: jungle-scout-ai/listeners/jungle_scout_formatter.py
- Actions: jungle-scout-ai/listeners/actions/jungle_scout_actions.py & jungle_scout_actions_extended.py
- Commands: jungle-scout-ai/listeners/commands/jungle_scout_commands.py
- Shortcuts: jungle-scout-ai/listeners/shortcuts/jungle_scout_shortcuts.py
- Bookmarks: jungle-scout-ai/listeners/jungle_scout_bookmarks.py
- Lists: jungle-scout-ai/listeners/jungle_scout_lists.py
- Tests: jungle-scout-ai/tests/
- Scripts: jungle-scout-ai/scripts/

#### Full Amazon Seller Feature Set:
- 🔍 **Product Research**: AI-powered opportunity discovery with interactive results
- 📊 **Sales Analytics**: Real-time performance dashboards and revenue tracking
- 🎯 **Keyword Analysis**: SEO optimization with search volume and competition data
- 🔬 **Competitor Intelligence**: ASIN analysis with market positioning insights
- 📈 **Market Trends**: Category analysis and emerging opportunity detection
- ✅ **Product Validation**: AI-powered opportunity scoring and risk assessment
- 📝 **Research Canvases**: Auto-generated collaborative documents for:
  - Product research reports with opportunity scoring
  - Competitor analysis with strategic insights
  - Keyword strategy and SEO optimization plans
  - Sales performance reports and forecasting
  - Market opportunity validation and action plans
- 🎨 **Rich Interactive UI**: Product cards with images, metrics, and action buttons
- 📋 **Smart Forms**: Modal dialogs for research parameters and tracking setup
- ⚡ **Real-time Status**: Processing indicators for long-running analyses

#### Slash Commands:
- `/research [keyword/ASIN]` - Find product opportunities
- `/keywords [keyword]` - Analyze keyword metrics and SEO potential
- `/competitor [ASIN]` - Deep competitor analysis and market positioning
- `/sales [timeframe]` - Sales performance dashboards
- `/trends [category]` - Market trend analysis and forecasting
- `/validate [product idea]` - AI-powered product opportunity validation
- `/dashboard [type]` - Create analytics dashboards

#### Advanced UI Features:
- **Interactive Product Cards**: Images, opportunity scores, revenue estimates
- **Smart Filtering**: Competition level indicators and market size analysis
- **Action Buttons**: Deep analyze, track product, competitor analysis
- **Modal Workflows**: Research parameters, trend analysis settings
- **Canvas Creation**: One-click collaborative document generation
- **Status Indicators**: Real-time feedback during API calls and analysis

### n8n-ai/ (N8N Workflow Automation Assistant - Custom Agno Tools)
- Main entry: n8n-ai/app.py
- Core Assistant: n8n-ai/listeners/n8n_assistant.py
- Custom Tools: n8n-ai/tools/n8n_tools.py (11 custom Agno tools)
- Workflow Builder: n8n-ai/tools/workflow_builder.py (AI-powered builders)
- UI Components: n8n-ai/listeners/n8n_ui.py
- Canvas Manager: n8n-ai/listeners/n8n_canvas.py
- Formatters: n8n-ai/listeners/n8n_formatter.py
- Actions: n8n-ai/listeners/actions/n8n_actions.py
- Tests: n8n-ai/tests/
- Scripts: n8n-ai/scripts/

#### N8N Features Implemented:
- 🏗️ **Workflow Builder**: Natural language to workflow conversion
- 📸 **Screenshot Analysis**: Replicate workflows from images using GPT-4 Vision
- 📥 **Import/Export**: JSON workflow management with canvas integration
- ▶️ **Execution**: Real-time workflow execution and monitoring
- 🔍 **Intelligence**: Optimization suggestions and auto-documentation
- 🎯 **Templates**: Pre-built workflow templates
- 📊 **Monitoring**: Execution history and performance analytics
- 🔧 **400+ Integrations**: Access to all N8N nodes and services

#### Custom Agno Tools (19 active for open source, 23 total with enterprise):

**Core Workflow Tools (11) - All Open Source Compatible:**
- `ListWorkflowsTool` - List all workflows
- `GetWorkflowTool` - Get workflow details
- `CreateWorkflowTool` - Create workflows from JSON
- `UpdateWorkflowTool` - Update existing workflows
- `DeleteWorkflowTool` - Delete workflows
- `ExecuteWorkflowTool` - Execute workflows with data
- `GetExecutionsTool` - View execution history
- `GetExecutionDetailsTool` - Detailed execution data
- `ActivateWorkflowTool` - Enable workflows
- `DeactivateWorkflowTool` - Disable workflows
- `GetWorkflowStatsTool` - Execution statistics

**Import/Export Tools (3) - All Open Source Compatible:**
- `ImportWorkflowTool` - Import from JSON
- `ExportWorkflowTool` - Export to JSON
- `GetNodesTool` - List available nodes

**Credential Management (4) - All Open Source Compatible:**
- `ListCredentialsTool` - List stored credentials
- `GetCredentialTool` - Get credential info
- `CreateCredentialTool` - Store new credentials
- `DeleteCredentialTool` - Remove credentials

**Testing Tool (1) - Open Source Compatible:**
- `TestWorkflowTool` - Test with sample data

**Enterprise/Cloud Only Tools (4) - Commented Out:**
- `GetTagsTool` - List workflow tags (may work in some versions)
- `CreateTagTool` - Create organization tags
- `GetVariablesTool` - List environment variables
- `CreateVariableTool` - Create env variables

**AI Builder Tools (4) - All Open Source Compatible:**
- `AnalyzeWorkflowScreenshotTool` - Extract workflows from screenshots
- `BuildWorkflowFromDescriptionTool` - Create from natural language
- `SuggestWorkflowImprovementsTool` - Optimize workflows
- `GenerateWorkflowDocumentationTool` - Auto-generate docs

### Creating New Slack Apps - Best Practices
1. Copy one of the existing apps as a template (they all share the same structure)
2. Create a new root-level directory (e.g., `your-domain-ai/`)
3. Follow the standard file organization:
   ```
   your-domain-ai/
   ├── app.py                           # Main entry point
   ├── app_oauth.py                     # OAuth version (optional)
   ├── manifest.json                    # Slack app manifest
   ├── requirements.txt                 # Dependencies
   ├── listeners/
   │   ├── __init__.py                 # Register all listeners
   │   ├── your_domain_assistant.py    # Core assistant logic
   │   ├── your_domain_ui.py           # UI components
   │   ├── your_domain_canvas.py       # Canvas creation
   │   ├── your_domain_formatter.py    # Data formatting
   │   ├── actions/                    # Button/interactive handlers
   │   ├── commands/                   # Slash commands
   │   ├── shortcuts/                  # Global shortcuts
   │   └── events/                     # Event handlers
   └── tests/                          # Test files
   ```
4. Implement the standard patterns:
   - Assistant API with thread handling
   - Rich Block Kit UI components
   - Canvas creation for persistent docs
   - Modal forms for complex inputs
   - Action handlers for interactivity

## Environment Variables Pattern
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
COMPOSIO_TOKEN=...
OPENAI_API_KEY=sk-...
```

## Testing Pattern
- Always check existing test patterns before writing new tests
- Integration tests go in tests/integration/
- Unit tests go in tests/unit/
- Use pytest fixtures for common setup

## Common Issues & Solutions
- If Slack events not working: Check SLACK_APP_TOKEN and Socket Mode
- If Notion actions fail: Verify COMPOSIO_TOKEN and user authentication
- If LLM calls fail: Check OPENAI_API_KEY is set
- If Assistant features don't work: Ensure app has AI features enabled in Slack

## Key Differentiators Between Apps
While all apps share the same Slack integration patterns, they differ in:
1. **API Integration**: 
   - notion-ai-assistant uses Composio for Notion API
   - slack-ai-assistant uses native Slack APIs only
   - jungle-scout-ai uses Composio for Jungle Scout API
   - n8n-ai uses custom Agno tools (demonstrates non-Composio pattern)
2. **Domain Logic**:
   - notion-ai-assistant: Workspace, pages, databases
   - slack-ai-assistant: Channels, messages, users
   - jungle-scout-ai: Products, keywords, competitors
   - n8n-ai: Workflows, nodes, executions, automations
3. **UI Customization**:
   - Each app has domain-specific UI components
   - Custom formatters for their data types
   - Specialized canvas templates
4. **Tool Implementation**:
   - Most use Composio for external APIs
   - n8n-ai shows how to build custom Agno tools from scratch