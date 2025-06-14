import json
import random
from spade.behaviour import FSMBehaviour, State, OneShotBehaviour

from behaviours.communication_behaviours import SendMessageBehaviour

from utils.logger import logger
from utils.recipe import Recipe
from utils.service import Service


def determine_best_offer(offers: list[dict[str, Service]], agent=None):
    """
    Determine the best offer based on service attributes and consumer personality.

    Args:
        offers: List of offers with provider and service information
        agent: The consumer agent with personality profile

    Returns:
        dict: Selected offer with provider and service information
    """
    if not offers:
        return None

    if not agent or not hasattr(agent, "personality"):
        best_offer = min(
            offers,
            key=lambda offer: offer.get("service").price
            / offer.get("service").duration,
        )
        best_provider = best_offer.get("provider")
        return {
            "provider": best_provider,
            "service": best_offer.get("service").to_dict(),
        }

    try:
        personality = agent.personality.personality_descriptor.get(
            "personality profile"
        )

        # Price sensitivity (influenced by Conscientiousness - Self-Discipline)
        price_sensitivity = personality.get_facet_score("Self-Discipline")

        # Quality focus (influenced by Conscientiousness - Dutifulness)
        quality_focus = personality.get_facet_score("Dutifulness")

        # Badge appreciation (influenced by Openness - Values)
        badge_appreciation = personality.get_facet_score("Values")

        # Risk tolerance (influenced by Extraversion - Excitement seeking)
        risk_tolerance = personality.get_facet_score("Excitement seeking")

        logger.info(
            f"[Consumer {agent.jid}] Personality factors: price_sensitivity={price_sensitivity:.2f}, "
            f"quality_focus={quality_focus:.2f}, badge_appreciation={badge_appreciation:.2f}, "
            f"risk_tolerance={risk_tolerance:.2f}"
        )

        offer_values = []
        for offer in offers:
            service = offer.get("service")
            provider = offer.get("provider")

            awards = offer.get("awards", {})
            awards = sum([
                len(awards.get("badges", [])),
                len(awards.get("trophies", []))
            ])

            price_value = service.price
            duration_value = service.duration
            awards_value = awards

            # Calculate weighted value (lower is better)
            # Price component (higher price sensitivity means price matters more)
            price_component = price_value * (0.5 + price_sensitivity * 0.5)

            # Duration component (higher quality focus means duration matters more - longer is better quality)
            duration_component = -duration_value * (quality_focus * 0.5)

            # Badge component (higher badge appreciation means awards matter more - more is better)
            badge_component = -awards_value * (badge_appreciation * 10)

            # Risk component (higher risk tolerance means more variability is acceptable)
            # This creates a random factor in the valuation            
            risk_component = (random.random() * 2 - 1) * risk_tolerance * 5

            # Total weighted value (lower is better)
            weighted_value = (
                price_component + duration_component + badge_component + risk_component
            )

            offer_values.append(
                {"provider": provider, "service": service, "value": weighted_value}
            )

            logger.info(
                f"[Consumer {agent.jid}] Offer from {provider}: price={service.price}, "
                f"duration={service.duration}, awards={awards}, value={weighted_value:.2f}"
            )

        best_offer = min(offer_values, key=lambda o: o["value"])
        logger.info(
            f"[Consumer {agent.jid}] Selected best offer from {best_offer['provider']} with value {best_offer['value']:.2f}"
        )

        return {
            "provider": best_offer["provider"],
            "service": best_offer["service"].to_dict(),
        }

    except Exception as e:
        logger.error(
            f"[Consumer {agent.jid}] Error in personality-based valuation: {e}"
        )

        best_offer = min(
            offers,
            key=lambda offer: offer.get("service").price
            / offer.get("service").duration,
        )
        best_provider = best_offer.get("provider")

        return {
            "provider": best_provider,
            "service": best_offer.get("service").to_dict(),
        }


class CheckOfferedServices(State):
    async def run(self):
        logger.info(f"[Consumer {self.agent.jid}] Checking offered services")

        providers = self.agent.providers.keys()
        for provider in providers:
            send_message_behaviour = SendMessageBehaviour(
                provider, {"services": []}, metadata={"performative": "request"}
            )
            self.agent.add_behaviour(send_message_behaviour)

            msg = await self.receive(timeout=5)
            if msg:
                try:
                    msg_body = json.loads(msg.body)
                    services = msg_body.get("services")
                except Exception:
                    continue
                if msg.metadata.get("performative") == "inform":
                    self.agent.providers.get(provider).update({"services": services})
        logger.info(f"[Consumer {self.agent.jid}] Providers: {self.agent.providers}")

        self.set_next_state("Idle")


class Idle(State):
    async def run(self):
        logger.info(f"[Consumer {self.agent.jid}] Idle.")
        recipe_done = self.agent.recipe.is_done()

        if recipe_done:
            self.set_next_state("CompleteRecipe")
        else:
            self.set_next_state("NextElement")


