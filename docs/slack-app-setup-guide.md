# Slack App Setup Guide

This guide walks you through setting up the Agno Slack app using the existing manifest.json file.

## Option 1: Using the Web UI with Manifest (Recommended)

1. **Go to Slack API Apps page**
   - Navigate to https://api.slack.com/apps
   - Click "Create New App"

2. **Choose "From an app manifest"**
   - Select your workspace
   - Copy and paste the contents of `notion-ai-assistant/manifest.json`
   - Click "Next" to review the configuration
   - Click "Create" to create the app

3. **Install the app to your workspace**
   - After creation, you'll be redirected to the app settings
   - Click "Install to Workspace"
   - Review and authorize the permissions

4. **Collect your credentials**
   - **Bot User OAuth Token**: Go to "OAuth & Permissions" → Copy the "Bot User OAuth Token" (starts with `xoxb-`)
   - **Signing Secret**: Go to "Basic Information" → "App Credentials" → Copy the "Signing Secret"
   - **App ID**: Go to "Basic Information" → Copy the "App ID"

5. **For Socket Mode (Development)**
   - Go to "Basic Information" → "App-Level Tokens"
   - Click "Generate Token and Scopes"
   - Add the `connections:write` scope
   - Name it something like "Socket Mode Token"
   - Copy the generated token (starts with `xapp-`)

## Option 2: Using Slack CLI (Interactive)

Since the CLI requires interactive input, run these commands from your terminal:

```bash
# Navigate to the project directory
cd notion-ai-assistant

# Create a new app from scratch (since manifest import might not be available)
slack create notion-ai-assistant

# Link your existing app (if you already created one via web)
slack app link

# Install the app to your workspace
slack app install

# Run the app locally in Socket Mode
slack run
```

## Option 3: Manual Creation via Web UI

If you can't use the manifest, create the app manually:

1. **Create New App**
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Name: "Agno Assistant" (or your preferred name)
   - Select your workspace

2. **Configure OAuth Scopes**
   - Go to "OAuth & Permissions"
   - Add these Bot Token Scopes:
     - `assistant:write`
     - `chat:write`
     - `channels:join`
     - `im:history`
     - `channels:history`
     - `groups:history`

3. **Enable Socket Mode (for development)**
   - Go to "Socket Mode"
   - Toggle "Enable Socket Mode" to On
   - Create an app-level token with `connections:write` scope

4. **Configure Event Subscriptions**
   - Go to "Event Subscriptions"
   - Toggle "Enable Events" to On
   - If using Socket Mode, you don't need a Request URL
   - Subscribe to these bot events:
     - `assistant_thread_started`
     - `assistant_thread_context_changed`
     - `message.im`

5. **Configure Slash Commands**
   - Go to "Slash Commands"
   - Create these commands:
     - `/ask` - Ask the AI assistant a question
     - `/kb-search` - Search the knowledge base
     - `/tasks` - Manage tasks

## Update Environment Configuration

After creating the app, update your `.env` file:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials:
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_ID=your-app-id
SLACK_APP_TOKEN=xapp-your-app-token  # Only for Socket Mode

# Other required variables
LITELLM_BASE_URL=https://your-litellm-proxy.domain.com
LITELLM_API_KEY=your-litellm-api-key
COMPOSIO_TOKEN=your-composio-token
```

## Test the Installation

1. **Verify credentials**:
   ```bash
   # Test the bot token
   curl -H "Authorization: Bearer xoxb-your-token" https://slack.com/api/auth.test
   ```

2. **Run the app locally**:
   ```bash
   cd notion-ai-assistant
   python app.py  # For Socket Mode
   # or
   python app_oauth.py  # For HTTP mode
   ```

3. **Test in Slack**:
   - Send a direct message to your bot
   - Try a slash command like `/ask What can you help me with?`

## Next Steps

Once the Slack app is configured:
1. Deploy the FastAPI agent service (`src/app/server.py`)
2. Update `API_BASE_URL` in your `.env` to point to the deployed agent
3. Test the complete integration flow: Slack → Bolt → Agno Agent → Notion

## Troubleshooting

- **Bot not responding**: Check that Socket Mode is connected (look for "⚡ Bolt app is running!" in logs)
- **Events not received**: Verify event subscriptions are properly configured
- **Authentication errors**: Double-check all tokens are correctly copied to `.env`
- **Slash commands not working**: Ensure commands are created with correct request URLs