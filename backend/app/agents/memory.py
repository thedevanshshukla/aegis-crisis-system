import math
from app.models import TaskState, MemoryNarrative
from app.agents.base import BaseAgent
from app import config

class MemoryAgent(BaseAgent):
    name: str = "MemoryAgent"

    def run(self, state: TaskState) -> None:
        intent = "consulting empirical memory library"
        action = "retrieve_past_cases"

        scenario = state.scenario
        if not scenario:
            raise ValueError("No scenario telemetry found in TaskState for MemoryAgent.")

        best_case = None
        min_distance = float('inf')

        scales = {
            "rainfall": 50.0,
            "water_level": 2.0,
            "crowd_size": 1000.0,
            "unrest_level": 50.0
        }

        # Calculate similarity distance
        for case in config.HISTORICAL_CASES:
            case_metrics = case["metrics"]
            dist = math.sqrt(
                ((scenario.rainfall - case_metrics["rainfall"]) / scales["rainfall"]) ** 2 +
                ((scenario.water_level - case_metrics["water_level"]) / scales["water_level"]) ** 2 +
                ((scenario.crowd_size - case_metrics["crowd_size"]) / scales["crowd_size"]) ** 2 +
                ((scenario.unrest_level - case_metrics["unrest_level"]) / scales["unrest_level"]) ** 2
            )
            if dist < min_distance:
                min_distance = dist
                best_case = case

        threshold = 1.8
        
        if best_case and min_distance < threshold:
            rec_plan = best_case["selected_plan"]
            success_rate = best_case["success_rate"]
            
            # Boost the corresponding plan score
            if rec_plan in state.evaluations:
                original_score = state.evaluations[rec_plan].aggregate_score
                boost = 5.0
                state.evaluations[rec_plan].aggregate_score = round(original_score + boost, 2)
                state.evaluations[rec_plan].feedback += f" [Historical Boost: +{boost} from {best_case['id']}]"
                
            impact_desc = (
                f"Empirical matching found close correlation with {best_case['id']}. "
                f"{rec_plan} strategy success rate of {int(success_rate * 100)}% verified. "
                f"Aggregate score boosted by +5.0."
            )
            
            narrative = MemoryNarrative(
                memory_used=True,
                reference_case=f"{best_case['id']}: {best_case['description']}",
                impact=impact_desc
            )
        else:
            narrative = MemoryNarrative(
                memory_used=False,
                reference_case="N/A",
                impact="Current crisis parameters show unique signature. No similar historical cases exceed confidence threshold."
            )

        state.metadata["memory_narrative"] = narrative
        
        reasoning = "Matching current disaster profile against database cases (e.g., CASE-101) to boost strategy confidence."
        impact = "Queried precedent database and applied confidence scoring boosts"

        self.log(state, intent, action, reasoning, impact, narrative.dict())
