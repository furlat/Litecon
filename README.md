# Litecon

Litecon is a library for implementing turn-based Double Auction simulations with literate economic agents capable of reading/writing news and communicating with each other. The library aims to study the role of news and information processing in the pricing dynamics of simulated virtual financial markets. Traditional economic models have struggled to acknowledge the role of information networks in price formation beyond simplistic implementations due to the inability to model human communication using natural language. The latest generation of LLMs now makes this possible.

This library seeks to merge and validate formal economic models of trade and learning with recent agent-based modeling capabilities. Large language models can implement, model, and formalize three fundamental aspects of realistic economic agents that have been known weaknesses of traditional economic models:

1. Information and communication beyond prices
2. In-context learning mimicking human behavior exhibited in experiments and actual markets
3. Bounded rationality through context overflow management and prompting choices

We anchor our simulation environment to the theoretical framework for modeling human experiments as Microeconomic Systems proposed by Nobel laureate Vernon L. Smith (1982). This framework's extensive use of information theory terminology offers an immediate connection to modern LLM theory and practice.

## Microeconomic Systems

A microeconomic system is a framework for modeling economic interactions between agents. It consists of two main components: an environment and an institution. The environment defines the characteristics of the economic agents, including their preferences, endowments, and technologies. The institution specifies the rules governing how agents can communicate and exchange goods or services. This framework allows economists to study how different environmental conditions and institutional rules impact economic outcomes and agent behavior.

## Double Auction

Double auctions are a specific type of microeconomic system commonly used in experimental economics and financial markets. In a double auction, buyers and sellers can simultaneously submit bids and offers for a single type of good. The environment typically consists of separate buyer and seller populations, each with their own induced values or costs for the good. The institutional rules allow participants to freely announce bids and offers, with trades occurring when a bid meets or exceeds an offer. This structure facilitates price discovery and efficient allocation of resources, making double auctions a powerful tool for studying market dynamics and testing economic theories.




| Proposition | Description |
|-------------|-------------|
| 4 | Allocations and prices in DA converge to levels near the competitive equilibrium (C.E.) prediction. This convergence is rapid, occurring in three to four trading periods or less with experienced subjects. |
| 5 | Convergence to C.E. prices and allocations occurs with as few as six to eight agents, and as few as two sellers. |
| 6 | Complete information on the theoretical supply and demand conditions is neither necessary nor sufficient for the rapid convergence property in DA. |
| 7 | Price convergence tends to be from above (below) the C.E. price when consumer's surplus is greater (smaller) than producer's surplus. |
| 8 | Experiments with one seller and five buyers do not achieve monopoly outcomes in DA, although some replications achieve the C.E. outcome. Buyers tend to withhold purchases, giving the seller a reduced profit. |
| 9 | Experiments with four buyers and four sellers where sellers (or buyers) are allowed to "conspire" do not converge to the monopoly (or monopsony) outcome in DA; neither do they seem to converge dependably to the C.E. |
| 10 | Binding price ceilings (floors) in DA yield contract price sequences which converge to the ceiling price from below (above). Non-binding price controls affect price dynamics but ultimately converge to C.E. |
| 11 | Asset markets with eight or nine agents in DA converge slowly toward the C.E. (rational expectations) price and efficiency. Convergence is hastened by introducing a futures market. |
| 12 | Asset markets with nine or twelve agents in DA, where some agents have insider information, converge toward the C.E. (rational expectations) price and efficiency. |


## Design and Implementation

```mermaid
classDiagram
    class Environment {
        +agents: List[Agent]
        +commodities: List[Commodity]
    }
    class Institution {
        +language: Language
        +allocation_rules: AllocationRules
        +cost_imputation_rules: CostImputationRules
        +adjustment_process_rules: AdjustmentProcessRules
    }
    class MicroeconomicSystem {
        +environment: Environment
        +institution: Institution
    }
    class Agent {
        +id: int
        +utility_function: Function
        +endowment: Dict[Commodity, float]
        +send_message(message: Message)
        +receive_message(message: Message)
    }
    class Buyer {
        +induced_value: float
    }
    class Seller {
        +induced_cost: float
    }
    class Commodity {
        +id: int
        +name: str
    }
    class Message {
        +sender: Agent
        +content: str
        +timestamp: datetime
    }
    class Bid {
        +price: float
        +quantity: int
    }
    class Ask {
        +price: float
        +quantity: int
    }
    class Language {
        +valid_messages: List[str]
    }
    class AllocationRules {
        +determine_allocation(bids: List[Bid], asks: List[Ask])
    }
    class CostImputationRules {
        +calculate_costs(trades: List[Trade])
    }
    class AdjustmentProcessRules {
        +start_rule()
        +transition_rule()
        +stopping_rule()
    }
    class DoubleAuction {
        +buyers: List[Buyer]
        +sellers: List[Seller]
        +bids: List[Bid]
        +asks: List[Ask]
        +trades: List[Trade]
        +current_price: float
        +submit_bid(bid: Bid)
        +submit_ask(ask: Ask)
        +execute_trades()
        +clear_market()
    }
    class Trade {
        +buyer: Buyer
        +seller: Seller
        +price: float
        +quantity: int
        +timestamp: datetime
    }

    MicroeconomicSystem *-- Environment
    MicroeconomicSystem *-- Institution
    Environment *-- Agent
    Environment *-- Commodity
    Agent <|-- Buyer
    Agent <|-- Seller
    Agent -- Message
    Message <|-- Bid
    Message <|-- Ask
    Institution *-- Language
    Institution *-- AllocationRules
    Institution *-- CostImputationRules
    Institution *-- AdjustmentProcessRules
    DoubleAuction *-- Buyer
    DoubleAuction *-- Seller
    DoubleAuction *-- Bid
    DoubleAuction *-- Ask
    DoubleAuction *-- Trade
```