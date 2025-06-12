# Gamified Emergent Agent Relations (GEAR)

![alt text](logo.png)

> *recipeWorld* is an agent-based model that simulates the emergence of networks out of a decentralized autonomous interaction. [^Fontana2015recipeWorld]

This repository contains an implementation of GEAR, a multiagent system inspired by the recipeWorld model. The implementation is based on the [SPADE](https://spade-mas.readthedocs.io/en/latest/index.html) agent implementation framework.

The basic elements of the recipeWorld model can be abstracted to the following fundamental elements of GEAR:

- **Consumers** have a *recipe* that they need to complete. The recipe is a list of *services* that need to be performed. Consumers have a *budget* that they can spend on services. Consumers can *request* services from providers.
- **Providers** offer *services* that consumers can request. Providers have a *budget* that they can spend on services. Providers can *accept* or *reject* requests from consumers. Providers can *inform* consumers when a service is complete.

One of the main goals of the original recipeWorld is to study the emergence of *networks* between consumers and providers. The network is formed by the *requests* and *inform* messages that are exchanged between consumers and providers. The network is analysed using *network analysis* techniques to study the emergence of *communities* and *hubs*. This feature is not implemented in this version of the GEAR, although agents do communicate with each other, and a log of all messages and interaction is kept.

## Install and Run

Clone the repository.

The virtual environment for running this project can easily be setup using [uv](https://github.com/astral-sh/uv). Set it up by running the following command in the root directory of the project:

```bash
uv sync
```

To run the project, use the following command:

```bash
uv run main.py
```

Agents need an XMPP server to live on and communicate with each other. SPADE offers a built-in XMPP server that can be launched by running the following command:

```bash
spade run
```

A differently-sourced local XMPP server can be used as well. For example, it can be set up using `docker` by running the following command:

```bash
docker run -d -p 5222:5222 -p 5280:5280 --name prosody -h localhost prosody/prosody
```

## Visualised GEAR Implementation Details

### Class Diagram

```mermaid
---
  config:
    class:
      hideEmptyMembersBox: true
---
classDiagram
    class Behaviour {
    }
    class SPADE Agent {
        +jid: str
        +password: str
        +setup()
    }
    class ChimeraAgent {
        +personality: Personality
    }
    class Personality {
        +personality_descriptor: dict[str, int | float | PersonalityProfile]
        +get_personality_descriptor()
        +set_personality_descriptor(personality_descriptor: dict[str, int | float | PersonalityProfile])
        +get_personality_vector()
        +set_personality_vector(scores: list[float])
        +generate_random_personality_vector()
    }
    class PersonalityProfile {
        +scores: list[float]
        +get_facet_score(facet: str)
        +set_facet_score(facet: str, score: float)
        +get_factor_scores(factor: str)
        +set_factor_scores(factor: str, scores: list[float])
        +get_personality_vector()
        +set_personality_vector(scores: list[float])
        +generate_random_personality_vector()
    }
    class AgentWithInventory {
        +inventory: Inventory
    }
    class Inventory {
        +item_stack: dict[Item, dict[str, any]]
        +add_item(item: Item)
        +add_items(items: list[Item])
        +add_item_in_quantity(item: Item, quantity: int)
        +remove_item(item: Item)
        +has_item(item: Item)
        +get_items_in_inventory()
        +get_item_stacks()
        +get_items_by_name(name: str)
        +get_item_by_name(name: str)
        +get_item_by_feature(feature: str, value: any)
        +get_items_by_feature(feature: str, value: any)
        +get_item_quantity(item: Item)
        +get_total_quantity()
        +add_item_stack_attribute(item: Item, attribute: str, value: any)
        +update_item_stack_attribute(item: Item, attribute: str, value: any)
        +get_item_stack_attribute(item: Item, attribute: str)
        +remove_item_stack_attribute(item: Item, attribute: str)
        +get_item_stack_attributes(item: Item)
        +get_item_stack_by_attribute(attribute: str, value: any)
        +get_item_stack_by_attributes(attributes: dict)
        +get_item_stacks_by_attribute(attribute: str, value: any)
        +get_item_stacks_by_attributes(attributes: dict)
        +to_json()
        +from_json(json: dict)
    }
    class Item {
        +name: str
        +features: dict[str, any]
        +add_feature(feature: str, value: any)
        +set_feature(feature: str, value: any)
        +update_feature(feature: str, value: any)
        +update_features(features: dict[str, any])
        +get_feature_value(feature: str)
        +get_features()
        +remove_feature(feature: str)
        +get_name()
        +to_json()
        +from_json(json: dict)
    }
    class ServiceConsumerAgent {
        +budget: int
        +recipe: Recipe
        +current_recipe_element: dict[str, any]
        +completed_recipes: int
        +providers: dict[str, dict[str, any]]
        +setup()
    }
    class ServiceProviderAgent {
        +budget: int
        +services: list[Service]
        +inbox: deque[Message]
        +capacity: int
        +setup()
    }
    class Recipe {
        +recipe: list[dict[str, any]]
        +current_element_index: int
        +done: bool
        +get_recipe()
        +set_recipe(recipe: list[dict[str, any]])
        +get_recipe_length()
        +add_element(element: dict[str, any])
        +remove_element(element: dict[str, any])
        +get_current_element()
        +finish_current_element()
        +next_element()
        +check_if_done()
        +is_done()
        +to_json()
        +from_json(json: dict)
        +random()
    }
    class Service {
        +name: str
        +price: int
        +quality: int
        +to_dict()
        +from_dict(json: dict)
        +random()
    }
    Behaviour <-- SPADE Agent
    PersonalityProfile --* Personality
    Personality <-- ChimeraAgent
    SPADE Agent <|-- ChimeraAgent
    ChimeraAgent <|-- AgentWithInventory
    AgentWithInventory <|-- ServiceConsumerAgent
    AgentWithInventory <|-- ServiceProviderAgent
    AgentWithInventory --> Inventory
    ServiceConsumerAgent --> Recipe
    ServiceProviderAgent --> Service
    Inventory o-- Item
    Recipe <.. Service
```

### Service Provider Network

```mermaid
graph TD;
    A[Consumer] -->|Request| B[Provider];
    B -->|Response| A;
    A -->|Request| C[Provider];
    C -->|Response| A;
    A -->|Request| D[Provider];
    D -->|Response| A;
```

### Service Consumer Finite State Machine

```mermaid
stateDiagram-v2
    idle: Idle
    next: Next element
    tender: Put out to tender and wait
    best_offer: Select best offer
    request: Request service
    wait: Wait for service
    complete: Service complete
    complete_recipe: Completed recipe

    state budget <<choice>>
    state recipe <<choice>>
    state service <<choice>>
    state offers <<choice>>
    state request_approved <<choice>>
    state providers <<choice>>

    new_provider: Look for new provider

    [*] --> idle
    next --> tender
    tender --> offers
    offers --> best_offer: Offers received
    offers --> new_provider: No offers received
    best_offer --> budget
    budget --> request: Budget OK
    budget --> new_provider: Budget not OK
    state new_provider {
        [*] --> [*]
    }
    new_provider --> providers
    providers --> tender: New providers found
    providers --> [*]: No new providers found
    request --> request_approved
    request_approved --> wait: Request approved
    request_approved --> tender: Request denied
    wait --> service
    service --> complete: Service complete
    service --> wait: Service not complete
    complete --> idle
    idle --> recipe
    recipe --> next: Recipe not done
    recipe --> complete_recipe: Recipe done
    complete_recipe --> [*]
```

### Service Consumer Communication Sequence

```mermaid
sequenceDiagram
    autonumber
        actor c as Consumer
        participant p1 as Provider A
        participant p2 as Provider B
    loop Until recipe complete
        rect rgb(57, 208, 133)
            note over c: Call to Tender

            c->>p1: call for proposal
            p1->>c: propose

            c->>p2: call for proposal
            p2->>c: propose
        end
        
        note over c: Select best offer (A)

        rect rgb(57, 208, 133)
            note over c: Reject other offers
            c-xp2: reject proposal
        end

        alt Budget not OK
            c-xp1: reject proposal
            
            note over c: Look for new providers
            alt New providers found
                note right of c: Start from (1)
            else No new providers found
                note right of c: Stop agent
            end
        else Budget OK
            c->>p1: accept proposal
            c->>p2: reject proposal

            note over c: Request service
            c ->> p1: request
            
            alt Request denied
                p1-xc: refuse
            
            else Request approved
                p1->>c: agree
                activate p1
                note over c: Wait for service
                p1->>c: confirm
                deactivate p1
                c-xp1: inform w/ cost
                note over c: Next recipe element
            end
        end
    end
```

### Service Provider Finite State Machine

```mermaid
stateDiagram-v2
    idle: Idle
    analyse: Analyse message
    process_proposal: Process proposal
    process_proposal_accept: Process proposal accept
    process_proposal_reject: Process proposal reject
    process_request: Process request
    process_inform: Process inform
    perform: Perform service

    [*] --> idle
    idle --> analyse: \> 1 message
    idle --> idle: No messages
    analyse --> process_proposal: call for proposal
    analyse --> process_proposal_accept: accept proposal
    analyse --> process_proposal_reject: reject proposal
    analyse --> process_request: request
    analyse --> process_inform: inform
    process_proposal --> idle: Proposal processed
    process_proposal_accept --> idle: Proposal accepted
    process_proposal_reject --> idle: Proposal rejected
    process_request --> perform: Request processed
    process_inform --> idle: Inform processed
    perform --> idle: Service complete
```

[^Fontana2015recipeWorld]: Fontana, M., & Terna, P. (2015). From Agent-based models to network analysis (and return): The policy-making perspective (201507; Working Paper Series, str. 1–19). University of Turin Department of Economics and Statistics „Cognetti de Martiis“. https://ideas.repec.org/p/uto/dipeco/201507.html
