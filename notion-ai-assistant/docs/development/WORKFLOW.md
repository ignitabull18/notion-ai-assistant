# Slack Agent Creation Workflow

This workflow provides step-by-step instructions for creating a new Slack AI agent with Agno backend and Composio integrations, following our established production patterns.

## Prerequisites

Before starting, ensure you have:
- [ ] Python 3.9+ installed
- [ ] Docker and Docker Compose installed
- [ ] A Slack workspace where you can create apps
- [ ] OpenAI API key
- [ ] Composio account (for tool integrations)
- [ ] Access to this reference implementation

## Phase 1: Slack App Setup (30 minutes)

### Step 1: Create Slack App
1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Your Service AI Assistant")
4. Select your workspace
5. Click "Create App"

### Step 2: Configure OAuth & Permissions
1. Navigate to "OAuth & Permissions" in sidebar
2. Under "Bot Token Scopes", add these scopes:
   ```
   app_mentions:read
   channels:history
   channels:join
   chat:write
   im:history
   im:write
   users:read
   assistant:write
   ```
3. Click "Install to Workspace"
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### Step 3: Enable Socket Mode
1. Navigate to "Socket Mode" in sidebar
2. Toggle "Enable Socket Mode" ON
3. Click "Generate" to create an app token
4. Name it "socket-token"
5. Copy the token (starts with `xapp-`)

### Step 4: Configure Event Subscriptions
1. Navigate to "Event Subscriptions" in sidebar
2. Toggle "Enable Events" ON
3. Under "Subscribe to bot events", add:
   ```
   app_mention
   message.channels
   message.im
   assistant_thread_started
   assistant_thread_context_changed
   ```
4. Save changes

### Step 5: Enable Assistant Features
1. Navigate to "App Home" in sidebar
2. Enable "Messages Tab"
3. Check "Allow users to send Slash commands and messages"

### Step 6: Get Signing Secret
1. Navigate to "Basic Information"
2. Under "App Credentials", copy "Signing Secret"

## Phase 2: Composio Setup (15 minutes)

### Step 1: Create Composio Account
1. Go to https://app.composio.dev
2. Sign up or log in
3. Navigate to "API Keys"
4. Create and copy your API key

### Step 2: Connect Your Integration
1. Navigate to "Connected Accounts"
2. Click "Add Account"
3. Select your service (e.g., Notion, GitHub, Jira)
4. Follow the OAuth flow to connect
5. Note the connection status

### Step 3: Identify Available Tools
1. Navigate to "Tools"
2. Search for your connected service
3. Note the tool names you'll use (e.g., `NOTION_CREATE_PAGE`)

## Phase 3: Project Setup (20 minutes)

### Step 1: Clone Base Structure
```bash
# Clone the reference implementation
cp -r notion-ai-assistant/ your-service-ai-assistant/
cd your-service-ai-assistant/

# Remove old git history
rm -rf .git
git init

# Remove service-specific files
rm -rf data/ logs/ *.db
```

### Step 2: Update Project Configuration

#### 2.1 Update `manifest.json`
```json
{
  "name": "Your Service AI Assistant",
  "description": "AI-powered assistant for Your Service integration in Slack",
  "long_description": "A comprehensive Slack assistant that helps teams interact with Your Service...",
  "background_color": "#7B68EE",
  "primary_color": "#5A4FCF"
}
```

#### 2.2 Update `pyproject.toml`
```toml
[project]
name = "your-service-ai-assistant"
version = "1.0.0"
description = "Slack AI Assistant for Your Service"
```

#### 2.3 Update `docker-compose.yml`
```yaml
services:
  your-service-ai-assistant:  # Change service name
    container_name: your-service-ai-assistant
    # ... rest remains the same
```

### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Slack Configuration (from Phase 1)
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_APP_TOKEN=xapp-your-token-here
SLACK_SIGNING_SECRET=your-secret-here

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4

# Composio Configuration (from Phase 2)
COMPOSIO_API_KEY=your-composio-key-here

