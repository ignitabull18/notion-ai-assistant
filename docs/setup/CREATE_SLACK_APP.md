# Creating Your Notion AI Assistant Slack App

Since the app doesn't exist yet, let's create it from scratch using the manifest.

## Method 1: Create via Slack API Website (Recommended)

1. **Go to Create New App**
   - Visit: https://api.slack.com/apps/new
   - Choose "From an app manifest"

2. **Select Your Workspace**
   - Choose "ignitabull" (Team ID: T01FAMQ2H0B)
   - Click "Next"

3. **Paste the Manifest**
   - Select the "JSON" tab
   - Copy the entire contents of `/Users/ignitabull/Desktop/agno/notion-ai-assistant/manifest.json`
   - Paste it into the text box
   - Click "Next"

4. **Review and Create**
   - Review the settings
   - Click "Create"

5. **Install to Workspace**
   - Click "Install to Workspace"
   - Click "Allow" on the permissions screen

6. **Get Your Tokens**
   
   **Bot Token:**
   - Go to "OAuth & Permissions" in the left sidebar
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)
   
   **App Token (for Socket Mode):**
   - Go to "Basic Information"
   - Scroll to "App-Level Tokens"
   - Click "Generate Token and Scopes"
   - Name: "socket-mode"
   - Add scope: `connections:write`
   - Click "Generate"
   - Copy the token (starts with `xapp-`)
   
   **Other Credentials:**
   - Stay on "Basic Information"
   - Copy "Signing Secret" from "App Credentials"
   - Copy "App ID" from the top

## Method 2: Create via Slack CLI

If you prefer using the CLI, run these commands in your terminal:

```bash
# Navigate to the app directory
cd /Users/ignitabull/Desktop/agno/notion-ai-assistant

# Create a new app
slack create notion-ai-assistant --template https://github.com/slack-samples/bolt-python-assistant-template

# Or if you want to use your existing manifest
slack app create --manifest manifest.json --team T01FAMQ2H0B
```

## Update Your Environment

Once you have all the credentials, create your `.env` file:

```bash
# In the notion-ai-assistant directory
cat > .env << EOF
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_APP_ID=your-app-id-here

# LiteLLM Configuration
LITELLM_BASE_URL=https://your-litellm-proxy.example.com
LITELLM_API_KEY=your-litellm-api-key
LITELLM_MODEL_ID=gpt-4o

# Composio for Notion
COMPOSIO_TOKEN=your-composio-token

# Optional: Qdrant for knowledge base
QDRANT_HOST=localhost
QDRANT_PORT=6333
EOF
```

## Test Your App

After setting up:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

You should see:
```
⚡️ Bolt app is running!
```

Then in Slack:
1. Find your bot in the Apps section
2. Send it a message: "Hello!"
3. Try a Notion command: "Can you create a new Notion page?"