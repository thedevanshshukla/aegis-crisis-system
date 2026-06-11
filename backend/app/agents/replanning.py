from app.models import TaskState, PlanStep
from app.agents.base import BaseAgent

class ReplanningAgent(BaseAgent):
    name: str = "ReplanningAgent"

    def run(self, state: TaskState, event_type: str) -> None:
        intent = "injecting new incident disruption parameters"
        action = "inject_disruption"

        if not state.plans or not state.scenario:
            raise ValueError("Incomplete state. Plans and Scenario must exist before injecting disruptions.")

        state.disruption_event = event_type
        state.performance_metrics.replans_triggered += 1
        adjustments = {}

        if event_type == "bridge_collapse":
            # Fastest
            p_fast = state.plans["Fastest"]
            p_fast.duration_hours += 3.0
            p_fast.cost += 40000.0
            p_fast.risk_level = 5.0
            p_fast.description += " Detour added due to highway bridge collapse."
            p_fast.steps.insert(1, PlanStep(step_number=99, action="Reroute convoys through secondary dirt bypass due to Bridge Collapse", resource="Detour Scout Team", estimated_duration_hours=1.5))
            for i, s in enumerate(p_fast.steps): s.step_number = i + 1

            # Balanced
            p_bal = state.plans["Balanced"]
            p_bal.duration_hours += 1.5
            p_bal.cost += 20000.0
            p_bal.risk_level = 3.5
            p_bal.description += " Detour added due to highway bridge collapse."
            p_bal.steps.insert(1, PlanStep(step_number=99, action="Reroute ground transport through Sector C bridge detours", resource="State Patrol", estimated_duration_hours=1.0))
            for i, s in enumerate(p_bal.steps): s.step_number = i + 1

            # Safest
            p_safe = state.plans["Safest"]
            p_safe.duration_hours += 0.5

            adjustments = {
                "Fastest": {"duration": "+3.0h", "cost": "+$40,000", "risk": "5.0"},
                "Balanced": {"duration": "+1.5h", "cost": "+$20,000", "risk": "3.5"},
                "Safest": {"duration": "+0.5h"}
            }

        elif event_type == "riot_outbreak":
            state.scenario.unrest_level = 95.0
            state.scenario.crowd_size = 2500
            state.scenario.description += " Outbreak of civil rioting in primary transit grid."

            for name, plan in state.plans.items():
                if name == "Fastest":
                    plan.risk_level = 4.8
                elif name == "Balanced":
                    plan.risk_level = 3.8

            adjustments = {
                "scenario": {"unrest_level": "95.0", "crowd_size": "2500"},
                "Fastest": {"risk": "4.8"},
                "Balanced": {"risk": "3.8"}
            }

        elif event_type == "severe_downpour":
            state.scenario.rainfall = 130.0
            state.scenario.water_level = 3.9
            state.scenario.description += " Microburst downpour escalates runoff rates."

            state.plans["Fastest"].risk_level = 5.0
            state.plans["Fastest"].duration_hours += 2.0
            state.plans["Balanced"].risk_level = 4.0
            state.plans["Balanced"].duration_hours += 1.0
            state.plans["Safest"].duration_hours += 1.5

            adjustments = {
                "scenario": {"rainfall": "130.0 mm/h", "water_level": "3.9m"},
                "Fastest": {"risk": "5.0", "duration": "+2.0h"},
                "Balanced": {"risk": "4.0", "duration": "+1.0h"},
                "Safest": {"duration": "+1.5h"}
            }
        else:
            raise ValueError(f"Unknown disruption event type: {event_type}")

        reasoning = "Adapting scenario parameters in response to active infrastructure or crowd disruption anomalies."
        impact = "Modified plan properties and triggered replanning cycle"
        
        self.log(state, intent, action, reasoning, impact, {
            "disruption": event_type,
            "adjustments": adjustments
        })
