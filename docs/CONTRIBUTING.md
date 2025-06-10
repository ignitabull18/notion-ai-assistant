# Contributing to Agno Slack-Notion Assistant

Thank you for your interest in contributing to the Agno project! This guide will help you get started.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Docker (for containerized testing)
- A Slack workspace with admin privileges
- Access to Task Master for task tracking

### Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/agno.git
   cd agno
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Copy environment template**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## 📋 Development Workflow

### Before Starting Work

1. **Check Task Master**
   ```bash
   taskmaster-ai next_task
   ```
   Always pick up the next available task or create a new one if needed.

2. **Update task status**
   ```bash
   taskmaster-ai set_task_status --id <task_id> --status in-progress
   ```

### During Development

1. **Follow the architecture**
   - Review `plan.md` for system design
   - Check `CLAUDE.md` for implementation rules
   - Refer to `docs/slack-integration-guide.md` for Slack specifics

2. **Use Agno's built-in tools**
   - ❌ NO custom schedulers → Use `agno.tools.scheduler.SchedulerTools`
   - ❌ NO direct SDK imports → Use LiteLLM proxy for all LLM calls
   - ✅ Two-layer Slack strategy:
     - `slack_sdk` for advanced features (AI Agents API, blocks, modals)
     - `ComposioTools` for simple messaging

3. **Run tests frequently**
   ```bash
   pytest tests/
   ```

### Committing Changes

1. **Include task reference in commit message**
   ```bash
   git commit -m "Implement feature X (Task #5)"
   ```

2. **Ensure pre-commit passes**
   Pre-commit will automatically:
   - Format code with Black
   - Sort imports with isort
   - Check for forbidden imports
   - Run tests

3. **Update task status**
   ```bash
   taskmaster-ai set_task_status --id <task_id> --status done
   ```

## 🚫 Critical Rules

### NEVER Import Provider SDKs Directly

```python
# ❌ WRONG
import openai
import anthropic

# ✅ CORRECT
from agno.models.litellm import LiteLLMOpenAI
model = LiteLLMOpenAI(base_url=os.getenv("LITELLM_BASE_URL"))
```

### NEVER Create Custom Infrastructure

```python
# ❌ WRONG
class MyScheduler:
    def schedule_task(self):
        pass

# ✅ CORRECT
from agno.tools.scheduler import SchedulerTools
scheduler = SchedulerTools()
```

### Keep FastAPI Minimal

The FastAPI wrapper should be ≤50 lines. Delegate all logic to Agno tools.

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Test specific module
```bash
pytest tests/test_slack_client.py -v
```

### Test Docker build
```bash
docker build . -t agno-test
docker run --rm agno-test python -m pytest
```

## 📁 Project Structure

```
agno/
├── src/                    # Main application code
│   ├── agent/             # Agno agent implementation
│   ├── app/               # FastAPI wrapper
│   └── slack_client.py    # Slack SDK wrapper
├── notion-ai-assistant/    # Bolt app (Slack CLI)
├── tests/                  # All test files
├── docs/                   # Documentation
└── .taskmaster/           # Task management
```

## 🔄 Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/task-5-implement-x
   ```

2. **Push changes**
   ```bash
   git push origin feature/task-5-implement-x
   ```

3. **Open PR with:**
   - Clear title referencing task (e.g., "Implement X (Task #5)")
   - Description of changes
   - Test results
   - Any breaking changes noted

4. **CI will automatically:**
   - Run tests on Python 3.9-3.12
   - Check for forbidden imports
   - Validate Task Master references
   - Build Docker image

## 🏗️ Architecture Decisions

### Two-Layer Slack Strategy

1. **Bolt App** (`notion-ai-assistant/`)
   - Handles AI Agents API
   - Interactive components (blocks, modals)
   - Slash commands
   - Per-workspace customization

2. **FastAPI + ComposioTools** (`src/`)
   - Simple message handling
   - Integration with other SaaS tools
   - Agent orchestration

### Bridge Communication

The Bolt app delegates complex reasoning to the FastAPI agent via HTTP:
- Endpoint: `POST /agent/ask`
- Optional authentication with `AGNO_API_KEY`
- See `docs/bolt-fastapi-bridge.md` for details

## 🐛 Debugging

### Enable debug logging
```bash
export LOG_LEVEL=DEBUG
```

### Check Slack signature verification
```python
# In src/slack_client.py
logger.debug(f"Signature verification: timestamp={timestamp}, signature={signature}")
```

### Test agent endpoint directly
```bash
curl -X POST http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "text": "Hello", "channel": "test"}'
```

## 📚 Resources

- [Agno Documentation](https://docs.agno.ai)
- [Slack API Documentation](https://api.slack.com)
- [Notion API Reference](https://developers.notion.com)
- [Task Master Guide](.taskmaster/README.md)

## 🤝 Getting Help

- Review existing issues on GitHub
- Check `docs/` for architecture guides
- Ask in the project's Slack channel
- Tag maintainers in PR comments

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Happy coding! 🚀