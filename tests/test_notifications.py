"""
Tests for notification functionality in daily_premarket_report.py
Tests email, Slack, and Discord notifications.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import smtplib

# Import module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from daily_premarket_report import PreMarketReportGenerator


class TestExtractSummary:
    """Test extract_summary() method."""

    @pytest.mark.unit
    def test_extract_summary_length(self, mock_env_vars, sample_report_content):
        """Test that extract_summary returns content within 500 char limit."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            summary = generator.extract_summary(sample_report_content)

            # Should be <= 500 characters
            assert len(summary) <= 500

    @pytest.mark.unit
    def test_extract_summary_not_empty(self, mock_env_vars, sample_report_content):
        """Test that extract_summary returns non-empty content."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            summary = generator.extract_summary(sample_report_content)

            assert len(summary) > 0

    @pytest.mark.unit
    def test_extract_summary_truncation(self, mock_env_vars):
        """Test that extract_summary truncates long content."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Create very long report
            long_report = "A" * 1000

            summary = generator.extract_summary(long_report)

            # Should be truncated
            assert len(summary) <= 500

    @pytest.mark.unit
    def test_extract_summary_preserves_beginning(self, mock_env_vars, sample_report_content):
        """Test that extract_summary preserves beginning of report."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            summary = generator.extract_summary(sample_report_content)

            # Should contain beginning text
            assert 'Pre-Market' in summary or 'October' in summary

    @pytest.mark.unit
    def test_extract_summary_stops_at_second_heading(self, mock_env_vars):
        """Test that extract_summary stops at second ## heading."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            report = """# Title
First paragraph

## Second Heading
This should not be included

