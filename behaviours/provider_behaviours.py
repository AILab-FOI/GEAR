import json
import asyncio

from spade.behaviour import FSMBehaviour, State, OneShotBehaviour

from behaviours.communication_behaviours import SendMessageBehaviour

from utils.gamification import adjust_proposal_values
from utils.service import Service
from utils.logger import logger


class PerformServiceBehaviour(OneShotBehaviour):

    def __init__(self, service: Service, consumer_jid: str):
        super().__init__()
        self.service = service
        self.consumer_jid = consumer_jid

    async def run(self):
        logger.info(f"[Provider {self.agent.jid}] Performing service {self.service.name} for {self.consumer_jid}")
        service_providing_medium = next(filter(lambda medium: medium.get_feature_value("available"), self.agent.capacity), None)
        service_providing_medium.set_feature("available", False)
        await asyncio.sleep(self.service.duration)
        service_providing_medium.set_feature("available", True)

        send_message_behaviour = SendMessageBehaviour(
            self.consumer_jid, {"service": self.service.to_dict()}, {"performative": "confirm"}
        )
        self.agent.add_behaviour(send_message_behaviour)

    async def on_end(self):
        logger.info(f"[Provider {self.agent.jid}] Service {self.service.name} complete for {self.consumer_jid}")

class Idle(State):
    async def run(self):
        logger.info(f"[Provider {self.agent.jid}] Idle, inbox: {self.agent.inbox}")

        if self.agent.inbox:
            self.set_next_state("AnalyseMessage")
        else:
            await asyncio.sleep(1)
            self.set_next_state("Idle")

