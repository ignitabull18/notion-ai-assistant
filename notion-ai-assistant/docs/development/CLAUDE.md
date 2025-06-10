# Claude Development Guide for Slack AI Agents

## Project Overview
This directory contains production-ready Slack AI agents built with the Agno framework, featuring comprehensive error handling, monitoring, security, and deployment capabilities.

## Quick Commands Reference

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run linting and type checking
python check_style.py

# Run tests
python run_tests.py

# Start development server
python main.py

# Check health status
curl http://localhost:3001/health
```

### Docker Commands
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f notion-ai-assistant

# Check health
curl http://localhost:3001/health

# Stop services
docker-compose down
```

## Architecture Pattern for Slack Agents

### Core Structure (FOLLOW THIS PATTERN)
```
slack-agent/
├── main.py                     # Production entry point with health checks
├── config.py                   # Environment-based configuration
├── listeners/
│   ├── __init__.py            # Production app factory with middleware
│   ├── assistant.py           # Main assistant logic
│   ├── delegate_to_agent.py   # Agent delegation handlers
│   └── agno_integration.py    # Agno framework integration
├── utils/
│   ├── logging.py             # Structured JSON logging
│   ├── errors.py              # Custom exception hierarchy
│   ├── security.py            # Input validation & rate limiting
│   ├── monitoring.py          # Health checks & metrics
│   └── retry.py               # Retry logic & circuit breakers
├── Dockerfile                 # Production container
├── docker-compose.yml         # Local deployment
├── .env.example              # Environment template
└── requirements.txt          # Dependencies
```

## Critical Lessons Learned

### 1. Configuration Management
❌ **DON'T**: Hardcode API keys or configuration values
✅ **DO**: Use environment-based configuration with validation
```python
# Use config.py pattern
config = get_config()
api_key = config.openai.api_key  # Validated and typed
```

### 2. Error Handling
❌ **DON'T**: Let exceptions crash the app or show raw errors to users
✅ **DO**: Use structured error handling with user-friendly messages
```python
try:
    result = risky_operation()
except Exception as e:
    app_error = error_handler.handle_error(e, context={"operation": "risky"})
    say(f"❌ {app_error.user_message}")  # User-friendly message
```

### 3. Slack API Integration
❌ **DON'T**: Make API calls without retry logic or circuit breakers
✅ **DO**: Use retry decorators and proper error handling
```python
@api_retry.retry
def get_slack_data():
    return client.conversations_history(channel=channel_id)
```

### 4. Agent Integration Patterns
❌ **DON'T**: Mix agent logic directly in Slack handlers
✅ **DO**: Use dedicated integration modules with intent detection
```python
if detect_notion_intent(user_message):
    response = await process_with_agent(user_id, message, channel_id)
    formatted = format_agent_response(response)
    say(blocks=formatted['blocks'])
```

### 5. Production Middleware
❌ **DON'T**: Skip security validation and metrics collection
✅ **DO**: Implement comprehensive middleware stack
```python
# Security, metrics, and error handling middleware
app = create_production_app(config)  # Includes all middleware
```

## Environment Variables Checklist

### Required for All Slack Agents
```bash
# Slack Configuration (ALWAYS REQUIRED)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token  # Socket Mode
SLACK_SIGNING_SECRET=your-signing-secret

# Environment Settings
ENVIRONMENT=development|production
DEBUG=true|false
LOG_LEVEL=debug|info|warning|error
```

### Common Integration Variables
```bash
# OpenAI (if using LLM features)
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4

# Composio (if using tool integrations)
COMPOSIO_API_KEY=your-composio-key

# Security (production)
RATE_LIMIT_PER_MINUTE=60
MAX_MESSAGE_LENGTH=4000
ALLOWED_USERS=U123,U456  # Optional: restrict users
ALLOWED_CHANNELS=C123,C456  # Optional: restrict channels
```

## Slack App Configuration Requirements

### OAuth Scopes (Bot Token)
```
app_mentions:read     # Respond to @mentions
channels:history      # Read channel messages
channels:join         # Join public channels
chat:write            # Send messages
im:history           # Read DM history
im:write             # Send DMs
users:read           # Get user information
assistant:write      # Use Assistant features
```

### Event Subscriptions
```
app_mention          # Handle @mentions
message.channels     # Channel messages
message.im          # Direct messages
assistant_thread_started    # Assistant features
assistant_thread_context_changed
```

