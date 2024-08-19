import random
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field
from typing import Dict

class PreferenceSchedule(BaseModel):
    values: Dict[int, float] = Field(..., description="Dictionary mapping quantity to value/cost")
    is_buyer: bool = Field(..., description="True if this is a buyer's schedule, False for seller")

    @classmethod
    def generate(cls, is_buyer: bool, num_units: int, base_value: float, noise_factor: float = 0.1):
        values = {}
        current_value = base_value
        for i in range(1, num_units + 1):
            noise = random.uniform(-noise_factor, noise_factor) * current_value
            new_value = max(0, current_value + noise)
            print(f"Unit {i}: base_value={current_value:.2f}, noise={noise:.2f}, new_value={new_value:.2f}")

            if is_buyer:
                # Ensure monotonic decreasing values
                if i > 1:
                    new_value = min(new_value, values[i-1])
                current_value *= random.uniform(0.9, 1.0)  # Decreasing marginal utility
            else:
                # Ensure monotonic increasing costs
                if i > 1:
                    new_value = max(new_value, values[i-1])
                current_value *= random.uniform(1.0, 1.1)  # Increasing marginal cost

            values[i] = new_value
        
        return cls(values=values, is_buyer=is_buyer)

    def get_value(self, quantity: int) -> float:
        return self.values.get(quantity, 0.0)

    def plot_schedule(self):
        """Plot the preference schedule."""
        quantities = list(self.values.keys())
        values = list(self.values.values())
        
        plt.figure(figsize=(10, 6))
        plt.plot(quantities, values, marker='o', linestyle='-', color='blue' if self.is_buyer else 'red')
        plt.xlabel('Quantity')
        plt.ylabel('Value/Cost')
        plt.title(f'{"Buyer" if self.is_buyer else "Seller"} Preference Schedule')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    # Generate and plot buyer and seller schedules
    buyer_schedule = PreferenceSchedule.generate(is_buyer=True, num_units=10, base_value=100, noise_factor=0.1)
    buyer_schedule.plot_schedule()

    seller_schedule = PreferenceSchedule.generate(is_buyer=False, num_units=10, base_value=50, noise_factor=0.1)
    seller_schedule.plot_schedule()

    # Test edge cases and plot
    empty_schedule = PreferenceSchedule.generate(is_buyer=True, num_units=0, base_value=100, noise_factor=0.1)
    empty_schedule.plot_schedule()

    high_value_schedule = PreferenceSchedule.generate(is_buyer=False, num_units=5, base_value=10000, noise_factor=0.5)
    high_value_schedule.plot_schedule()

    low_noise_schedule = PreferenceSchedule.generate(is_buyer=True, num_units=5, base_value=10, noise_factor=0.01)
    low_noise_schedule.plot_schedule()
