import numpy as np
from typing import Dict

class PureMonteCarloSimulator:
    """
    Seismic Risk Monte Carlo Engine
    Rebuilt strictly from Excel logic (Normal Distribution MDR)
    """
    
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations

    def run_simulation(self, 
                       total_value: float, 
                       a_coeff: float, 
                       retention_rate: float,
                       degree: str = "III") -> Dict:
        
        # New Discrete Uniform Model extracted from mount carlo (1).xlsx
        # Alpha is chosen from deciles 0% to 100%
        alpha_steps = np.arange(0, 1.1, 0.1)
        
        # Random iterations for damage multipliers
        alphas = np.random.choice(alpha_steps, size=self.iterations)
        
        # Gross Damage Ratio = Alpha * Acceleration A
        # (This matches 'MAX_DAMAGE' logic where A is the ceiling)
        ratios = alphas * a_coeff
        
        # Calculate Losses
        gross_losses = ratios * total_value
        net_losses = gross_losses * retention_rate
        
        # Statistics
        results = {
            "kpis": {
                "aal_gross": float(np.mean(gross_losses)),
                "aal_net": float(np.mean(net_losses)),
                "min": float(np.min(gross_losses)),
                "max": float(np.max(gross_losses)),
                "std": float(np.std(gross_losses)),
                "pml_95_gross": float(np.percentile(gross_losses, 95)),
                "pml_95_net": float(np.percentile(net_losses, 95)),
                "p10": float(np.percentile(gross_losses, 10)),
                "p50": float(np.percentile(gross_losses, 50)),
                "p90": float(np.percentile(gross_losses, 90))
            },
            "distribution": {
                "bins": 50,
                "histogram": np.histogram(gross_losses, bins=50)[0].tolist(),
                "labels": np.histogram(gross_losses, bins=50)[1].tolist()
            },
            "ep_curve": {
                "return_periods": [10, 20, 50, 100, 200, 500],
                "gross": [float(np.percentile(gross_losses, 100 - (100/rp))) for rp in [10, 20, 50, 100, 200, 500]],
                "net": [float(np.percentile(net_losses, 100 - (100/rp))) for rp in [10, 20, 50, 100, 200, 500]]
            }
        }
        
        return results

# Mandatory instance for backend/main.py
monte_carlo_engine = PureMonteCarloSimulator()
