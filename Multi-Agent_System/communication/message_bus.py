"""
Asynchronous message bus for agent communication
"""

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
import logging
from .protocols import AgentMessage

class MessageBus:
    """
    Central message bus for agent communication
    Implements pub/sub pattern for decoupled agent messaging
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[AgentMessage] = []
        self.max_history_size = 1000
        self.logger = logging.getLogger("message_bus")
        self.running = False
        
    async def start(self):
        """Start the message bus processing"""
        self.running = True
        self.logger.info("Message bus started")
        asyncio.create_task(self._process_messages())
        
    async def stop(self):
        """Stop the message bus"""
        self.running = False
        self.logger.info("Message bus stopped")
        
    async def publish(self, message: AgentMessage):
        """
        Publish a message to the bus
        
        Args:
            message: AgentMessage to publish
        """
        await self.message_queue.put(message)
        self.logger.debug(f"Message published from {message.agent_id}: {message.message_type}")
        
    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to messages on a specific topic
        
        Args:
            topic: Topic to subscribe to (ticker symbol or 'all')
            callback: Async function to call when message received
        """
        self.subscribers[topic].append(callback)
        self.logger.debug(f"New subscriber for topic: {topic}")
        
    def unsubscribe(self, topic: str, callback: Callable):
        """
        Unsubscribe from a topic
        
        Args:
            topic: Topic to unsubscribe from
            callback: Callback function to remove
        """
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            self.logger.debug(f"Unsubscribed from topic: {topic}")
            
    async def _process_messages(self):
        """Process messages from the queue"""
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                # Store in history
                self._add_to_history(message)
                
                # Deliver to subscribers
                await self._deliver_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                
    async def _deliver_message(self, message: AgentMessage):
        """
        Deliver message to appropriate subscribers
        
        Args:
            message: Message to deliver
        """
        # Deliver to ticker-specific subscribers
        if message.ticker in self.subscribers:
            for callback in self.subscribers[message.ticker]:
                try:
                    await callback(message)
                except Exception as e:
                    self.logger.error(f"Error in subscriber callback: {e}")
        
        # Deliver to 'all' subscribers
        for callback in self.subscribers.get('all', []):
            try:
                await callback(message)
            except Exception as e:
                self.logger.error(f"Error in 'all' subscriber callback: {e}")
                
    def _add_to_history(self, message: AgentMessage):
        """Add message to history with size limit"""
        self.message_history.append(message)
        
        # Trim history if too large
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
            
    def get_recent_messages(self, ticker: Optional[str] = None, 
                           agent_id: Optional[str] = None,
                           limit: int = 10) -> List[AgentMessage]:
        """
        Get recent messages from history
        
        Args:
            ticker: Filter by ticker symbol
            agent_id: Filter by agent ID
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        messages = self.message_history
        
        if ticker:
            messages = [m for m in messages if m.ticker == ticker]
        if agent_id:
            messages = [m for m in messages if m.agent_id == agent_id]
            
        return messages[-limit:]
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        agent_counts = defaultdict(int)
        ticker_counts = defaultdict(int)
        
        for msg in self.message_history:
            agent_counts[msg.agent_type] += 1
            ticker_counts[msg.ticker] += 1
            
        return {
            "total_messages": len(self.message_history),
            "queue_size": self.message_queue.qsize(),
            "subscriber_count": sum(len(subs) for subs in self.subscribers.values()),
            "agent_message_counts": dict(agent_counts),
            "ticker_message_counts": dict(ticker_counts)
        }