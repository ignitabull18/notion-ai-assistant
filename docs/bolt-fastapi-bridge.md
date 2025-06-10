# Bolt-FastAPI Bridge Documentation

This document describes the HTTP bridge between the Slack Bolt app and the FastAPI/Agno agent.

## Architecture

```
┌─────────────────┐      HTTP POST       ┌──────────────────┐
│   Bolt App      │ ─────────────────────▶│  FastAPI Agent   │
│                 │   /agent/ask          │                  │
│ slash commands  │◀───────────────────── │  Agno reasoning  │
└─────────────────┘      JSON response    └──────────────────┘
```

## Environment Variables

### Bolt App (notion-ai-assistant/)

```bash
# URL of the FastAPI agent service
API_BASE_URL=http://localhost:8000

# Optional: API key for authenticating with the agent endpoint
# If not set, the endpoint is open (suitable for internal networks)
AGNO_API_KEY=your-secure-api-key

# Slack credentials (existing)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret

# LiteLLM proxy (for direct LLM calls in Bolt)
LITELLM_BASE_URL=https://your-litellm-proxy.domain.com
LITELLM_API_KEY=your-litellm-key
```

### FastAPI Agent (src/)

```bash
# Optional: API key to secure the /agent/ask endpoint
# Must match AGNO_API_KEY in Bolt app
AGNO_API_KEY=your-secure-api-key

# Existing Slack credentials for direct operations
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret

# LiteLLM proxy
LITELLM_BASE_URL=https://your-litellm-proxy.domain.com
LITELLM_API_KEY=your-litellm-key

# Other existing configs...
COMPOSIO_TOKEN=your-composio-token
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## API Endpoint

### POST /agent/ask

Request complex reasoning from the Agno agent.

**Request:**
```json
{
  "user_id": "U123456",
  "text": "Create a Notion page for project planning",
  "channel": "C789012",
  "session_id": "optional-custom-session-id"
}
```

**Headers (if AGNO_API_KEY is set):**
```
Authorization: Bearer your-secure-api-key
```

**Response:**
```json
{
  "response": "I've created a new Notion page titled 'Project Planning'...",
  "session_id": "slack-U123456"
}
```

## Slash Commands

The bridge supports three slash commands:

### /ask
General purpose command for complex queries.
```
/ask How do I create a weekly report template in Notion?
```

### /kb-search
Search the knowledge base (Qdrant).
```
/kb-search Notion API pagination
```

### /tasks
Interact with task management.
```
/tasks list
/tasks create Write documentation
/tasks update 5 in-progress
```

## Error Handling

The bridge handles several error scenarios:

1. **Timeout (30s)**: Returns user-friendly timeout message
2. **HTTP errors**: Reports status code to user
3. **Network errors**: Generic error message with retry suggestion
4. **Authentication failure**: 401 if API key is invalid

## Deployment Scenarios

### Local Development
```bash
# Terminal 1: Start FastAPI
cd agno/
uvicorn src.app.server:app --reload

# Terminal 2: Start Bolt app
cd notion-ai-assistant/
slack run
```

### Production with Docker
```bash
# FastAPI in Docker
docker-compose up -d

# Bolt app on separate host
API_BASE_URL=https://agent.yourdomain.com slack run
```

### Kubernetes
```yaml
# Set API_BASE_URL to service DNS
API_BASE_URL=http://agno-agent-service.default.svc.cluster.local:8000
```

## Security Considerations

1. **API Key**: Always use AGNO_API_KEY in production to prevent unauthorized access
2. **HTTPS**: Use HTTPS for API_BASE_URL in production
3. **Network**: Ideally, keep the agent service on an internal network
4. **Rate Limiting**: Consider adding rate limiting to prevent abuse

## Monitoring

Monitor these metrics:
- Response times from /agent/ask
- Error rates by type
- Session creation frequency
- Timeout occurrences

## Testing the Bridge

```bash
# Test with curl
curl -X POST http://localhost:8000/agent/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "user_id": "test-user",
    "text": "Hello, agent!",
    "channel": "test-channel"
  }'
```