"""
Catalyst Alerts - Multi-Channel Notification System
Sends priority-based alerts for catalyst events via email, Slack, Discord, Telegram
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class CatalystAlerts:
    """
    Multi-channel alert system for catalyst events

    Supported Channels:
    - Email (Gmail SMTP)
    - Slack (webhook)
    - Discord (webhook)
    - Telegram (bot API)

    Priority Handling:
    - CRITICAL: All channels immediately
    - HIGH: Email + primary channel
    - MEDIUM: Primary channel only
    - LOW: Logged only, no alerts
    """

    def __init__(
        self,
        email_config: Optional[Dict] = None,
        slack_webhook: Optional[str] = None,
        discord_webhook: Optional[str] = None,
        telegram_config: Optional[Dict] = None,
        primary_channel: str = 'email'
    ):
        """
        Initialize Catalyst Alerts

        Args:
            email_config: Dict with smtp_server, smtp_port, username, password, from_email, to_emails
            slack_webhook: Slack webhook URL
            discord_webhook: Discord webhook URL
            telegram_config: Dict with bot_token, chat_id
            primary_channel: Primary notification channel ('email', 'slack', 'discord', 'telegram')
        """
        # Email configuration
        self.email_config = email_config or self._load_email_config_from_env()

        # Webhook URLs
        self.slack_webhook = slack_webhook or os.getenv('SLACK_WEBHOOK_URL')
        self.discord_webhook = discord_webhook or os.getenv('DISCORD_WEBHOOK_URL')

        # Telegram configuration
        self.telegram_config = telegram_config or self._load_telegram_config_from_env()

        self.primary_channel = primary_channel

        # Alert history
        self.sent_alerts: List[Dict] = []

        logger.info(f"CatalystAlerts initialized (primary: {primary_channel})")

    def _load_email_config_from_env(self) -> Dict:
        """Load email config from environment variables"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'from_email': os.getenv('EMAIL_FROM'),
            'to_emails': os.getenv('EMAIL_TO', '').split(',')
        }

    def _load_telegram_config_from_env(self) -> Dict:
        """Load Telegram config from environment variables"""
        return {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID')
        }

    async def send_catalyst_alert(self, event) -> None:
        """
        Send alert for catalyst event based on priority

        Args:
            event: CatalystEvent object
        """
        priority = event.priority.value

        try:
            if priority == 'CRITICAL':
                # Send to all channels immediately
                await asyncio.gather(
                    self._send_email_alert(event),
                    self._send_slack_alert(event),
                    self._send_discord_alert(event),
                    self._send_telegram_alert(event),
                    return_exceptions=True
                )
                logger.info(f"Sent CRITICAL alert for {event.ticker} to all channels")

            elif priority == 'HIGH':
                # Send to email + primary channel
                if self.primary_channel == 'email':
                    await self._send_email_alert(event)
                elif self.primary_channel == 'slack':
                    await asyncio.gather(
                        self._send_email_alert(event),
                        self._send_slack_alert(event)
                    )
                elif self.primary_channel == 'discord':
                    await asyncio.gather(
                        self._send_email_alert(event),
                        self._send_discord_alert(event)
                    )
                elif self.primary_channel == 'telegram':
                    await asyncio.gather(
                        self._send_email_alert(event),
                        self._send_telegram_alert(event)
                    )

                logger.info(f"Sent HIGH alert for {event.ticker}")

            elif priority == 'MEDIUM':
                # Send to primary channel only
                if self.primary_channel == 'email':
                    await self._send_email_alert(event)
                elif self.primary_channel == 'slack':
                    await self._send_slack_alert(event)
                elif self.primary_channel == 'discord':
                    await self._send_discord_alert(event)
                elif self.primary_channel == 'telegram':
                    await self._send_telegram_alert(event)

                logger.info(f"Sent MEDIUM alert for {event.ticker} to {self.primary_channel}")

            else:  # LOW
                logger.info(f"LOW priority event for {event.ticker}, no alert sent")

            # Record alert
            self._record_alert(event, priority)

        except Exception as e:
            logger.error(f"Error sending catalyst alert for {event.ticker}: {e}")

    async def _send_email_alert(self, event) -> None:
        """Send email alert"""
        if not self.email_config.get('username') or not self.email_config.get('password'):
            logger.debug("Email not configured, skipping email alert")
            return

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{event.priority.value}] Catalyst Alert: {event.ticker} - {event.catalyst_type.value}"
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])

            # Create HTML body
            html_body = self._format_email_body(event)
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['username'], self.email_config['password'])
                server.send_message(msg)

            logger.debug(f"Sent email alert for {event.ticker}")

        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    async def _send_slack_alert(self, event) -> None:
        """Send Slack webhook alert"""
        if not self.slack_webhook:
            logger.debug("Slack webhook not configured, skipping")
            return

        try:
            # Format message
            message = self._format_slack_message(event)

            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook,
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.debug(f"Sent Slack alert for {event.ticker}")
                    else:
                        logger.error(f"Slack webhook error: {response.status}")

        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    async def _send_discord_alert(self, event) -> None:
        """Send Discord webhook alert"""
        if not self.discord_webhook:
            logger.debug("Discord webhook not configured, skipping")
            return

        try:
            # Format message
            message = self._format_discord_message(event)

            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.discord_webhook,
                    json=message,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 204]:
                        logger.debug(f"Sent Discord alert for {event.ticker}")
                    else:
                        logger.error(f"Discord webhook error: {response.status}")

        except Exception as e:
            logger.error(f"Error sending Discord alert: {e}")

    async def _send_telegram_alert(self, event) -> None:
        """Send Telegram bot alert"""
        if not self.telegram_config.get('bot_token') or not self.telegram_config.get('chat_id'):
            logger.debug("Telegram not configured, skipping")
            return

        try:
            # Format message
            message = self._format_telegram_message(event)

            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            payload = {
                'chat_id': self.telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        logger.debug(f"Sent Telegram alert for {event.ticker}")
                    else:
                        logger.error(f"Telegram API error: {response.status}")

        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")

    def _format_email_body(self, event) -> str:
        """Format HTML email body"""
        priority_color = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107',
            'LOW': '#28a745'
        }.get(event.priority.value, '#6c757d')

        sentiment_emoji = {
            'POSITIVE': '📈',
            'NEGATIVE': '📉',
            'NEUTRAL': '➡️'
        }.get(event.sentiment or 'NEUTRAL', '❓')

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: {priority_color}; color: white; padding: 15px; }}
                .content {{ padding: 20px; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>[{event.priority.value}] Catalyst Alert: {event.ticker}</h2>
            </div>
            <div class="content">
                <div class="detail">
                    <span class="label">Type:</span> {event.catalyst_type.value}
                </div>
                <div class="detail">
                    <span class="label">Title:</span> {event.title}
                </div>
                <div class="detail">
                    <span class="label">Description:</span> {event.description}
                </div>
                <div class="detail">
                    <span class="label">Sentiment:</span> {sentiment_emoji} {event.sentiment or 'N/A'}
                </div>
                <div class="detail">
                    <span class="label">Time:</span> {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                {f'<div class="detail"><span class="label">Source:</span> {event.source}</div>' if event.source else ''}
            </div>
        </body>
        </html>
        """

        return html

    def _format_slack_message(self, event) -> Dict:
        """Format Slack message"""
        priority_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': 'ℹ️',
            'LOW': '📝'
        }.get(event.priority.value, '❓')

        sentiment_emoji = {
            'POSITIVE': '📈',
            'NEGATIVE': '📉',
            'NEUTRAL': '➡️'
        }.get(event.sentiment or 'NEUTRAL', '❓')

        return {
            "text": f"{priority_emoji} [{event.priority.value}] Catalyst Alert: {event.ticker}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{priority_emoji} {event.ticker} - {event.catalyst_type.value}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Priority:*\n{event.priority.value}"},
                        {"type": "mrkdwn", "text": f"*Sentiment:*\n{sentiment_emoji} {event.sentiment or 'N/A'}"},
                        {"type": "mrkdwn", "text": f"*Title:*\n{event.title}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{event.timestamp.strftime('%H:%M:%S')}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{event.description[:500]}"
                    }
                }
            ]
        }

    def _format_discord_message(self, event) -> Dict:
        """Format Discord embed message"""
        priority_color = {
            'CRITICAL': 16711680,  # Red
            'HIGH': 16744192,      # Orange
            'MEDIUM': 16776960,    # Yellow
            'LOW': 65280           # Green
        }.get(event.priority.value, 8421504)  # Gray

        sentiment_emoji = {
            'POSITIVE': ':chart_with_upwards_trend:',
            'NEGATIVE': ':chart_with_downwards_trend:',
            'NEUTRAL': ':arrow_right:'
        }.get(event.sentiment or 'NEUTRAL', ':question:')

        return {
            "embeds": [{
                "title": f"[{event.priority.value}] {event.ticker} - {event.catalyst_type.value}",
                "description": event.title,
                "color": priority_color,
                "fields": [
                    {"name": "Description", "value": event.description[:1000], "inline": False},
                    {"name": "Sentiment", "value": f"{sentiment_emoji} {event.sentiment or 'N/A'}", "inline": True},
                    {"name": "Time", "value": event.timestamp.strftime('%Y-%m-%d %H:%M:%S'), "inline": True}
                ],
                "footer": {"text": f"Source: {event.source}" if event.source else "Catalyst Monitor"},
                "timestamp": event.timestamp.isoformat()
            }]
        }

    def _format_telegram_message(self, event) -> str:
        """Format Telegram message (Markdown)"""
        priority_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': 'ℹ️',
            'LOW': '📝'
        }.get(event.priority.value, '❓')

        sentiment_emoji = {
            'POSITIVE': '📈',
            'NEGATIVE': '📉',
            'NEUTRAL': '➡️'
        }.get(event.sentiment or 'NEUTRAL', '❓')

        message = f"""
{priority_emoji} *[{event.priority.value}] Catalyst Alert*

*Ticker:* {event.ticker}
*Type:* {event.catalyst_type.value}
*Title:* {event.title}

*Description:*
{event.description}

*Sentiment:* {sentiment_emoji} {event.sentiment or 'N/A'}
*Time:* {event.timestamp.strftime('%H:%M:%S')}
"""

        return message.strip()

    def _record_alert(self, event, priority: str) -> None:
        """Record sent alert in history"""
        self.sent_alerts.append({
            'ticker': event.ticker,
            'catalyst_type': event.catalyst_type.value,
            'priority': priority,
            'timestamp': datetime.now(),
            'channels': self._get_channels_for_priority(priority)
        })

        # Keep only last 1000 alerts
        if len(self.sent_alerts) > 1000:
            self.sent_alerts = self.sent_alerts[-1000:]

    def _get_channels_for_priority(self, priority: str) -> List[str]:
        """Get channels used for priority level"""
        if priority == 'CRITICAL':
            return ['email', 'slack', 'discord', 'telegram']
        elif priority == 'HIGH':
            return ['email', self.primary_channel]
        elif priority == 'MEDIUM':
            return [self.primary_channel]
        else:
            return []

    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        if not self.sent_alerts:
            return {
                'total_alerts': 0,
                'by_priority': {},
                'by_ticker': {},
                'recent_alerts': []
            }

        # Count by priority
        by_priority = {}
        by_ticker = {}

        for alert in self.sent_alerts:
            priority = alert['priority']
            ticker = alert['ticker']

            by_priority[priority] = by_priority.get(priority, 0) + 1
            by_ticker[ticker] = by_ticker.get(ticker, 0) + 1

        # Get recent alerts (last 10)
        recent = self.sent_alerts[-10:]

        return {
            'total_alerts': len(self.sent_alerts),
            'by_priority': by_priority,
            'by_ticker': by_ticker,
            'recent_alerts': [
                {
                    'ticker': a['ticker'],
                    'type': a['catalyst_type'],
                    'priority': a['priority'],
                    'time': a['timestamp'].isoformat()
                }
                for a in recent
            ]
        }