class NextElement(State):
    async def run(self):
        if self.agent.recipe.get_current_element().get("done"):
            self.agent.recipe.next_element()
        self.agent.current_recipe_element = self.agent.recipe.get_current_element()
        logger.info(
            f"[Consumer {self.agent.jid}] Starting with the next element in recipe {self.agent.recipe}"
        )
        self.set_next_state("Tender")


class Tender(State):
    async def on_start(self):
        self.offers = []
        logger.info(
            f"[Consumer {self.agent.jid}] Tendering for service {self.agent.current_recipe_element.get('service')}"
        )

    async def run(self):
        requested_service = self.agent.current_recipe_element.get("service")

        providers = list(
            filter(
                lambda provider: requested_service.name
                in self.agent.providers.get(provider).get("services"),
                self.agent.providers.keys(),
            )
        )

        for provider in providers:
            send_message_behaviour = SendMessageBehaviour(
                provider,
                {"service": requested_service.to_dict()},
                metadata={"performative": "call for proposal"},
            )
            self.agent.add_behaviour(send_message_behaviour)
            logger.info(
                f"[Consumer {self.agent.jid}] Sent query to {provider} for service {requested_service}"
            )

            reply = await self.receive(timeout=5)
            if reply:
                logger.info(
                    f"[Consumer {self.agent.jid}] Received reply from {provider}: {reply.body}"
                )
                try:
                    msg = json.loads(reply.body)
                    received_service = Service.from_dict(msg.get("service"))
                    awards = msg.get("awards", {})
                except Exception:
                    continue
                if reply.metadata.get("performative") == "propose":
                    if received_service.name == requested_service.name:
                        self.agent.current_recipe_element.get("providers").append(
                            provider
                        )
                        self.offers.append(
                            {
                                "provider": provider,
                                "service": received_service,
                                "awards": awards,
                            }
                        )

        if len(self.offers) == 0:
            self.set_next_state("LookForNewProvider")
        else:
            self.set_next_state("SelectBestOffer")

    async def on_end(self):
        self.agent.offers = self.offers
        logger.info(f"[Consumer {self.agent.jid}] Offers: {self.agent.offers}")


class SelectBestOffer(State):
    async def on_start(self):
        self.best_offer: Service = None
        self.best_provider = None
        logger.info(
            f"[Consumer {self.agent.jid}] Selecting best offer for service {self.agent.current_recipe_element.get('service')}"
        )

    async def run(self):
        offer = determine_best_offer(self.agent.offers, self.agent)
        self.best_offer = Service.from_dict(offer.get("service"))
        self.best_provider = offer.get("provider")

        providers = self.agent.current_recipe_element.get("providers")

        for provider in providers:
            if provider != self.best_provider:
                send_message_behaviour = SendMessageBehaviour(
                    provider,
                    {
                        "service": self.agent.current_recipe_element.get(
                            "service"
                        ).to_dict()
                    },
                    metadata={"performative": "reject proposal"},
                )
                self.agent.add_behaviour(send_message_behaviour)

        self.set_next_state("BudgetCheck")

    async def on_end(self):
        self.agent.best_offer = self.best_offer
        self.agent.best_provider = self.best_provider
        logger.info(
            f"[Consumer {self.agent.jid}] Best offer: {self.agent.best_offer} from {self.agent.best_provider}"
        )


class BudgetCheck(State):
    async def on_start(self):
        logger.info(
            f"[Consumer {self.agent.jid}] Checking budget for service {self.agent.best_offer}"
        )

    async def run(self):
        logger.info(f"[Consumer {self.agent.jid}] Budget: {self.agent.budget}")

        budget_ok = self.agent.budget >= self.agent.best_offer.price

        if budget_ok:
            send_message_behaviour = SendMessageBehaviour(
                self.agent.best_provider,
                {"service": self.agent.best_offer.to_dict()},
                metadata={"performative": "accept proposal"},
            )
            self.agent.add_behaviour(send_message_behaviour)

            self.set_next_state("RequestService")
        else:
            send_message_behaviour = SendMessageBehaviour(
                self.agent.best_provider,
                {"service": self.agent.best_offer.to_dict()},
                metadata={"performative": "reject proposal"},
            )
            self.agent.add_behaviour(send_message_behaviour)
            self.set_next_state("LookForNewProvider")

    async def on_end(self):
        logger.info(
            f"[Consumer {self.agent.jid}] Budget check complete. Budget OK? {self.agent.budget >= self.agent.best_offer.price}"
        )


class LookForNewProvider(State):
    async def on_start(self):
        logger.info(
            f"[Consumer {self.agent.jid}] Looking for new provider for service {self.agent.current_recipe_element.get('service')}"
        )
        self.providers = self.agent.providers

    async def run(self):
        # Logic to find a new provider
        if self.providers == self.agent.providers:
            self.kill()
        else:
            self.set_next_state("Tender")


