"""
Simple message bus for agent communication
"""

import asyncio
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MessageBus:
    """Message bus for agent communication"""

    def __init__(self):
        self.subscribers = {}
        self.message_queue = asyncio.Queue()
        self.running = False

    async def start(self):
        """Start the message bus"""
        self.running = True
        logger.info("Message bus started")

    async def stop(self):
        """Stop the message bus"""
        self.running = False
        logger.info("Message bus stopped")

    async def publish(self, topic: str, message: Dict[Any, Any]):
        """Publish a message to a topic"""
        if topic in self.subscribers:
            for subscriber in self.subscribers[topic]:
                await subscriber(message)

    def subscribe(self, topic: str, callback):
        """Subscribe to a topic"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)