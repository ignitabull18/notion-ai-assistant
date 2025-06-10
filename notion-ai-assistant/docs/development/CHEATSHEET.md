# Slack Agent Development Cheat Sheet

## 🚀 Quick Start New Agent

```bash
# 1. Copy structure from existing agent
cp -r notion-ai-assistant/ new-agent/
cd new-agent/

# 2. Update configuration
cp .env.example .env
# Edit .env with your Slack app credentials

# 3. Install and test
pip install -r requirements.txt
python main.py

# 4. Health check
curl http://localhost:3001/health
```

## 📋 Essential Code Patterns

### Basic Assistant Handler
```python
@assistant.user_message
def respond_in_assistant_thread(payload, context, say):
    try:
        with metrics.timer("assistant.user_message"):
            metrics.increment("assistant.messages.received")
            
            user_message = payload["text"]
            
            if detect_your_intent(user_message):
                response = await process_with_your_agent(
                    user_id=context.user_id,
                    message=user_message,
                    channel_id=context.channel_id
                )
                formatted = format_your_response(response)
                say(blocks=formatted['blocks'])
            else:
                # Fallback to LLM
                pass
                
            metrics.increment("assistant.messages.success")
            
    except Exception as e:
        metrics.increment("assistant.messages.error")
        app_error = error_handler.handle_error(e, user_id=context.user_id)
        say(f"❌ {app_error.user_message}")
```

### External API Call Pattern
```python
from utils.retry import api_retry, with_circuit_breaker

@api_retry.retry
@with_circuit_breaker("your_service")
def call_external_api(data):
    try:
        response = your_api_client.post("/endpoint", json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise YourAPIError(f"API call failed: {e}")
```

### Configuration Access
```python
from config import get_config

config = get_config()
api_key = config.your_service.api_key
model = config.your_service.model
debug = config.debug
```

### Logging with Context
```python
from utils.errors import error_handler

logger = error_handler.logger
logger.info(
    "Operation completed",
    extra={
        "user_id": user_id,
        "operation": "your_operation",
        "duration_ms": 150,
        "result": "success"
    }
)
```

## 🔧 Environment Variables Template

```bash
# .env file template
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug

# Slack (ALWAYS REQUIRED)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# Your Integration
YOUR_SERVICE_API_KEY=your-key
YOUR_SERVICE_MODEL=your-model

# Security
RATE_LIMIT_PER_MINUTE=60
MAX_MESSAGE_LENGTH=4000
```

## 🏗️ Project Structure Checklist

```
your-agent/
├── ✅ main.py                     # Production entry point
├── ✅ config.py                   # Add your service config
├── ✅ listeners/
│   ├── ✅ __init__.py            # Production app factory
│   ├── ✅ assistant.py           # Update with your logic
│   └── ✅ your_integration.py     # Your specific integration
├── ✅ utils/                     # REUSE - don't modify
├── ✅ Dockerfile                 # Update if needed
├── ✅ docker-compose.yml         # Update service name
├── ✅ .env.example              # Update with your vars
├── ✅ requirements.txt          # Add your dependencies
└── ✅ tests/                    # Add your tests
```

## 🧪 Testing Quick Commands

```bash
# Style and type checking
python check_style.py

# Run all tests
python run_tests.py

# Run specific test
python -m pytest tests/test_your_feature.py -v

# Test with coverage
python -m pytest --cov=listeners --cov=utils
```

## 🐳 Docker Quick Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f your-agent

# Shell into container
docker-compose exec your-agent bash

# Stop and cleanup
docker-compose down -v
```

## 🔍 Debugging Quick Checks

### Health Check Not Passing?
```bash
# Check endpoint
curl http://localhost:3001/health

# Check logs
docker-compose logs your-agent | grep ERROR

# Test individual components
python -c "from config import get_config; print(get_config())"
```

### Slack Not Responding?
```bash
# Verify tokens in .env
grep SLACK_ .env

# Check bot scopes in Slack app settings
# Required: app_mentions:read, channels:history, chat:write, assistant:write

# Test socket connection
python -c "
from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import get_config
config = get_config()
print(f'App token: {config.slack.app_token[:10]}...')
"
```

### Integration Not Working?
```bash
# Test API credentials
python -c "
from config import get_config
config = get_config()
print(f'Your API key: {config.your_service.api_key[:10]}...')
"

# Check circuit breaker status
curl http://localhost:3001/health | jq '.checks'
```

## 📊 Monitoring Quick Checks

### View Metrics
```bash
# Health status
curl -s http://localhost:3001/health | jq '.'

# Check logs for metrics
docker-compose logs your-agent | grep '"metrics"'
```

### Performance Issues
```bash
# Check response times
docker-compose logs your-agent | grep 'duration_ms'

# Monitor circuit breaker status
curl -s http://localhost:3001/health | jq '.checks'
```

## 🔒 Security Checklist

- [ ] All user inputs validated via SecurityMiddleware
- [ ] Rate limiting configured (default 60/min)
- [ ] No secrets in code or logs
- [ ] Slack signature verification enabled
- [ ] Input length limits enforced
- [ ] SQL injection patterns blocked

## 🚨 Common Mistakes to Avoid

### ❌ Don't Do This
```python
# Raw API call without error handling
response = api_client.call()

# Hardcoded credentials
api_key = "sk-1234567890"

# Print debugging in production
print(f"API response: {response}")

# Raw user input processing
result = process(payload["text"])

# Sync/async mixing
result = async_function()  # In sync handler
```

### ✅ Do This Instead
```python
# Proper API call with retry and circuit breaker
@api_retry.retry
@with_circuit_breaker("service")
def call_api():
    return api_client.call()

# Configuration-based credentials
api_key = config.service.api_key

# Structured logging
logger.info("API call completed", extra={"status": "success"})

# Validated input processing
validated = security.validate_request(user_id, channel_id, message)
result = process(validated["message"])

# Proper async handling
result = asyncio.run(async_function())
```

## 🎯 Production Deployment Checklist

- [ ] Health checks passing on port 3001
- [ ] All environment variables configured
- [ ] Docker image builds successfully
- [ ] Security middleware enabled
- [ ] Metrics collection working
- [ ] Error handling tested
- [ ] Circuit breakers configured
- [ ] Logging structured and parseable

## 📞 When You Need Help

1. **Configuration Issues**: Check config.py and .env.example
2. **Slack Integration**: Verify OAuth scopes and event subscriptions
3. **Error Handling**: Follow patterns in utils/errors.py
4. **Performance**: Check circuit breaker status and metrics
5. **Security**: Review SecurityMiddleware configuration
6. **Deployment**: Use docker-compose for local testing first

Remember: When in doubt, copy from working patterns in this directory!