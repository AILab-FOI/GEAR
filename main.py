import asyncio
import argparse

from agents.service_provider_agent import ServiceProviderAgent
from agents.service_consumer_agent import ServiceConsumerAgent

from utils.service import Service


async def main(simulation_timeout=None):
    # Example provider services
    provider1_services = [Service("A", 10, 3), Service("B", 15, 5)]
    provider2_services = [Service("A", 8, 4), Service("C", 20, 2)]

    providers = []

    providers.append(ServiceProviderAgent("provider1@localhost", "password", provider1_services))
    providers.append(ServiceProviderAgent("provider2@localhost", "password", provider2_services))

    for provider_agent in providers:
        await provider_agent.start(auto_register=True)

    await asyncio.sleep(2)

    consumer = ServiceConsumerAgent("consumer1@localhost", "password", providers={provider.jid: {"services": None} for provider in providers})
    await consumer.start(auto_register=True)

    # Keep agents running for up to simulation_timeout seconds
    counter = 0
    while not consumer.main_FSM_behaviour.is_killed():
        try:
            await asyncio.sleep(1)
            counter += 1
            if simulation_timeout and counter == simulation_timeout:
                break
        except KeyboardInterrupt:
            break

    await consumer.stop()
    for provider_agent in providers:
        await provider_agent.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the GEAR multiagent system.")
    parser.add_argument("--nologs", action="store_true", help="Disable logging.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds.")
    args = parser.parse_args()
    if args.nologs:
        import logging
        logging.disable(logging.CRITICAL)
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main(simulation_timeout=args.timeout))
