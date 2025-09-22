import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from communication.message_bus import MessageBus


def test_publish_delivers_payload_to_subscriber():
    async def run_test():
        bus = MessageBus()
        await bus.start()

        received_payloads = []
        message_processed = asyncio.Event()

        async def subscriber(message):
            received_payloads.append(message["payload"])
            message_processed.set()

        bus.subscribe("agent.analysis", subscriber)

        payload = {"decision": "BUY"}
        message = {
            "agent_id": "test-agent",
            "agent_type": "test",
            "timestamp": "2024-01-01T00:00:00",
            "ticker": "AAPL",
            "message_type": "analysis",
            "payload": payload,
            "priority": 1,
        }

        await bus.publish("agent.analysis", message)
        await asyncio.wait_for(message_processed.wait(), timeout=1)

        assert received_payloads == [payload]

    asyncio.run(run_test())