# Your Service Configuration (if needed)
YOUR_SERVICE_API_KEY=your-api-key
YOUR_SERVICE_BASE_URL=https://api.yourservice.com
```

## Phase 4: Integration Development (45 minutes)

### Step 1: Create Integration Module
Create `listeners/your_service_integration.py`:

```python
"""
Your Service integration using Composio and Agno
"""
import re
from typing import Dict, Any, List, Optional
import agno
from agno.models import BaseTool
from composio_agno import ComposioToolSet
from listeners.slack_formatter import format_blocks_from_markdown

from utils.errors import error_handler, ComposioAPIError
from utils.monitoring import metrics
from utils.retry import api_retry, with_circuit_breaker

# Initialize Composio client
composio = ComposioToolSet()

# Intent patterns for your service
YOUR_SERVICE_PATTERNS = [
    r'\byour[- ]?service\b',
    r'\b(create|update|search|list)\b.*\b(items?|records?|entries?)\b',
    # Add patterns specific to your service
]

def detect_your_service_intent(message: str) -> bool:
    """Detect if message is related to Your Service"""
    message_lower = message.lower()
    return any(re.search(pattern, message_lower) for pattern in YOUR_SERVICE_PATTERNS)

@api_retry.retry
@with_circuit_breaker("composio")
async def process_with_agent(
    user_id: str,
    message: str,
    channel_id: str,
    thread_ts: Optional[str] = None
) -> Dict[str, Any]:
    """Process Your Service requests using Agno agent"""
    
    with metrics.timer("your_service.agent_processing"):
        try:
            # Initialize Agno agent
            agent = agno.Agent(
                name="your-service-assistant",
                model="gpt-4",
                system_prompt=f"""You are a helpful AI assistant integrated with Your Service.
                
                You help users:
                - Create and manage items in Your Service
                - Search and retrieve information
                - Update and organize content
                - Perform bulk operations
                
                User Context:
                - Slack User ID: {user_id}
                - Channel: <#{channel_id}>
                
                Always be helpful, concise, and format responses clearly.
                Use Your Service tools when appropriate.
                If a task cannot be completed, explain why and suggest alternatives.
                """,
                tools=composio.get_tools(apps=["YOURSERVICE"]),
                memory=True,
                markdown_support=True
            )
            
            # Execute agent
            response = await agent.execute(message)
            
            # Format response
            formatted_response = format_agent_response(response)
            
            metrics.increment("your_service.requests.success")
            return formatted_response
            
        except Exception as e:
            metrics.increment("your_service.requests.error")
            app_error = error_handler.handle_error(
                e,
                context={
                    "integration": "your_service",
                    "user_id": user_id,
                    "message": message
                }
            )
            
            if isinstance(e, TimeoutError):
                raise ComposioAPIError(
                    "Your Service request timed out. Please try again.",
                    composio_error="timeout"
                )
            else:
                raise ComposioAPIError(
                    f"Failed to process Your Service request: {str(e)}",
                    composio_error=str(e)
                )

def format_agent_response(response: Any) -> Dict[str, Any]:
    """Format agent response for Slack"""
    # Handle string responses
    if isinstance(response, str):
        return format_blocks_from_markdown(response)
    
    # Handle AgentResponse objects
    if hasattr(response, 'output'):
        return format_blocks_from_markdown(response.output)
    
    # Handle dict responses with 'output' key
    if isinstance(response, dict) and 'output' in response:
        return format_blocks_from_markdown(response['output'])
    
    # Fallback for unexpected formats
    return format_blocks_from_markdown(str(response))
```

### Step 2: Update Assistant Handler
Edit `listeners/assistant.py`:

```python
# Add import at top
from .your_service_integration import (
    process_with_agent as process_your_service,
    detect_your_service_intent,
    format_agent_response as format_your_service_response
)

# Update the suggested prompts in start_assistant_thread
prompts: List[Dict[str, str]] = [
    {
        "title": "Create item in Your Service",
        "message": "Can you create a new item in Your Service for our project?",
    },
    {
        "title": "Search Your Service",
        "message": "Can you search for our Q4 planning documents in Your Service?",
    },
    {
        "title": "Update status",
        "message": "Can you update the status of my tasks in Your Service?",
    },
    {
        "title": "List items",
        "message": "Can you show me all items in Your Service?",
    },
]

