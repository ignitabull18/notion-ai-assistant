# Deployment Guide

This guide covers deploying the Notion AI Assistant to production environments.

## Prerequisites

- Docker and Docker Compose
- Environment variables configured
- Slack app set up with proper OAuth scopes
- OpenAI API key
- Composio account with Notion integration

## Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure all required environment variables:
   ```bash
   # Required Slack credentials
   SLACK_BOT_TOKEN=xoxb-your-bot-token
   SLACK_APP_TOKEN=xapp-your-app-token  
   SLACK_SIGNING_SECRET=your-signing-secret
   
   # Required OpenAI credentials
   OPENAI_API_KEY=sk-your-openai-key
   
   # Required Composio credentials
   COMPOSIO_API_KEY=your-composio-key
   ```

## Docker Deployment

### Quick Start with Docker Compose

1. Build and start the application:
   ```bash
   docker-compose up -d
   ```

2. Check application health:
   ```bash
   curl http://localhost:3001/health
   ```

3. Monitor logs:
   ```bash
   docker-compose logs -f notion-ai-assistant
   ```

### Manual Docker Deployment

1. Build the image:
   ```bash
   docker build -t notion-ai-assistant .
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name notion-ai-assistant \
     --env-file .env \
     -p 3000:3000 \
     -p 3001:3001 \
     -v notion_data:/app/data \
     notion-ai-assistant
   ```

## Production Considerations

### Security

- **Environment Variables**: Never commit `.env` files to version control
- **Network Security**: Run behind a reverse proxy (nginx, Cloudflare)
- **User Access**: Configure `ALLOWED_USERS` and `ALLOWED_CHANNELS` for access control
- **Rate Limiting**: Adjust `RATE_LIMIT_PER_MINUTE` based on usage patterns

### Monitoring

- **Health Checks**: Monitor `/health` endpoint (port 3001)
- **Application Logs**: Located in `/app/logs` inside container
- **Metrics**: Built-in metrics collection for monitoring integrations
- **Alerts**: Set up alerts for application errors and health check failures

### Scaling

- **Resource Limits**: Configure CPU/memory limits in docker-compose.yml
- **Database**: SQLite is suitable for single-instance deployments
- **Load Balancing**: For multiple instances, use external load balancer

### Backup

- **Database**: Regular backups of `/app/data/production.db`
- **Configuration**: Backup environment variables securely
- **Logs**: Implement log rotation and archival

## Cloud Provider Deployment

### AWS ECS

1. Create task definition with container configuration
2. Set up Application Load Balancer for health checks
3. Configure CloudWatch for logging and monitoring
4. Use AWS Secrets Manager for sensitive environment variables

### Google Cloud Run

1. Build and push image to Google Container Registry
2. Deploy with Cloud Run service
3. Configure environment variables in service settings
4. Set up Cloud Monitoring for health checks

### Azure Container Instances

1. Push image to Azure Container Registry
2. Create container group with health probe configuration
3. Use Azure Key Vault for secrets management
4. Configure Azure Monitor for logging

## Kubernetes Deployment

Example Kubernetes manifests:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notion-ai-assistant
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notion-ai-assistant
  template:
    metadata:
      labels:
        app: notion-ai-assistant
    spec:
      containers:
      - name: app
        image: notion-ai-assistant:latest
        ports:
        - containerPort: 3000
        - containerPort: 3001
        env:
        - name: ENVIRONMENT
          value: "production"
        envFrom:
        - secretRef:
            name: notion-ai-assistant-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
```

## Troubleshooting

### Common Issues

1. **Health Check Failures**
   - Check if all required environment variables are set
   - Verify Slack/OpenAI/Composio API connectivity
   - Review application logs for specific errors

2. **Slack Connection Issues**
   - Verify bot token has correct scopes
   - Check signing secret matches Slack app configuration
   - Ensure app token is for Socket Mode (starts with `xapp-`)

3. **Memory Issues**
   - Monitor memory usage in production
   - Adjust Docker memory limits if needed
   - Check for memory leaks in application logs

4. **Performance Issues**
   - Monitor response times in metrics
   - Check rate limiting configuration
   - Review circuit breaker status

### Log Analysis

Application logs are structured JSON format:
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

Key log patterns to monitor:
- `CRITICAL` or `ERROR` level messages
- Circuit breaker state changes
- Rate limit violations
- API failures

## Maintenance

### Updates

1. Build new image with updated code
2. Test in staging environment
3. Deploy with rolling update strategy
4. Monitor health checks and logs

### Database Maintenance

- Regular SQLite database cleanup
- Backup before updates
- Monitor database size and performance

### Security Updates

- Regularly update base Docker image
- Keep Python dependencies updated
- Monitor security advisories for used packages