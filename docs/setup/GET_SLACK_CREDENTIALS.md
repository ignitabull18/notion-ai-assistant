# How to Get Your Slack App Credentials

Since your Slack app is configured with a remote manifest, you'll need to get the credentials from the Slack App Management page.

## Steps to Get Your Credentials:

1. **Go to Slack App Management**
   - Visit: https://api.slack.com/apps
   - Sign in to your workspace (ignitabull - Team ID: T01FAMQ2H0B)

2. **Find Your App**
   - Look for "notion-ai-assistant" in your apps list
   - Click on the app name to open its configuration

3. **Get Bot Token (SLACK_BOT_TOKEN)**
   - Go to "OAuth & Permissions" in the left sidebar
   - Find "Bot User OAuth Token" (starts with `xoxb-`)
   - Copy this token

4. **Get App Token (SLACK_APP_TOKEN)**
   - Go to "Basic Information" in the left sidebar
   - Scroll to "App-Level Tokens" section
   - If no token exists:
     - Click "Generate Token and Scopes"
     - Name it (e.g., "socket-mode")
     - Add scope: `connections:write`
     - Click "Generate"
   - Copy the token (starts with `xapp-`)

5. **Get Signing Secret (SLACK_SIGNING_SECRET)**
   - Stay on "Basic Information" page
   - Find "Signing Secret" in the "App Credentials" section
   - Click "Show" and copy the secret

6. **Get App ID (SLACK_APP_ID)**
   - Stay on "Basic Information" page
   - Find "App ID" at the top (starts with `A`)
   - Copy this ID

## Alternative: Using Slack CLI

If you prefer to use the Slack CLI, you can run these commands in your terminal:

```bash
# Navigate to the app directory
cd /Users/ignitabull/Desktop/agno/notion-ai-assistant

# Link your existing app (interactive)
slack app link

# After linking, you can get the credentials
slack app credentials
```

## Update Your .env File

Once you have all the credentials, create a `.env` file in the project root:

```bash
# Create .env from example
cp /Users/ignitabull/Desktop/agno/.env.example /Users/ignitabull/Desktop/agno/.env

# Edit the file and add your credentials
```

Your `.env` should include:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
SLACK_APP_ID=your-app-id-here
```

## Verify Socket Mode is Enabled

In the Slack App Management page:
1. Go to "Socket Mode" in the left sidebar
2. Make sure it's toggled ON
3. This is required for the app to work with the app token