## Common Pitfalls and Solutions

### 1. Slack Table Formatting Issues
❌ **Problem**: Large markdown tables break Slack's block limit
✅ **Solution**: Use field layouts for small tables, truncate large ones
```python
# Check slack_formatter.py for table handling patterns
if len(headers) <= 3:
    # Use fields layout for compact tables
else:
    # Use structured text with truncation
```

### 2. Async/Await in Slack Handlers
❌ **Problem**: Mixing sync Slack handlers with async agent calls
✅ **Solution**: Use asyncio.run() for async calls in sync handlers
```python
returned_message = asyncio.run(
    process_with_agent(user_id, message, channel_id, thread_ts)
)
```

### 3. Memory Management
❌ **Problem**: Memory leaks from unclosed connections or large data
✅ **Solution**: Use context managers and proper resource cleanup
```python
with metrics.timer("operation"):
    # Automatically cleaned up
    result = expensive_operation()
```

### 4. Production Deployment
❌ **Problem**: Missing health checks, improper signal handling
✅ **Solution**: Use production main.py pattern with health monitoring
```python
# main.py includes:
# - Signal handlers for graceful shutdown
# - Health check setup
# - Metrics initialization
# - Proper async event loop management
```

## Development Workflow

### 1. Initial Setup
```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Configure Slack app credentials in .env
```

### 2. Testing Pattern
```bash
# Run style checks
python check_style.py

# Run tests
python run_tests.py

# Test specific functionality
python -m pytest tests/test_specific.py -v
```

### 3. Agent Integration
1. Add intent detection in `agno_integration.py`
2. Implement agent processing logic
3. Add response formatting
4. Update assistant.py to use new integration
5. Test with real Slack interactions

### 4. Production Deployment
1. Set production environment variables
2. Build and test Docker image
3. Deploy with docker-compose
4. Monitor health endpoint
5. Check application logs

## Monitoring and Debugging

### Health Check Endpoint
```bash
curl http://localhost:3001/health
```
Returns comprehensive health status including:
- Database connectivity
- API service status (OpenAI, Composio, etc.)
- Circuit breaker states
- Overall system health

### Log Analysis
Logs are structured JSON for easy parsing:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "assistant",
  "message": "Processing user request",
  "user_id": "U12345",
  "channel_id": "C67890"
}
```

### Metrics Collection
Built-in metrics for monitoring:
- `slack.requests` - Total Slack requests
- `assistant.messages.received` - Assistant messages
- `assistant.notion_requests` - Notion-specific requests
- Circuit breaker states and timings

## Security Best Practices

### 1. Input Validation
All user inputs are validated for:
- Length limits (default 4000 chars)
- Suspicious patterns (XSS, injection attempts)
- Proper Slack ID formats

### 2. Rate Limiting
Default: 60 requests per minute per user/channel combination
Configurable via `RATE_LIMIT_PER_MINUTE`

### 3. Access Control
Optional user/channel restrictions:
```bash
ALLOWED_USERS=U123,U456  # Only these users
ALLOWED_CHANNELS=C123,C456  # Only these channels
```

### 4. Signature Verification
All Slack requests are verified using signing secret to prevent tampering

## Performance Optimization

### 1. Circuit Breakers
Automatic failure detection and recovery for external APIs:
- OpenAI: 3 failures triggers 30s timeout
- Composio: 5 failures triggers 60s timeout
- Slack: 5 failures triggers 30s timeout

### 2. Retry Logic
Exponential backoff with jitter for API calls:
- API calls: 5 attempts with 2s base delay
- Database operations: 3 attempts with 0.5s base delay

### 3. Resource Management
- Memory limits in Docker deployment
- Connection pooling for external APIs
- Proper cleanup of resources

## Directory Standards for New Agents

When creating new Slack agents in this directory:

1. **Copy the production structure** from this agent
2. **Reuse utils/** - Don't recreate logging, errors, security, etc.
3. **Follow naming conventions**: `agent-name/` directory structure
4. **Use shared configuration patterns** from `config.py`
5. **Implement health checks** on port 3001
6. **Include deployment files**: Dockerfile, docker-compose.yml
7. **Document environment variables** in .env.example
8. **Add proper .gitignore** for the agent type

This ensures consistency and leverages all the production-ready patterns we've established.