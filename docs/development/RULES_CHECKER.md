# 🚨 AGNO PROJECT RULES CHECKER 🚨

## Before Writing ANY Code, Check This List:

### 1. Are you about to import `slack_sdk`?
❌ **STOP!** Use `from agno.tools.composio import ComposioTools` and `SlackWebhookHandler`

### 2. Are you creating a scheduler?
❌ **STOP!** Use `from agno.tools.scheduler import SchedulerTools`

### 3. Are you writing caching code?
❌ **STOP!** Use the built-in `@cached_tool` parameter on Agno tools

### 4. Are you importing `openai`, `anthropic`, or any LLM SDK?
❌ **STOP!** Use the LiteLLM proxy via `agno.models.litellm.LiteLLMOpenAI`

### 5. Are you creating storage/database code?
❌ **STOP!** Use `from agno.storage.sqlite import SqliteStorage` or `from agno.storage.postgres import PostgresStorage`

### 6. Are you handling Slack webhooks/verification?
❌ **STOP!** Use `SlackWebhookHandler` from ComposioTools

### 7. Are you creating utility functions?
❌ **STOP!** Check the Agno documentation first - it probably already exists

### 8. Is your FastAPI file growing beyond 50 lines?
❌ **STOP!** You're doing too much - let Composio and Agno handle it

## The Golden Rule:
**If you're writing more than 10 lines of code for something that sounds like infrastructure (scheduling, caching, webhooks, storage, etc.), you're probably doing it wrong. Agno already has it built-in.**

## Correct Imports:
```python
# ✅ CORRECT
from agno.tools.composio import ComposioTools, SlackWebhookHandler
from agno.tools.scheduler import SchedulerTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.knowledge import KnowledgeTools
from agno.tools.crawl4ai import Crawl4aiTools
from agno.storage.sqlite import SqliteStorage
from agno.storage.postgres import PostgresStorage
from agno.models.litellm import LiteLLMOpenAI

# ❌ WRONG - NEVER USE THESE
import slack_sdk  # NO!
import openai  # NO!
from apscheduler import ...  # NO!
import schedule  # NO!
```

## Before Every Commit:
1. Run this checklist
2. Delete any custom infrastructure code
3. Use Agno's built-in tools instead
4. Keep it simple - Agno handles the complexity