# Update the message handler
if detect_your_service_intent(user_message):
    with metrics.timer("assistant.your_service_request"):
        import asyncio
        returned_message = asyncio.run(
            process_your_service(
                user_id=context.user_id,
                message=user_message,
                channel_id=context.channel_id,
                thread_ts=context.thread_ts
            )
        )
        if isinstance(returned_message, dict) and 'blocks' in returned_message:
            say(blocks=returned_message['blocks'], text=returned_message.get('text', 'Response'))
        else:
            formatted_response = format_your_service_response(returned_message)
            say(blocks=formatted_response['blocks'], text=formatted_response.get('text', 'Response'))
        metrics.increment("assistant.your_service_requests")
```

### Step 3: Update Configuration
Edit `config.py` to add your service configuration:

```python
@dataclass
class YourServiceConfig:
    """Your Service API configuration"""
    api_key: str = ""
    base_url: str = "https://api.yourservice.com"
    timeout: int = 30
    max_retries: int = 3

# Add to AppConfig
@dataclass
class AppConfig:
    # ... existing fields ...
    your_service: YourServiceConfig = field(default_factory=YourServiceConfig)

# Update load_from_env
if "YOUR_SERVICE_API_KEY" in os.environ:
    config.your_service.api_key = os.environ["YOUR_SERVICE_API_KEY"]
if "YOUR_SERVICE_BASE_URL" in os.environ:
    config.your_service.base_url = os.environ["YOUR_SERVICE_BASE_URL"]
```

## Phase 5: Testing (30 minutes)

### Step 1: Create Integration Tests
Create `tests/test_your_service.py`:

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from listeners.your_service_integration import (
    detect_your_service_intent,
    process_with_agent,
    format_agent_response
)

class TestYourServiceIntegration:
    
    def test_intent_detection(self):
        """Test Your Service intent detection"""
        # Positive cases
        assert detect_your_service_intent("Create a new item in Your Service")
        assert detect_your_service_intent("Search Your Service for documents")
        
        # Negative cases
        assert not detect_your_service_intent("What's the weather today?")
        assert not detect_your_service_intent("Tell me a joke")
    
    @pytest.mark.asyncio
    async def test_process_with_agent(self):
        """Test agent processing"""
        with patch('listeners.your_service_integration.agno.Agent') as mock_agent:
            mock_instance = Mock()
            mock_instance.execute = AsyncMock(return_value="Created item successfully")
            mock_agent.return_value = mock_instance
            
            result = await process_with_agent(
                user_id="U123",
                message="Create a new item",
                channel_id="C456"
            )
            
            assert 'blocks' in result
            assert mock_instance.execute.called
    
    def test_format_response(self):
        """Test response formatting"""
        # Test string response
        result = format_agent_response("Simple response")
        assert 'blocks' in result
        
        # Test dict response
        result = format_agent_response({"output": "Dict response"})
        assert 'blocks' in result
```

### Step 2: Run Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run style checks
python check_style.py

# Run your integration tests
python -m pytest tests/test_your_service.py -v

# Run all tests
python run_tests.py
```

### Step 3: Manual Testing
```bash
# Start the application
python main.py

# In another terminal, check health
curl http://localhost:3001/health

# Test in Slack
# 1. Open your Slack workspace
# 2. Find your app in Apps
# 3. Send a message: "Can you create a new item in Your Service?"
# 4. Verify the response
```

## Phase 6: Deployment (20 minutes)

### Step 1: Build Docker Image
```bash
# Build the image
docker-compose build

# Run locally
docker-compose up -d

# Check logs
docker-compose logs -f your-service-ai-assistant
```

### Step 2: Production Deployment
```bash
# Tag for production
docker tag your-service-ai-assistant:latest your-registry/your-service-ai-assistant:v1.0.0

