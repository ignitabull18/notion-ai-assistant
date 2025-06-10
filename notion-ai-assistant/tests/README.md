# Tests Directory

Comprehensive test suite for the Notion AI Assistant.

## 📂 Structure

### unit/
Unit tests for individual components:
- `test_slack_formatter_standalone.py` - Test Slack formatting functions
- `test_slack_formatting.py` - Test Block Kit formatting

### integration/
Integration tests for full workflows:
- `test_enhanced_context.py` - Test enhanced context window
- `test_enhanced_prompt.py` - Test system prompt enhancements
- `test_fix.py` - Test error fixes and recovery
- `test_memory.py` - Test long-term memory functionality
- `test_notion_tools.py` - Test Notion tool availability
- `test_simple_notion.py` - Test Notion operations without Slack

### Root level
- `test_all_notion_actions.py` - Comprehensive Notion action tests
- `test_composio.py` - Composio integration tests

## 🧪 Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test file
python tests/integration/test_simple_notion.py

# Run unit tests only
python -m pytest tests/unit/

# Run integration tests only
python -m pytest tests/integration/
```

## ✅ Test Coverage

- **Slack Formatting**: Full Block Kit conversion
- **Notion Tools**: All 16 available actions
- **Memory**: Persistence and retrieval
- **Context**: Large context window handling
- **Error Handling**: Validation and recovery

## 📝 Writing New Tests

1. **Unit tests**: Test single functions/classes
2. **Integration tests**: Test complete workflows
3. Use descriptive test names
4. Include setup and teardown
5. Test both success and failure cases