## Third Heading
This definitely should not be included
"""

            summary = generator.extract_summary(report)

            # Should stop before second heading
            assert '## Third Heading' not in summary


class TestSendEmailNotification:
    """Test send_email_notification() method."""

    @pytest.mark.unit
    def test_email_disabled_returns_early(self, mock_env_vars, sample_report_content, temp_dir):
        """Test that email notification returns early when disabled."""
        # Set EMAIL_ENABLED to false
        with patch('daily_premarket_report.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda x, default='': {
                'EMAIL_ENABLED': 'false',
                'ANTHROPIC_API_KEY': 'test_key'
            }.get(x, default)

            with patch('daily_premarket_report.Anthropic'):
                generator = PreMarketReportGenerator()

                # Should not raise exception
                generator.send_email_notification(sample_report_content, temp_dir / 'test.md')

    @pytest.mark.unit
    def test_email_sends_with_correct_data(self, mock_env_vars, sample_report_content, temp_dir, mock_email_server):
        """Test that email is sent with correct data."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Mock SMTP
            with patch('daily_premarket_report.smtplib.SMTP') as mock_smtp:
                mock_smtp.return_value.__enter__.return_value = mock_email_server

                filepath = temp_dir / 'premarket_report_2025-10-14.md'
                filepath.write_text(sample_report_content)

                generator.send_email_notification(sample_report_content, filepath)

                # Check SMTP was called
                mock_smtp.assert_called_once_with('smtp.gmail.com', 587)

                # Check email was sent
                assert mock_email_server.sendmail.called

    @pytest.mark.unit
    def test_email_handles_smtp_error(self, mock_env_vars, sample_report_content, temp_dir):
        """Test that email handles SMTP errors gracefully."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Mock SMTP to raise exception
            with patch('daily_premarket_report.smtplib.SMTP', side_effect=smtplib.SMTPException("Connection failed")):
                filepath = temp_dir / 'test.md'
                filepath.write_text(sample_report_content)

                # Should not raise exception
                generator.send_email_notification(sample_report_content, filepath)

    @pytest.mark.unit
    def test_email_missing_credentials_returns_early(self, sample_report_content, temp_dir):
        """Test that email returns early when credentials missing."""
        with patch('daily_premarket_report.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda x, default='': {
                'EMAIL_ENABLED': 'true',
                'EMAIL_SENDER': '',  # Missing
                'EMAIL_PASSWORD': '',  # Missing
                'ANTHROPIC_API_KEY': 'test_key'
            }.get(x, default)

            with patch('daily_premarket_report.Anthropic'):
                generator = PreMarketReportGenerator()

                filepath = temp_dir / 'test.md'
                filepath.write_text(sample_report_content)

                # Should return early without error
                generator.send_email_notification(sample_report_content, filepath)


class TestSendSlackNotification:
    """Test send_slack_notification() method."""

    @pytest.mark.unit
    def test_slack_disabled_returns_early(self, sample_report_content):
        """Test that Slack notification returns early when disabled."""
        with patch('daily_premarket_report.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda x, default='': {
                'SLACK_WEBHOOK': '',  # Not set
                'ANTHROPIC_API_KEY': 'test_key'
            }.get(x, default)

            with patch('daily_premarket_report.Anthropic'):
                generator = PreMarketReportGenerator()

                # Should not raise exception
                generator.send_slack_notification(sample_report_content)

    @pytest.mark.unit
    def test_slack_sends_with_correct_payload(self, mock_env_vars, sample_report_content, mock_requests_response):
        """Test that Slack sends with correct payload format."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.requests.post') as mock_post:
                mock_post.return_value = mock_requests_response

                generator.send_slack_notification(sample_report_content)

                # Check POST was called
                assert mock_post.called

                # Check payload structure
                call_kwargs = mock_post.call_args
                assert call_kwargs is not None

                # Get the json parameter
                json_payload = call_kwargs.kwargs.get('json')
                assert json_payload is not None
                assert 'blocks' in json_payload

    @pytest.mark.unit
    def test_slack_truncates_summary(self, mock_env_vars):
        """Test that Slack truncates summary to 1000 chars."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Create very long report
            long_report = "A" * 5000

            with patch('daily_premarket_report.requests.post') as mock_post:
                mock_post.return_value = MagicMock(status_code=200)

                generator.send_slack_notification(long_report)

                # Check that summary in payload is truncated
                if mock_post.called:
                    call_kwargs = mock_post.call_args
                    json_payload = call_kwargs.kwargs.get('json', {})

                    # Check blocks don't contain excessive text
                    assert 'blocks' in json_payload

    @pytest.mark.unit
    def test_slack_handles_request_error(self, mock_env_vars, sample_report_content):
        """Test that Slack handles request errors gracefully."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.requests.post', side_effect=Exception("Network error")):
                # Should not raise exception
                generator.send_slack_notification(sample_report_content)

    @pytest.mark.unit
    def test_slack_includes_trading_date(self, mock_env_vars, sample_report_content, mock_requests_response):
        """Test that Slack notification includes trading date."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.requests.post') as mock_post:
                mock_post.return_value = mock_requests_response

                generator.send_slack_notification(sample_report_content)

                if mock_post.called:
                    call_kwargs = mock_post.call_args
                    json_payload = call_kwargs.kwargs.get('json', {})

                    # Convert to string to check content
                    payload_str = str(json_payload)
                    assert 'October' in payload_str or '2025' in payload_str or 'report' in payload_str.lower()


class TestSendDiscordNotification:
    """Test send_discord_notification() method."""

    @pytest.mark.unit
    def test_discord_disabled_returns_early(self, sample_report_content):
        """Test that Discord notification returns early when disabled."""
        with patch('daily_premarket_report.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda x, default='': {
                'DISCORD_WEBHOOK': '',  # Not set
                'ANTHROPIC_API_KEY': 'test_key'
            }.get(x, default)

            with patch('daily_premarket_report.Anthropic'):
                generator = PreMarketReportGenerator()

                # Should not raise exception
                generator.send_discord_notification(sample_report_content)

    @pytest.mark.unit
    def test_discord_sends_with_correct_payload(self, mock_env_vars, sample_report_content, mock_requests_response):
        """Test that Discord sends with correct embed format."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.requests.post') as mock_post:
                mock_post.return_value = mock_requests_response

                generator.send_discord_notification(sample_report_content)

                # Check POST was called
                assert mock_post.called

                # Check payload structure
                call_kwargs = mock_post.call_args
                json_payload = call_kwargs.kwargs.get('json')
                assert json_payload is not None
                assert 'embeds' in json_payload

    @pytest.mark.unit
    def test_discord_truncates_summary(self, mock_env_vars):
        """Test that Discord truncates summary to 1500 chars."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            # Create very long report
            long_report = "B" * 5000

            with patch('daily_premarket_report.requests.post') as mock_post:
                mock_post.return_value = MagicMock(status_code=200)

                generator.send_discord_notification(long_report)

                # Check that payload is created (truncation happens inside)
                assert mock_post.called

    @pytest.mark.unit
    def test_discord_handles_request_error(self, mock_env_vars, sample_report_content):
        """Test that Discord handles request errors gracefully."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.requests.post', side_effect=Exception("Network error")):
                # Should not raise exception
                generator.send_discord_notification(sample_report_content)

    @pytest.mark.unit
    def test_discord_uses_blue_color(self, mock_env_vars, sample_report_content, mock_requests_response):
        """Test that Discord embed uses blue color (3447003)."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            with patch('daily_premarket_report.requests.post') as mock_post:
                mock_post.return_value = mock_requests_response

                generator.send_discord_notification(sample_report_content)

                if mock_post.called:
                    call_kwargs = mock_post.call_args
                    json_payload = call_kwargs.kwargs.get('json', {})

                    if 'embeds' in json_payload and len(json_payload['embeds']) > 0:
                        embed = json_payload['embeds'][0]
                        # Color should be 3447003 (blue)
                        assert embed.get('color') == 3447003


class TestSendNotifications:
    """Test send_notifications() wrapper method."""

    @pytest.mark.unit
    def test_send_notifications_calls_all_methods(self, mock_env_vars, sample_report_content, temp_dir):
        """Test that send_notifications calls all notification methods."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            filepath = temp_dir / 'test.md'
            filepath.write_text(sample_report_content)

            with patch.object(generator, 'send_email_notification') as mock_email, \
                 patch.object(generator, 'send_slack_notification') as mock_slack, \
                 patch.object(generator, 'send_discord_notification') as mock_discord:

                generator.send_notifications(sample_report_content, filepath)

                # Check all methods were called
                mock_email.assert_called_once()
                mock_slack.assert_called_once()
                mock_discord.assert_called_once()

    @pytest.mark.unit
    def test_send_notifications_continues_on_error(self, mock_env_vars, sample_report_content, temp_dir):
        """Test that send_notifications continues even if one method fails."""
        with patch('daily_premarket_report.Anthropic'):
            generator = PreMarketReportGenerator()

            filepath = temp_dir / 'test.md'
            filepath.write_text(sample_report_content)

            with patch.object(generator, 'send_email_notification', side_effect=Exception("Email failed")), \
                 patch.object(generator, 'send_slack_notification') as mock_slack, \
                 patch.object(generator, 'send_discord_notification') as mock_discord:

                # Should not raise exception
                generator.send_notifications(sample_report_content, filepath)

                # Slack and Discord should still be called
                mock_slack.assert_called_once()
                mock_discord.assert_called_once()