# Push to registry
docker push your-registry/your-service-ai-assistant:v1.0.0

# Deploy (example for different platforms)
# AWS ECS: Update task definition
# Kubernetes: kubectl apply -f k8s/
# Docker host: docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Monitor Deployment
```bash
# Check health endpoint
curl https://your-domain.com/health

# Monitor logs
docker logs -f your-service-ai-assistant

# Check metrics
curl https://your-domain.com/health | jq '.checks'
```

## Phase 7: Documentation (15 minutes)

### Step 1: Update README.md
```markdown
# Your Service AI Assistant

AI-powered Slack assistant for Your Service integration.

## Features
- ✨ Natural language interface to Your Service
- 🔍 Smart search and retrieval
- 📝 Create and update items
- 🤖 Powered by GPT-4 and Agno framework

## Quick Start
1. Copy `.env.example` to `.env`
2. Configure your Slack and API credentials
3. Run `docker-compose up`

## Configuration
See `.env.example` for required environment variables.

## Usage
@mention the bot or message it directly:
- "Create a new project in Your Service"
- "Search for Q4 reports"
- "Update task status to complete"
```

### Step 2: Update FEATURES.md
Document your specific features and capabilities.

### Step 3: Create User Guide
Create a simple guide for end users explaining:
- How to interact with the bot
- Available commands
- Example use cases
- Troubleshooting tips

## Workflow Checklist

### Pre-Development
- [ ] Created Slack app with proper scopes
- [ ] Set up Composio account and connections
- [ ] Obtained all required API keys
- [ ] Cloned reference implementation

### Development
- [ ] Updated project configuration files
- [ ] Created integration module
- [ ] Updated assistant handlers
- [ ] Added service configuration
- [ ] Created comprehensive tests

### Testing
- [ ] All tests passing
- [ ] Manual testing in Slack successful
- [ ] Health checks working
- [ ] Error handling verified

### Deployment
- [ ] Docker image builds successfully
- [ ] Environment variables configured
- [ ] Deployed to production
- [ ] Monitoring active

### Documentation
- [ ] README.md updated
- [ ] FEATURES.md documented
- [ ] User guide created
- [ ] API documentation complete

## Common Integration Patterns

### Pattern 1: Simple Tool Execution
```python
# For services with straightforward tool calls
tools = composio.get_tools(apps=["YOURSERVICE"])
response = await agent.execute(message)
```

### Pattern 2: Complex Workflows
```python
# For multi-step operations
agent = agno.Agent(
    tools=composio.get_tools(apps=["YOURSERVICE"]),
    system_prompt="""
    Break down complex requests into steps:
    1. Validate requirements
    2. Execute operations in order
    3. Verify results
    """,
)
```

### Pattern 3: Hybrid Approach
```python
# Combine Composio tools with custom logic
if requires_preprocessing(message):
    processed_data = preprocess(message)
    response = await agent.execute(f"Process this data: {processed_data}")
else:
    response = await agent.execute(message)
```

## Troubleshooting Guide

### Slack Connection Issues
1. Verify app token starts with `xapp-`
2. Check Socket Mode is enabled
3. Ensure all OAuth scopes are added
4. Verify signing secret matches

### Composio Integration Issues
1. Check API key is valid
2. Verify service is connected in Composio dashboard
3. Test tools are available: `composio.get_tools(apps=["YOURSERVICE"])`
4. Check circuit breaker status in health endpoint

### Performance Issues
1. Monitor response times in logs
2. Check circuit breaker states
3. Verify rate limits aren't exceeded
4. Review memory usage in Docker

### Error Handling
1. Check structured logs for error details
2. Verify error messages are user-friendly
3. Test retry logic is working
4. Ensure circuit breakers are recovering

## Next Steps

Once your agent is deployed:
1. Monitor usage patterns and errors
2. Gather user feedback
3. Add more sophisticated workflows
4. Optimize based on metrics
5. Expand to additional Slack workspaces

Remember: The pattern is established, the infrastructure is solid. Focus on making your specific integration excellent!