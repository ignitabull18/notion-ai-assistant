# Contributing to Notion AI Assistant

## Code Style and Naming Conventions

### File Naming
- **Python files**: Use `snake_case.py` (e.g., `agno_integration.py`)
- **Test files**: Prefix with `test_` (e.g., `test_composio.py`)
- **Documentation**: Use UPPERCASE for standard files (e.g., `README.md`, `LICENSE`)
- **Config files**: Use lowercase with appropriate extension (e.g., `requirements.txt`, `manifest.json`)

### Folder Naming
- Use lowercase, no spaces (e.g., `listeners`, `tests`, `events`)
- Use underscores for multi-word folders if needed

### Python Code Conventions
- **Classes**: Use `PascalCase` (e.g., `ComposioToolSet`)
- **Functions**: Use `snake_case` (e.g., `process_with_agent`)
- **Constants**: Use `UPPER_SNAKE_CASE` (e.g., `SLACK_BOT_TOKEN`)
- **Variables**: Use `snake_case` (e.g., `user_message`)

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Alphabetical order within each group

Example:
```python
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt import App

from listeners import register_listeners
```

### Project Structure
```
notion-ai-assistant/
├── main.py                 # Entry point (always lowercase)
├── run_tests.py           # Scripts use snake_case
├── listeners/             # Feature modules
│   ├── __init__.py
│   └── module_name.py     # snake_case for modules
├── tests/                 # Test directory
│   ├── test_*.py         # Test files prefixed with test_
│   └── check_*.py        # Utility scripts
├── data/                  # Data storage (gitignored)
├── CONTRIBUTING.md        # Documentation in UPPERCASE
├── README.md
├── LICENSE
└── requirements.txt       # Config files lowercase
```

### Git Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests liberally

### Environment Variables
- Always use UPPER_SNAKE_CASE
- Prefix with service name when appropriate (e.g., `SLACK_BOT_TOKEN`, `COMPOSIO_TOKEN`)
- Document all required variables in README.md

### Testing
- Write tests for new features
- Test file names should mirror source files (e.g., `agno_integration.py` → `test_agno_integration.py`)
- Use descriptive test function names starting with `test_`

### Documentation
- Update README.md for user-facing changes
- Use docstrings for all public functions and classes
- Keep documentation close to code

## Pull Request Process

1. Ensure all tests pass: `python run_tests.py`
2. Update documentation if needed
3. Follow the naming conventions above
4. Request review from maintainers

## Questions?

Feel free to open an issue for clarification on any conventions!