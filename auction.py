from typing import List
import matplotlib.pyplot as plt
from environment import Environment, generate_agents
from ziagents import Order, Trade
from plotter import  analyze_and_plot_auction_results


class DoubleAuction:
    def __init__(self, environment: Environment, max_rounds: int):
        self.environment = environment
        self.max_rounds = max_rounds
        self.successful_trades: List[Trade] = []
        self.total_surplus_extracted = 0.0
        self.average_prices: List[float] = []

    def match_orders(self, bids: List[Order], asks: List[Order], round_num: int) -> List[Trade]:
        trades = []
        bids.sort(key=lambda x: x.price, reverse=True)  # Highest bids first
        asks.sort(key=lambda x: x.price)  # Lowest asks first

        while bids and asks and bids[0].price >= asks[0].price:
            bid = bids.pop(0)
            ask = asks.pop(0)
            trade_price = (bid.price + ask.price) / 2  # Midpoint price
            trade_quantity = min(bid.quantity, ask.quantity)
            trade = Trade(
                buyer_id=bid.agent_id,
                seller_id=ask.agent_id,
                quantity=trade_quantity,
                price=trade_price,
                buyer_value=bid.base_value,  # Use buyer's base value
                seller_cost=ask.base_cost,    # Use seller's base cost
                round=round_num               # Include the current round number
            )
            trades.append(trade)
        return trades



    def execute_trades(self, trades: List[Trade]):
        for trade in trades:
            buyer = self.environment.get_agent(trade.buyer_id)
            seller = self.environment.get_agent(trade.seller_id)

            # Use the buyer_value and seller_cost that were attached to the trade during order matching
            buyer_surplus = trade.buyer_value - trade.price
            seller_surplus = trade.price - trade.seller_cost

            if buyer_surplus < 0 or seller_surplus < 0:
                print(f"Trade rejected due to negative surplus: Buyer Surplus = {buyer_surplus}, Seller Surplus = {seller_surplus}")
                continue

            buyer.finalize_trade(trade)
            seller.finalize_trade(trade)
            self.total_surplus_extracted += buyer_surplus + seller_surplus
            self.average_prices.append(trade.price)
            self.successful_trades.append(trade)

            print(f"Executing trade: Buyer {buyer.id} - Surplus: {buyer_surplus:.2f}, Seller {seller.id} - Surplus: {seller_surplus:.2f}")


    def run_auction(self):
        for round_num in range(1, self.max_rounds + 1):
            print(f"\n=== Round {round_num} ===")

            # Generate bids from buyers
            bids = []
            for buyer in self.environment.buyers:
                if buyer.allocation.goods < buyer.preference_schedule.values.get(len(buyer.preference_schedule.values), 0):  # Check if the buyer can still buy
                    bid = buyer.generate_bid()
                    if bid:
                        bids.append(bid)
                        print(f"Buyer {buyer.id} bid: ${bid.price:.2f} for {bid.quantity} unit(s)")
                else:
                    print(f"Buyer {buyer.id} has reached maximum allocation of goods and cannot bid.")

            # Generate asks from sellers
            asks = []
            for seller in self.environment.sellers:
                if seller.allocation.goods > 0:  # Check if the seller has goods left to sell
                    ask = seller.generate_bid()
                    if ask:
                        asks.append(ask)
                        print(f"Seller {seller.id} ask: ${ask.price:.2f} for {ask.quantity} unit(s)")
                else:
                    print(f"Seller {seller.id} has sold all goods and cannot ask.")

            trades = self.match_orders(bids, asks, round_num)  # Pass the round number here
            if trades:
                self.execute_trades(trades)

        self.summarize_results()



    def summarize_results(self):
        total_trades = len(self.successful_trades)
        avg_price = sum(self.average_prices) / total_trades if total_trades > 0 else 0

        print(f"\n=== Auction Summary ===")
        print(f"Total Successful Trades: {total_trades}")
        print(f"Total Surplus Extracted: {self.total_surplus_extracted:.2f}")
        print(f"Average Price: {avg_price:.2f}")


        # Compare theoretical and practical surplus
        ce_price, ce_quantity, theoretical_buyer_surplus, theoretical_seller_surplus, theoretical_total_surplus = self.environment.calculate_equilibrium()
        print(f"\n=== Theoretical vs. Practical Surplus ===")
        print(f"Theoretical Total Surplus: {theoretical_total_surplus:.2f}")
        print(f"Practical Total Surplus: {self.total_surplus_extracted:.2f}")
        print(f"Difference (Practical - Theoretical): {self.total_surplus_extracted - theoretical_total_surplus:.2f}")

        # Detecting and explaining potential negative surplus
        if self.total_surplus_extracted < 0:
            print(f"Warning: Negative practical surplus detected. Possible causes include:")
            print(f"  1. Mismatch between bid/ask values and agent utilities.")
            print(f"  2. Overestimated initial utilities.")
            print(f"  3. High frictions or spread preventing trades.")

def run_market_simulation(num_buyers: int, num_sellers: int, num_units: int, buyer_base_value: int, seller_base_value: int, spread: float, max_rounds: int):
    # Generate test agents
    agents = generate_agents(num_agents=num_buyers + num_sellers, num_units=num_units, buyer_base_value=buyer_base_value, seller_base_value=seller_base_value, spread=spread)
    
    # Create the environment
    env = Environment(agents=agents)

    # Print initial market state
    env.print_market_state()

    # Calculate and print initial utilities
    print("\nInitial Utilities:")
    for agent in env.agents:
        initial_utility = env.get_agent_utility(agent)
        print(f"Agent {agent.id} ({'Buyer' if agent.preference_schedule.is_buyer else 'Seller'}): {initial_utility:.2f}")

    # Run the auction
    auction = DoubleAuction(environment=env, max_rounds=max_rounds)
    auction.run_auction()

    # Analyze the auction results and plot
    analyze_and_plot_auction_results(auction, env)


if __name__ == "__main__":
    # Generate test agents
    num_buyers = 50
    num_sellers = 50
    spread = 0.5
    agents = generate_agents(num_agents=num_buyers + num_sellers, num_units=5, buyer_base_value=100, seller_base_value=90, spread=spread)
    
    # Create the environment
    env = Environment(agents=agents)

    # Print initial market state
    env.print_market_state()

    # Calculate and print initial utilities
    print("\nInitial Utilities:")
    for agent in env.agents:
        initial_utility = env.get_agent_utility(agent)
        print(f"Agent {agent.id} ({'Buyer' if agent.preference_schedule.is_buyer else 'Seller'}): {initial_utility:.2f}")

    # Run the auction
    auction = DoubleAuction(environment=env, max_rounds=50)
    auction.run_auction()

    # Analyze and plot results
    analyze_and_plot_auction_results(auction, env)
