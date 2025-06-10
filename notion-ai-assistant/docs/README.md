# Notion AI Assistant Documentation

Welcome to the Notion AI Assistant documentation. This directory contains comprehensive guides for users, developers, and operators.

## 📚 Documentation Structure

### User Documentation
- **[ONBOARDING_GUIDE.md](ONBOARDING_GUIDE.md)** - Step-by-step guide for new users to get started
- **[ASSISTANT_PROFILE.md](ASSISTANT_PROFILE.md)** - Complete profile and capabilities of the Notion AI Assistant
- **[APP_LISTING.md](APP_LISTING.md)** - Official app listing description for the Slack App Directory

### Development Documentation
- **[development/CLAUDE.md](development/CLAUDE.md)** - Comprehensive development guide with lessons learned and best practices
- **[development/WORKFLOW.md](development/WORKFLOW.md)** - Step-by-step workflow for creating new Slack agents
- **[development/CHEATSHEET.md](development/CHEATSHEET.md)** - Quick reference for common patterns and commands

### Technical Notes
- **[CLAUDE.md](CLAUDE.md)** - Original technical notes about this specific Notion integration

## 🗂️ Documentation Organization

### This Directory (`/notion-ai-assistant/docs/`)
**Purpose**: Agent-specific documentation
- User guides and onboarding
- Feature documentation
- Marketing materials
- Development guides for creating similar agents

### Parent Directory (`/agno/docs/`)
**Purpose**: General Slack app development resources
- Slack app setup guides
- Architecture documentation
- Platform-specific guides (LiteLLM, Bolt, etc.)

### Root Directory (`/notion-ai-assistant/`)
**Purpose**: Configuration and deployment
- `.cursorrules` - Development standards enforcement
- `DEPLOYMENT.md` - Production deployment guide
- Configuration files (Dockerfile, docker-compose.yml)

## 🚀 Quick Links

### For Users
- [Getting Started](ONBOARDING_GUIDE.md)
- [Features & Capabilities](ASSISTANT_PROFILE.md)

### For Developers
- [Development Guide](development/CLAUDE.md)
- [Creating New Agents](development/WORKFLOW.md)
- [Quick Reference](development/CHEATSHEET.md)
- [Development Standards](../.cursorrules)

### For Operators
- [Deployment Guide](../DEPLOYMENT.md)
- [Production Configuration](../config.py)

## 📝 Documentation Standards

1. **Use clear headings** with emoji icons
2. **Include examples** for all features
3. **Keep language simple** and accessible
4. **Update regularly** with new features

## 🔄 Maintenance

- Review user guides monthly
- Update technical docs with each feature
- Keep marketing content current
- Archive outdated documentation

## 📋 Creating New Documentation

1. Use markdown format
2. Follow existing document structure
3. Include table of contents for long docs
4. Add to this README when created
5. Place in appropriate subdirectory:
   - User-facing → root of docs/
   - Development → docs/development/
   - Deployment → project root