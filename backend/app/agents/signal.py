from app.models import TaskState, ScenarioMetrics
from app.agents.base import BaseAgent
from app import config

class SignalAgent(BaseAgent):
    name: str = "SignalAgent"

    def run(self, state: TaskState, variant: str = None) -> None:
        intent = "Generate simulated weather and social telemetry based on selected scenario variant"
        action = "simulate_environment"
        
        # Load preset parameters based on variant
        preset_key = variant if variant in config.SCENARIO_VARIANTS else "variant_a"
        preset = config.SCENARIO_VARIANTS[preset_key]
        
        metrics = ScenarioMetrics(
            rainfall=preset["rainfall"],
            water_level=preset["water_level"],
            crowd_size=preset["crowd_size"],
            unrest_level=preset["unrest_level"],
            description=preset["description"],
            location=preset["location"]
        )
        state.scenario = metrics
        state.metadata["scenario_variant"] = preset_key
        
        reasoning = "Acquiring real-time rainfall sensors, river gauges, crowd estimates, and social media agitation signals."
        impact = "Mapped incident telemetry to scenario state"
        self.log(state, intent, action, reasoning, impact, metrics.dict())
