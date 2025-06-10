# Scripts Directory

This directory contains utility scripts for development and validation.

## 📂 Structure

### checks/
Validation and checking scripts:
- `check_actions.py` - List available Composio/Notion actions
- `check_composio_api.py` - Test Composio API connectivity
- `check_composio_raw.py` - Raw Composio API testing
- `check_context_limits.py` - Test context window limits
- `check_style.py` - Python code style validation

### development/
Development helper scripts:
- `get_action_schemas.py` - Extract action parameter schemas
- `inspect_tools.py` - Inspect available tools
- `show_parameters.py` - Display tool parameters

## 🚀 Usage

```bash
# Check available Notion actions
python scripts/checks/check_actions.py

# Validate code style
python scripts/checks/check_style.py

# Get tool schemas for development
python scripts/development/get_action_schemas.py
```

## 📝 Adding New Scripts

1. Place validation scripts in `checks/`
2. Place development utilities in `development/`
3. Add clear docstrings and usage examples
4. Update this README with the new script