# Project Structure

## 📁 Directory Organization

```
notion-ai-assistant/
├── 📄 main.py                    # Entry point for the Slack bot
├── 📄 requirements.txt           # Python dependencies
├── 📄 pyproject.toml            # Project configuration
├── 📄 manifest.json             # Slack app manifest
├── 📄 run_tests.py              # Test runner script
├── 📄 README.md                 # Project overview
├── 📄 CONTRIBUTING.md           # Contribution guidelines
├── 📄 FEATURES.md              # Feature documentation
├── 📄 LICENSE                  # License file
│
├── 📂 listeners/               # Slack event listeners and core logic
│   ├── __init__.py
│   ├── agno_integration.py     # Agno agent setup and configuration
│   ├── assistant.py            # Main Slack assistant handlers
│   ├── delegate_to_agent.py    # Agent delegation logic
│   ├── llm_caller_litellm.py   # LLM integration
│   ├── slack_formatter.py      # Slack Block Kit formatting
│   └── 📂 events/              # Slack event handlers
│       ├── __init__.py
│       ├── assistant_thread_context_changed.py
│       ├── assistant_thread_started.py
│       ├── thread_context_store.py
│       └── user_message.py
│
├── 📂 data/                    # Data storage
│   └── notion_memories.db      # SQLite database for agent memory
│
├── 📂 docs/                    # Documentation
│   ├── ASSISTANT_PROFILE.md    # Assistant description and features
│   ├── ONBOARDING_GUIDE.md     # User onboarding guide
│   ├── APP_LISTING.md          # App directory listing info
│   └── CLAUDE.md               # Development notes for Claude
│
├── 📂 scripts/                 # Utility scripts
│   ├── 📂 checks/              # Validation and checking scripts
│   │   ├── check_actions.py    # Check available Composio actions
│   │   ├── check_composio_api.py
│   │   ├── check_composio_raw.py
│   │   ├── check_context_limits.py
│   │   └── check_style.py      # Code style checker
│   └── 📂 development/         # Development helper scripts
│       ├── get_action_schemas.py
│       ├── inspect_tools.py
│       └── show_parameters.py
│
├── 📂 tests/                   # Test files
│   ├── __init__.py
│   ├── test_all_notion_actions.py
│   ├── test_composio.py
│   ├── 📂 unit/               # Unit tests
│   │   ├── test_slack_formatter_standalone.py
│   │   └── test_slack_formatting.py
│   └── 📂 integration/        # Integration tests
│       ├── test_enhanced_context.py
│       ├── test_enhanced_prompt.py
│       ├── test_fix.py
│       ├── test_memory.py
│       ├── test_notion_tools.py
│       └── test_simple_notion.py
│
└── 📂 venv/                   # Virtual environment (git-ignored)
```

## 🔧 Key Files

### Core Application
- **main.py**: Entry point that starts the Slack bot
- **listeners/agno_integration.py**: Core agent configuration with Composio tools
- **listeners/assistant.py**: Slack event handling and routing
- **listeners/slack_formatter.py**: Beautiful Slack UI formatting

### Configuration
- **requirements.txt**: Python dependencies (composio-agno, slack-bolt, etc.)
- **manifest.json**: Slack app configuration
- **.env**: Environment variables (not in git)

### Documentation
- **README.md**: Project overview and setup instructions
- **docs/CLAUDE.md**: Technical notes for development
- **docs/ONBOARDING_GUIDE.md**: User guide for getting started

## 🚀 Quick Commands

```bash
# Run the bot
python main.py

# Run all tests
python run_tests.py

# Check available Notion tools
python scripts/checks/check_actions.py

# Test Notion directly (without Slack)
python tests/integration/test_simple_notion.py

# Check code style
python scripts/checks/check_style.py
```

## 📦 Development Workflow

1. **Feature Development**: Work in `listeners/` for core features
2. **Testing**: Add tests to `tests/unit/` or `tests/integration/`
3. **Scripts**: Add utility scripts to `scripts/development/`
4. **Documentation**: Update docs in `docs/` directory

## 🔐 Environment Variables

Create a `.env` file with:
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
COMPOSIO_TOKEN=...
OPENAI_API_KEY=...
```

## 🧪 Testing Structure

- **Unit Tests** (`tests/unit/`): Test individual components
- **Integration Tests** (`tests/integration/`): Test full workflows
- **Check Scripts** (`scripts/checks/`): Validate configurations

## 📝 Notes

- Virtual environment (`venv/`) should not be committed
- Database files in `data/` are local only
- All test files are organized by type
- Scripts are separated by purpose (checks vs development)