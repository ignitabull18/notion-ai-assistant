"""
Tests for Slack AI Assistant functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from listeners.slack_assistant import SlackAssistant


class TestSlackAssistant:
    """Test cases for Slack Assistant"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.assistant = SlackAssistant()
        self.mock_say = Mock()
        self.mock_client = Mock()
        self.mock_context = Mock()
        self.mock_context.user_id = "U123456"
        self.mock_context.channel_id = "C123456"
        
    def test_extract_command(self):
        """Test command extraction from messages"""
        # Test basic commands
        assert self.assistant._extract_command("summarize") == "summarize"
        assert self.assistant._extract_command("remind me tomorrow") == "remind me tomorrow"
        assert self.assistant._extract_command("search deployment issues") == "search deployment issues"
        
        # Test with bot mentions
        assert self.assistant._extract_command("<@U1234> summarize") == "summarize"
        
        # Test unknown commands
        assert self.assistant._extract_command("hello there") is None
        
    def test_parse_timeframe(self):
        """Test timeframe parsing"""
        # Test today
        result = self.assistant._parse_timeframe("summarize today")
        assert result is not None
        assert "oldest_ts" in result
        
        # Test week
        result = self.assistant._parse_timeframe("summarize this week")
        assert result is not None
        
        # Test no timeframe
        result = self.assistant._parse_timeframe("summarize")
        assert result is None
        
    def test_parse_time_spec(self):
        """Test natural language time parsing"""
        # Test tomorrow at specific time
        result = self.assistant._parse_time_spec("tomorrow at 3pm")
        expected = datetime.now() + timedelta(days=1)
        expected = expected.replace(hour=15, minute=0, second=0, microsecond=0)
        assert result.date() == expected.date()
        assert result.hour == 15
        
        # Test AM time
        result = self.assistant._parse_time_spec("9am")
        assert result.hour == 9
        
    @patch('listeners.slack_assistant.ComposioToolSet')
    def test_handle_summarize(self, mock_composio):
        """Test channel summarization"""
        # Mock Composio response
        mock_entity = Mock()
        mock_entity.execute.return_value = {
            "messages": [
                {"text": "First message", "user": "U1", "ts": "1234567890.000000"},
                {"text": "Second message", "user": "U2", "ts": "1234567891.000000"}
            ]
        }
        mock_composio.return_value.get_entity.return_value = mock_entity
        mock_composio.return_value.get_action.return_value = Mock()
        
        # Mock LLM response
        with patch.object(self.assistant.llm, 'call', return_value="Summary: Team discussed project updates"):
            self.assistant._handle_summarize(
                "summarize today",
                "C123456",
                self.mock_say,
                self.mock_client
            )
            
        # Verify say was called with summary
        self.mock_say.assert_called()
        call_args = self.mock_say.call_args[0][0]
        assert "Channel Summary" in call_args
        assert "Team discussed project updates" in call_args
        
    @patch('listeners.slack_assistant.ComposioToolSet')
    def test_handle_reminder(self, mock_composio):
        """Test reminder creation"""
        # Mock Composio response
        mock_entity = Mock()
        mock_entity.execute.return_value = {"ok": True}
        mock_composio.return_value.get_entity.return_value = mock_entity
        mock_composio.return_value.get_action.return_value = Mock()
        
        self.assistant._handle_reminder(
            "remind me to review PRs tomorrow at 2pm",
            "U123456",
            "C123456",
            self.mock_say
        )
        
        # Verify reminder was created
        self.mock_say.assert_called()
        assert "Reminder set!" in self.mock_say.call_args[0][0]
        
    @patch('listeners.slack_assistant.ComposioToolSet')
    def test_handle_search(self, mock_composio):
        """Test message search"""
        # Mock Composio response
        mock_entity = Mock()
        mock_entity.execute.return_value = {
            "messages": {
                "matches": [
                    {
                        "text": "Found deployment issue",
                        "username": "user1",
                        "ts": "1234567890.000000"
                    }
                ]
            }
        }
        mock_composio.return_value.get_entity.return_value = mock_entity
        mock_composio.return_value.get_action.return_value = Mock()
        
        self.assistant._handle_search(
            "search deployment issues",
            self.mock_say
        )
        
        # Verify search results were formatted
        self.mock_say.assert_called()
        call_args = self.mock_say.call_args[0][0]
        assert "Search results" in call_args
        assert "deployment issue" in call_args
        
    def test_analyze_activity(self):
        """Test activity analysis"""
        messages = [
            {"user": "U1", "type": "message", "ts": "1234567890.000000"},
            {"user": "U1", "type": "message", "ts": "1234567891.000000"},
            {"user": "U2", "type": "message", "ts": "1234567892.000000"},
            {"user": "U2", "type": "thread_broadcast", "ts": "1234567893.000000"}
        ]
        
        analysis = self.assistant._analyze_activity(messages)
        
        assert analysis["total_messages"] == 4
        assert analysis["unique_users"] == 2
        assert analysis["message_types"]["message"] == 3
        assert analysis["message_types"]["thread_broadcast"] == 1
        assert "U1" in analysis["top_contributors"]
        assert "U2" in analysis["top_contributors"]
        
    def test_format_search_results(self):
        """Test search result formatting"""
        messages = [
            {
                "text": "This is a test message about deployment",
                "username": "testuser",
                "ts": "1234567890.000000"
            }
        ]
        
        formatted = self.assistant._format_search_results(messages, "deployment")
        
        assert "Search results for: *deployment*" in formatted
        assert "testuser" in formatted
        assert "test message" in formatted
        
    def test_process_slack_command_help(self):
        """Test help command processing"""
        body = {
            "user": {"id": "U123456"},
            "channel": {"id": "C123456"},
            "text": "help"
        }
        
        self.assistant.process_slack_command(
            body,
            self.mock_context,
            self.mock_say,
            self.mock_client
        )
        
        # Verify help message was sent
        self.mock_say.assert_called()
        help_text = self.mock_say.call_args[0][0]
        assert "summarize" in help_text
        assert "remind" in help_text
        assert "search" in help_text
        assert "schedule" in help_text
        assert "analyze" in help_text