import os
import matplotlib.pyplot as plt
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Tuple, Optional
from ziagents import ZIAgent, PreferenceSchedule, Allocation, Order
import os
from datetime import datetime
class Environment(BaseModel):
    agents: List[ZIAgent]
    buyers: List[ZIAgent] = Field(default_factory=list)
    sellers: List[ZIAgent] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self.buyers = [agent for agent in self.agents if agent.preference_schedule.is_buyer]
        self.sellers = [agent for agent in self.agents if not agent.preference_schedule.is_buyer]

    def get_agent(self, agent_id: int) -> Optional[ZIAgent]:
        """Retrieve an agent by their ID."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None  # Return None if no agent with the given ID is found

    def calculate_initial_utility(self, agent: ZIAgent) -> float:
        if agent.preference_schedule.is_buyer:
            return agent.allocation.initial_cash
        else:
            goods_value = sum(agent.preference_schedule.get_value(q) for q in range(1, agent.allocation.initial_goods + 1))
            return goods_value

    def get_agent_utility(self, agent: ZIAgent) -> float:
        if agent.preference_schedule.is_buyer:
            goods_utility = sum(agent.preference_schedule.get_value(q) for q in range(1, agent.allocation.goods + 1))
            return goods_utility + agent.allocation.cash
        else:
            goods_value = sum(agent.preference_schedule.get_value(q) for q in range(1, agent.allocation.goods + 1))
            return agent.allocation.cash + goods_value

    def get_total_utility(self) -> float:
        return sum(self.get_agent_utility(agent) for agent in self.agents)

    def print_market_state(self):
        print("\nMarket State:")
        for agent in self.agents:
            role = "Buyer" if agent.preference_schedule.is_buyer else "Seller"
            print(f"Agent {agent.id} ({role}):")
            print(f"  Goods: {agent.allocation.goods}")
            print(f"  Cash: {agent.allocation.cash:.2f}")
            print(f"  Utility: {self.get_agent_utility(agent):.2f}")
        print(f"Total Market Utility: {self.get_total_utility():.2f}")

    def calculate_remaining_trade_opportunities(self) -> int:
        potential_trades = 0
        for buyer in self.buyers:
            for seller in self.sellers:
                if buyer.allocation.cash > 0 and seller.allocation.goods > 0:
                    buyer_value = buyer.preference_schedule.get_value(buyer.allocation.goods + 1)
                    seller_cost = seller.preference_schedule.get_value(seller.allocation.goods)
                    if buyer_value > seller_cost and buyer.allocation.cash >= seller_cost:
                        potential_trades += 1
        return potential_trades

    def calculate_remaining_surplus(self) -> float:
        remaining_surplus = 0.0
        for buyer in self.buyers:
            for seller in self.sellers:
                if buyer.allocation.cash > 0 and seller.allocation.goods > 0:
                    buyer_value = buyer.preference_schedule.get_value(buyer.allocation.goods + 1)
                    seller_cost = seller.preference_schedule.get_value(seller.allocation.goods)
                    if buyer_value > seller_cost:
                        remaining_surplus += (buyer_value - seller_cost)
        return remaining_surplus

    def calculate_theoretical_supply_demand(self) -> Tuple[List[float], List[float], List[float], List[float]]:
        buyer_valuations = [agent.preference_schedule.values for agent in self.buyers]
        seller_costs = [agent.preference_schedule.values for agent in self.sellers]
        
        # Flatten and sort the valuations and costs
        demand_values = sorted([value for valuation in buyer_valuations for value in valuation.values()], reverse=True)
        supply_values = sorted([value for cost in seller_costs for value in cost.values()])

        demand_x, demand_y = [], []
        supply_x, supply_y = [], []
        
        # Generate demand curve points
        for i, value in enumerate(demand_values, start=1):
            demand_x.extend([i-1, i])
            demand_y.extend([value, value])
        
        # Generate supply curve points
        for i, value in enumerate(supply_values, start=1):
            supply_x.extend([i-1, i])
            supply_y.extend([value, value])

        return demand_x, demand_y, supply_x, supply_y

    def calculate_equilibrium(self) -> Tuple[float, float, float, float, float]:
        demand_x, demand_y, supply_x, supply_y = self.calculate_theoretical_supply_demand()

        ce_quantity = 0
        ce_price = 0
        for i in range(0, min(len(demand_x), len(supply_x)), 2):
            if demand_y[i] >= supply_y[i]:
                ce_quantity = i // 2 + 1  # Add 1 because we start from 0
                ce_price = (demand_y[i] + supply_y[i]) / 2
            else:
                break

        buyer_surplus = sum(max(demand_y[i] - ce_price, 0) for i in range(0, ce_quantity * 2, 2))
        seller_surplus = sum(max(ce_price - supply_y[i], 0) for i in range(0, ce_quantity * 2, 2))
        total_surplus = buyer_surplus + seller_surplus

        return ce_price, ce_quantity, buyer_surplus, seller_surplus, total_surplus


    def plot_theoretical_supply_demand(self, save_location=None):
        """Plot the theoretical supply and demand curves and the competitive equilibrium."""
        demand_x, demand_y, supply_x, supply_y = self.calculate_theoretical_supply_demand()
        ce_price, ce_quantity, buyer_surplus, seller_surplus, total_surplus = self.calculate_equilibrium()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.step(demand_x, demand_y, where='post', label='Theoretical Demand', color='blue', linestyle='--')
        ax.step(supply_x, supply_y, where='post', label='Theoretical Supply', color='red', linestyle='--')
        
        max_x = max(max(demand_x), max(supply_x))
        min_y = min(min(demand_y), min(supply_y))
        max_y = max(max(demand_y), max(supply_y))
        
        ax.set_xlim(0, max_x)
        ax.set_ylim(min_y * 0.9, max_y * 1.1)  # Add 10% padding

        ax.axvline(x=ce_quantity, color='green', linestyle='--', label=f'CE Quantity: {ce_quantity}')
        ax.axhline(y=ce_price, color='purple', linestyle='--', label=f'CE Price: {ce_price:.2f}')

        ax.set_xlabel('Quantity')
        ax.set_ylabel('Price')
        ax.set_title('Theoretical Supply and Demand Curves with CE')
        ax.legend()
        ax.grid(True)

        if save_location:
            file_path = os.path.join(save_location, "theoretical_supply_demand.png")
            fig.savefig(file_path)
            print(f"Plot saved to {file_path}")
        
        return fig
        
def generate_agents(num_agents: int, num_units: int,buyer_base_value:int,seller_base_value:int,spread:0.5) -> List[ZIAgent]:
    return [ZIAgent.generate(agent_id=i, max_relative_spread=spread,is_buyer=(i < num_agents//2), num_units=num_units, base_value=buyer_base_value if i < num_agents//2 else seller_base_value) for i in range(num_agents)]


if __name__ == "__main__":
    # Generate test agents
    num_buyers = 5
    num_sellers = 5
    spread = 0.5
    agents = generate_agents(num_agents=num_buyers + num_sellers, num_units=5,buyer_base_value=100,seller_base_value=80,spread=spread)
    # Create the environment
    env = Environment(agents=agents)

    # Print initial market state
    env.print_market_state()

    # Calculate and print initial utilities
    print("\nInitial Utilities:")
    for agent in env.agents:
        initial_utility = env.get_agent_utility(agent)
        print(f"Agent {agent.id} ({'Buyer' if agent.preference_schedule.is_buyer else 'Seller'}): {initial_utility:.2f}")

    # Calculate and print remaining trade opportunities and surplus
    remaining_trades = env.calculate_remaining_trade_opportunities()
    remaining_surplus = env.calculate_remaining_surplus()
    print(f"\nRemaining Trade Opportunities: {remaining_trades}")
    print(f"Remaining Surplus: {remaining_surplus:.2f}")

    # Plot the theoretical supply and demand curves
    env.plot_theoretical_supply_demand()