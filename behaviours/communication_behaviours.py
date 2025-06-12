import json
import asyncio
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from utils.logger import logger


class ReceiveMessagesBehaviour(CyclicBehaviour):
    async def on_start(self):
        self.queue_type = self.agent.inbox.__class__.__name__
        logger.info(f"[{self.agent.jid}] Starting receive behaviour with queue_type: {self.queue_type}")

    def store_message(self, msg):
        if self.queue_type == "Queue":
            self.agent.inbox.put(msg)
        elif self.queue_type == "deque":
            self.agent.inbox.appendleft(msg)
        else:
            self.agent.inbox.append(msg)

    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            logger.info(f"[{self.agent.jid}] Received message:\n{msg}\n")
            try:
                self.store_message(msg)
            except Exception:
                return

        await asyncio.sleep(1)


class SendMessageBehaviour(OneShotBehaviour):
    def __init__(self, receiver: str=None, payload: dict=None, metadata: dict = None, message: Message = None):
        super().__init__()
        self.receiver = receiver
        self.payload = payload
        self.metadata = metadata
        self.message = message

    async def run(self):
        if self.message:
            msg = self.message
        else:
            msg = Message(to=self.receiver)
            msg.body = json.dumps(self.payload)
            msg.metadata = self.metadata
        await self.send(msg)
        logger.info(f"[{self.agent.jid}] Sent message:\n{msg}\n")
