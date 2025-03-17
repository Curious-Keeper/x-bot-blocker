import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from x_bot_blocker.slack_reporting import SlackReporter

@pytest.fixture
def slack_reporter():
    return SlackReporter("https://test-webhook.slack.com")

@pytest.fixture
def daily_stats():
    return {
        'total_blocks': 5,
        'false_positives': 0,
        'accuracy': 100.0,
        'api_calls': 10,
        'errors': ["Test error 1", "Test error 2"]
    }

@pytest.fixture
def weekly_stats():
    return {
        'total_blocks': 25,
        'false_positives': 1,
        'avg_accuracy': 96.0,
        'total_api_calls': 50,
        'top_issues': ["Weekly issue 1", "Weekly issue 2"]
    }

def test_send_daily_report(slack_reporter, daily_stats):
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        slack_reporter.send_daily_report(daily_stats)
        
        # Verify the request was made with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['url'] == "https://test-webhook.slack.com"
        
        # Verify message structure
        message = call_args['json']
        assert 'blocks' in message
        blocks = message['blocks']
        
        # Check header
        assert blocks[0]['type'] == 'header'
        assert 'X Bot Blocker Daily Report' in blocks[0]['text']['text']
        
        # Check stats
        stats_text = str(blocks[1:3])
        assert '5' in stats_text  # total_blocks
        assert '0' in stats_text  # false_positives
        assert '100.0' in stats_text  # accuracy
        assert '10' in stats_text  # api_calls
        
        # Check errors
        assert 'Test error 1' in str(blocks[-1])
        assert 'Test error 2' in str(blocks[-1])

def test_send_weekly_report(slack_reporter, weekly_stats):
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        slack_reporter.send_weekly_report(weekly_stats)
        
        # Verify the request was made with correct data
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['url'] == "https://test-webhook.slack.com"
        
        # Verify message structure
        message = call_args['json']
        assert 'blocks' in message
        blocks = message['blocks']
        
        # Check header
        assert blocks[0]['type'] == 'header'
        assert 'X Bot Blocker Weekly Summary' in blocks[0]['text']['text']
        
        # Check stats
        stats_text = str(blocks[2:4])
        assert '25' in stats_text  # total_blocks
        assert '1' in stats_text  # false_positives
        assert '96.0' in stats_text  # avg_accuracy
        assert '50' in stats_text  # total_api_calls
        
        # Check issues
        assert 'Weekly issue 1' in str(blocks[-1])
        assert 'Weekly issue 2' in str(blocks[-1])

def test_send_message_error(slack_reporter):
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Test error")
        
        # Should not raise exception, just log error
        slack_reporter._send_message({"test": "message"})
        
        # Verify error was logged
        assert "Failed to send message to Slack" in str(slack_reporter.logger.error.call_args)

def test_empty_webhook_url(slack_reporter):
    slack_reporter.webhook_url = None
    slack_reporter.send_daily_report({})
    assert "Slack webhook URL not configured" in str(slack_reporter.logger.error.call_args) 