# 🔧 N8N AI Assistant for Slack

Build, deploy, and manage n8n workflows through natural language in Slack.

## Features

### 🏗️ **Workflow Builder**
- Create workflows from natural language descriptions
- Analyze screenshots of existing workflows and replicate them
- Access 400+ pre-built integrations
- Smart node recommendations based on use case

### 📥 **Import/Export**
- Import workflow JSON files directly
- Export workflows to collaborative canvases
- Version control friendly JSON format
- Bulk import/export capabilities

### ▶️ **Execution & Monitoring**
- Execute workflows on-demand
- Real-time execution status
- View execution history and logs
- Performance analytics

### 🔍 **Intelligence**
- Workflow optimization suggestions
- Automatic documentation generation
- Error analysis and troubleshooting
- Best practice recommendations

## Quick Start

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd n8n-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Set up N8N**
   - Install N8N: `npm install -g n8n`
   - Start N8N: `n8n start`
   - Get API key from Settings → API

5. **Run the assistant**
   ```bash
   python app.py
   ```

## Usage Examples

### Natural Language Workflow Creation
> "Create a workflow that monitors Slack for mentions of bugs, creates GitHub issues, and sends a summary email every Friday"

### Screenshot Analysis
> "Here's a screenshot of a workflow I saw on Twitter. Can you build this for me?"

### JSON Import
> "Import this workflow: {paste JSON}"

### Workflow Management
- `/n8n list` - Show all workflows
- `/n8n execute [workflow-id]` - Run a workflow
- `/n8n create` - Start workflow builder
- `/n8n import` - Import workflow JSON

## Custom Agno Tools

This assistant uses custom Agno tools for N8N integration.

### Open Source vs Enterprise Features

The N8N assistant is configured for **open source compatibility** by default. Some features are only available in N8N Enterprise/Cloud versions:

**Always Available (Open Source):**
- ✅ All workflow management (create, read, update, delete, execute)
- ✅ Credential management
- ✅ Import/Export functionality
- ✅ Execution monitoring and statistics
- ✅ AI-powered workflow building
- ✅ All core automation features

**Enterprise/Cloud Only (Commented Out):**
- ❌ Variables API - Environment variables for workflows
- ❌ Tags API - Workflow organization with tags
- ❌ Advanced permissions and SSO
- ❌ Some advanced API features

To enable enterprise features, uncomment the relevant tools in `tools/n8n_extended_tools.py`.

### Core Tools
- `ListWorkflowsTool` - List all workflows
- `GetWorkflowTool` - Get workflow details
- `CreateWorkflowTool` - Create new workflows
- `UpdateWorkflowTool` - Update existing workflows
- `ExecuteWorkflowTool` - Execute workflows
- `ActivateWorkflowTool` - Activate workflows
- `DeactivateWorkflowTool` - Deactivate workflows

### Builder Tools
- `AnalyzeWorkflowScreenshotTool` - Extract workflow from screenshots
- `BuildWorkflowFromDescriptionTool` - Create from natural language
- `SuggestWorkflowImprovementsTool` - Optimize workflows
- `GenerateWorkflowDocumentationTool` - Auto-generate docs

## Architecture

```
n8n-ai/
├── app.py                    # Main entry point
├── tools/                    # Custom Agno tools
│   ├── n8n_tools.py         # N8N API integration
│   └── workflow_builder.py  # AI-powered builders
├── listeners/               # Slack event handlers
│   ├── n8n_assistant.py    # Core assistant logic
│   ├── n8n_ui.py          # UI components
│   ├── n8n_formatter.py   # Response formatting
│   └── n8n_canvas.py      # Canvas creation
└── tests/                  # Test suite
```

## Workflow Templates

The assistant includes templates for common use cases:
- **Slack to Email** - Forward important messages
- **Daily Reports** - Automated reporting
- **Data Sync** - Database synchronization
- **AI Processing** - LLM-powered workflows

## Requirements

- Python 3.9+
- N8N instance (local or cloud)
- Slack workspace with AI features enabled
- OpenAI API key (for vision and LLM features)

## Configuration

### N8N Setup
1. Enable API access in N8N settings
2. Create API key or use username/password
3. Configure webhook URL if using cloud N8N

### Slack App Setup
1. Create app at api.slack.com
2. Enable Socket Mode
3. Add bot scopes (see manifest.json)
4. Install to workspace

## Security

- API keys stored in environment variables
- Secure credential handling
- Rate limiting on API calls
- Input validation on all user inputs

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.