class AnalyseMessage(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Analysing message:\n{self.message}\n")

    async def run(self):
        try:
            metadata = self.message.metadata
        except Exception:
            self.set_next_state("Idle")
            return

        message_type = metadata.get("performative")

        match message_type:
            case "call for proposal":
                self.set_next_state("ProcessProposal")
            case "accept proposal":
                self.set_next_state("ProcessProposalAccept")
            case "reject proposal":
                self.set_next_state("ProcessProposalReject")
            case "request":
                self.set_next_state("ProcessRequest")
            case "inform":
                self.set_next_state("ProcessInform")
            case _:
                self.set_next_state("Idle")

    async def on_end(self):
        self.agent.inbox.append(self.message)
        logger.info(f"[Provider {self.agent.jid}] Message analysis complete")

class ProcessProposal(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Processing proposal")
        self.proposed_service = Service.from_dict(json.loads(self.message.body).get("service"))

    async def run(self):
        if self.proposed_service.name in [service.name for service in self.agent.services] and any(medium.get_feature_value("available") for medium in self.agent.capacity):
                self.matching_service = next(filter(lambda service: service.name == self.proposed_service.name, self.agent.services), None)

                self.proposal = adjust_proposal_values(self.matching_service)

                send_message_behaviour = SendMessageBehaviour(
                    self.message.sender, {"service": self.proposal.to_dict()}, {"performative": "propose"}
                )
                self.agent.add_behaviour(send_message_behaviour)
                logger.info(f"[Provider {self.agent.jid}] Sent proposal: {self.proposal}")
        else:
            send_message_behaviour = SendMessageBehaviour(
                self.message.sender, {"service": self.proposed_service.to_dict()}, {"performative": "refuse"}
            )
            self.agent.add_behaviour(send_message_behaviour)
            logger.info(f"[Provider {self.agent.jid}] Service {self.proposed_service.name} not available")

        self.set_next_state("Idle")

class ProcessProposalAccept(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Processing proposal acceptance")

    async def run(self):
        self.set_next_state("Idle")

class ProcessProposalReject(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Processing proposal rejection")

    async def run(self):
        self.set_next_state("Idle")

class ProcessRequest(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Processing request")

    async def run(self):
        if "services" in json.loads(self.message.body):
            send_message_behaviour = SendMessageBehaviour(
                self.message.sender, {"services": [service.name for service in self.agent.services]}, {"performative": "inform"}
            )
            self.agent.add_behaviour(send_message_behaviour)
            logger.info(f"[Provider {self.agent.jid}] Sent services: {[service.name for service in self.agent.services]}")

            self.set_next_state("Idle")

        if "service" in json.loads(self.message.body):
            logger.info(f"[Provider {self.agent.jid}] Service providing media: {self.agent.capacity}")
            self.requested_service = Service.from_dict(json.loads(self.message.body).get("service"))
            if self.requested_service.name in [service.name for service in self.agent.services] and any(medium.get_feature_value("available") for medium in self.agent.capacity):
                send_message_behaviour = SendMessageBehaviour(
                    self.message.sender, {"service": self.requested_service.to_dict()}, {"performative": "agree"}
                )
                self.agent.add_behaviour(send_message_behaviour)
                logger.info(f"[Provider {self.agent.jid}] Request approved")
                self.set_next_state("PerformServiceState")
                self.agent.inbox.append(self.message)
            else:
                send_message_behaviour = SendMessageBehaviour(
                    self.message.sender, {"service": self.requested_service.to_dict()}, {"performative": "refuse"}
                )
                self.agent.add_behaviour(send_message_behaviour)
                logger.info(f"[Provider {self.agent.jid}] Request denied")

                self.set_next_state("Idle")

class ProcessInform(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Processing inform")
        self.subject_service = Service.from_dict(json.loads(self.message.body).get("service"))

    async def run(self):
        self.msg = json.loads(self.message.body)
        if "cost" in self.msg:
            self.agent.budget += self.msg.get("cost")
            logger.info(f"[Provider {self.agent.jid}] Received payment for service {self.subject_service.name}")
        self.set_next_state("Idle")

class PerformServiceState(State):
    async def on_start(self):
        self.message = self.agent.inbox.pop()
        logger.info(f"[Provider {self.agent.jid}] Performing service")
        self.requested_service = Service.from_dict(json.loads(self.message.body).get("service"))

    async def run(self):
        perform_service_behaviour = PerformServiceBehaviour(self.requested_service, self.message.sender)
        self.agent.add_behaviour(perform_service_behaviour)
        self.set_next_state("Idle")

    async def on_end(self):
        logger.info(f"[Provider {self.agent.jid}] Service complete")

def setup_FSM_provider_behaviour():
    fsm = FSMBehaviour()

    fsm.add_state(name="Idle", state=Idle(), initial=True)
    fsm.add_state(name="AnalyseMessage", state=AnalyseMessage())
    fsm.add_state(name="ProcessProposal", state=ProcessProposal())
    fsm.add_state(name="ProcessProposalAccept", state=ProcessProposalAccept())
    fsm.add_state(name="ProcessProposalReject", state=ProcessProposalReject())
    fsm.add_state(name="ProcessRequest", state=ProcessRequest())
    fsm.add_state(name="ProcessInform", state=ProcessInform())
    fsm.add_state(name="PerformServiceState", state=PerformServiceState())

    fsm.add_transition(source="Idle", dest="AnalyseMessage")
    fsm.add_transition(source="Idle", dest="Idle")
    fsm.add_transition(source="AnalyseMessage", dest="ProcessProposal")
    fsm.add_transition(source="AnalyseMessage", dest="ProcessProposalAccept")
    fsm.add_transition(source="AnalyseMessage", dest="ProcessProposalReject")
    fsm.add_transition(source="AnalyseMessage", dest="ProcessRequest")
    fsm.add_transition(source="AnalyseMessage", dest="ProcessInform")
    fsm.add_transition(source="ProcessProposal", dest="Idle")
    fsm.add_transition(source="ProcessProposalAccept", dest="Idle")
    fsm.add_transition(source="ProcessProposalReject", dest="Idle")
    fsm.add_transition(source="ProcessRequest", dest="PerformServiceState")
    fsm.add_transition(source="ProcessRequest", dest="Idle")
    fsm.add_transition(source="ProcessInform", dest="Idle")
    fsm.add_transition(source="PerformServiceState", dest="Idle")

    return fsm