"""Simple message bus for agent communication."""

import asyncio
import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

SubscriberCallback = Callable[[Dict[str, Any]], Optional[Awaitable[None]]]


class MessageBus:
    """Message bus for agent communication."""

    def __init__(self) -> None:
        self.subscribers: Dict[str, List[SubscriberCallback]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False

    async def start(self) -> None:
        """Start the message bus."""
        self.running = True
        logger.info("Message bus started")

    async def stop(self) -> None:
        """Stop the message bus."""
        self.running = False
        logger.info("Message bus stopped")

    async def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Publish a message to all subscribers listening on the topic."""
        subscribers = self.subscribers.get(topic, [])
        for subscriber in subscribers:
            try:
                result = subscriber(message)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Subscriber error on topic %s: %s", topic, exc)

    def subscribe(self, topic: str, callback: SubscriberCallback) -> None:
        """Subscribe a callback to a topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
