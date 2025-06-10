# LiteLLM Proxy Configuration Guide

This document describes how the Agno assistant connects to the existing Coolify-hosted LiteLLM proxy.

## Overview

The Agno assistant uses a centralized LiteLLM proxy hosted on Coolify to access various LLM models. This proxy provides:

- Unified interface for multiple LLM providers
- HTTPS secure connection
- API key authentication
- Request routing to appropriate models
- Rate limiting and error handling

## Configuration

### Environment Variables

The following environment variables must be set in your `.env` file:

```env
# HTTPS URL of your LiteLLM proxy instance
LITELLM_BASE_URL=https://your-litellm-proxy.domain.com

# API key for authenticating with the proxy
LITELLM_API_KEY=your-api-key-here

# Optional: specify the model to use (defaults to gpt-4o)
LITELLM_MODEL_ID=gpt-4o
```

### Security Requirements

1. **HTTPS Only**: The proxy URL must use HTTPS for secure communication
2. **API Key**: All requests require a valid API key
3. **Environment Variables**: Never commit credentials to version control

## Testing the Connection

Use the provided test script to verify your configuration:

```bash
# Make sure you have created .env from .env.example
cp .env.example .env
# Edit .env with your actual values

# Run the connection test
python test_litellm_connection.py
```

The test script will:
1. Validate environment variables
2. Create a LiteLLM model instance
3. Send a test request to the proxy
4. Report success or failure

## Integration with Agno

The LiteLLM proxy is integrated into the Agno agent through the `llm_config.py` module:

```python
from agent.llm_config import create_litellm_model

# Create model instance
model = create_litellm_model()

# Use with Agno Agent
from agno import Agent

agent = Agent(
    model=model,
    tools=[...],
    # other configuration
)
```

## Troubleshooting

### Connection Errors

If you encounter connection errors:

1. Verify the proxy URL is correct and uses HTTPS
2. Check that your API key is valid
3. Ensure the proxy is running and accessible
4. Check network connectivity and firewall rules

### Authentication Errors

If authentication fails:

1. Verify your API key is correctly set in `.env`
2. Ensure the API key has not expired
3. Check with your administrator for key permissions

### Timeout Errors

If requests timeout:

1. Check the `REQUEST_TIMEOUT` environment variable (default: 30 seconds)
2. Verify the proxy is not overloaded
3. Consider implementing retry logic

## Model Configuration

The proxy supports routing to various models. Common options:

- `gpt-4o` - GPT-4 Optimized (default)
- `gpt-4` - GPT-4 Standard
- `gpt-3.5-turbo` - GPT-3.5 Turbo
- `claude-3-opus` - Claude 3 Opus
- `claude-3-sonnet` - Claude 3 Sonnet

Set the desired model using the `LITELLM_MODEL_ID` environment variable.

## Error Handling

The `llm_config.py` module includes:

- Automatic retries with exponential backoff
- Structured logging for debugging
- Graceful error handling
- Connection validation

## Production Considerations

1. **Rate Limiting**: Be aware of proxy rate limits
2. **Monitoring**: Use structured logs to monitor usage
3. **Failover**: Consider implementing fallback strategies
4. **Caching**: Cache responses where appropriate
5. **Security**: Rotate API keys regularly

## Support

For issues with the LiteLLM proxy itself, contact your infrastructure team or check the Coolify deployment logs.