class RequestService(State):
    async def on_start(self):
        logger.info(
            f"[Consumer {self.agent.jid}] Requesting service {self.agent.best_offer} from {self.agent.best_provider}"
        )
        self.request_approved = False

    async def run(self):
        send_message_behaviour = SendMessageBehaviour(
            self.agent.best_provider,
            {"service": self.agent.best_offer.to_dict()},
            metadata={"performative": "request"},
        )
        self.agent.add_behaviour(send_message_behaviour)

        reply = await self.receive(timeout=5)
        if reply:
            self.request_approved = reply.metadata.get("performative") == "agree"

        if self.request_approved:
            logger.info(f"[Consumer {self.agent.jid}] Request approved")
            self.set_next_state("WaitForService")
        else:
            logger.info(f"[Consumer {self.agent.jid}] Request denied")
            self.set_next_state("Tender")


class WaitForService(State):
    async def on_start(self):
        logger.info(
            f"[Consumer {self.agent.jid}] Waiting for service {self.agent.best_offer} from {self.agent.best_provider}"
        )
        self.service_complete = False

    async def run(self):
        reply = await self.receive(timeout=10)
        if reply:
            self.service_complete = reply.metadata.get("performative") == "confirm"

        if self.service_complete:
            logger.info(f"[Consumer {self.agent.jid}] Service complete")
            self.set_next_state("ServiceComplete")
        else:
            logger.info(f"[Consumer {self.agent.jid}] Service not yet complete")
            self.set_next_state("WaitForService")


class ServiceComplete(State):
    async def run(self):
        self.agent.recipe.finish_current_element()

        send_message_behaviour = SendMessageBehaviour(
            self.agent.best_provider,
            {
                "service": self.agent.best_offer.to_dict(),
                "cost": self.agent.best_offer.price,
            },
            metadata={"performative": "inform"},
        )
        self.agent.add_behaviour(send_message_behaviour)
        logger.info(f"[Consumer {self.agent.jid}] Payment sent")
        self.agent.budget -= self.agent.best_offer.price

        self.set_next_state("Idle")


class CompleteRecipe(State):
    async def run(self):
        if self.agent.completed_recipes < 2:
            self.agent.completed_recipes += 1
            self.agent.recipe = Recipe.random()
            logger.info(
                f"[Consumer {self.agent.jid}] Recipe completed. New recipe: {self.agent.recipe}"
            )
            print(
                f"[Consumer {self.agent.jid}] Starting with recipe: {self.agent.recipe} and budget: {self.agent.budget}"
            )
            self.set_next_state("Idle")
        else:
            logger.info(f"[Consumer {self.agent.jid}] All recipes completed. Exiting.")
            self.kill()


def setup_FSM():
    fsm = FSMBehaviour()
    fsm.add_state(
        name="CheckOfferedServices", state=CheckOfferedServices(), initial=True
    )
    fsm.add_state(name="Idle", state=Idle())
    fsm.add_state(name="NextElement", state=NextElement())
    fsm.add_state(name="Tender", state=Tender())
    fsm.add_state(name="SelectBestOffer", state=SelectBestOffer())
    fsm.add_state(name="BudgetCheck", state=BudgetCheck())
    fsm.add_state(name="LookForNewProvider", state=LookForNewProvider())
    fsm.add_state(name="RequestService", state=RequestService())
    fsm.add_state(name="WaitForService", state=WaitForService())
    fsm.add_state(name="ServiceComplete", state=ServiceComplete())
    fsm.add_state(name="CompleteRecipe", state=CompleteRecipe())

    fsm.add_transition(source="CheckOfferedServices", dest="Idle")
    fsm.add_transition(source="Idle", dest="NextElement")
    fsm.add_transition(source="Idle", dest="CompleteRecipe")
    fsm.add_transition(source="NextElement", dest="Tender")
    fsm.add_transition(source="Tender", dest="SelectBestOffer")
    fsm.add_transition(source="Tender", dest="LookForNewProvider")
    fsm.add_transition(source="SelectBestOffer", dest="BudgetCheck")
    fsm.add_transition(source="BudgetCheck", dest="RequestService")
    fsm.add_transition(source="BudgetCheck", dest="LookForNewProvider")
    fsm.add_transition(source="LookForNewProvider", dest="Tender")
    fsm.add_transition(source="RequestService", dest="WaitForService")
    fsm.add_transition(source="RequestService", dest="Tender")
    fsm.add_transition(source="WaitForService", dest="ServiceComplete")
    fsm.add_transition(source="WaitForService", dest="WaitForService")
    fsm.add_transition(source="ServiceComplete", dest="Idle")
    fsm.add_transition(source="CompleteRecipe", dest="Idle")

    return fsm
