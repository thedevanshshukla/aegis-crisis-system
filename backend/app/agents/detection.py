from app.models import TaskState, DetectionOutput
from app.agents.base import BaseAgent

class DetectionAgent(BaseAgent):
    name: str = "DetectionAgent"

    def run(self, state: TaskState) -> None:
        intent = "Evaluate threat boundaries and compute normalized Crisis Severity Index"
        action = "detect_crisis"
        
        scenario = state.scenario
        if not scenario:
            raise ValueError("No scenario telemetry found in TaskState for DetectionAgent.")

        triggers = []
        crisis_detected = False
        
        # Check boundary breaches
        if scenario.rainfall > 50.0:
            triggers.append(f"Rainfall limits crossed: {scenario.rainfall} mm/h (limit: 50.0)")
            crisis_detected = True
        if scenario.water_level > 2.2:
            triggers.append(f"Water level safety margin breached: {scenario.water_level}m (limit: 2.2)")
            crisis_detected = True
        if scenario.crowd_size > 800:
            triggers.append(f"Crowd threshold exceeded: {scenario.crowd_size} (limit: 800)")
            crisis_detected = True
        if scenario.unrest_level > 50.0:
            triggers.append(f"Unrest aggression limit breached: {scenario.unrest_level}% (limit: 50.0)")
            crisis_detected = True

        # Crisis Severity Index Calculation (Normalized across 4 elements)
        norm_rain = min(1.0, scenario.rainfall / 150.0)
        norm_water = min(1.0, scenario.water_level / 5.0)
        norm_crowd = min(1.0, scenario.crowd_size / 4000.0)
        norm_unrest = min(1.0, scenario.unrest_level / 100.0)
        severity_index = round((norm_rain + norm_water + norm_crowd + norm_unrest) / 4.0, 2)

        # Threat classification level resolving
        if severity_index >= 0.70 or scenario.water_level >= 4.0 or scenario.unrest_level >= 90.0:
            level = "CRITICAL"
            alert_level = "RED"
        elif severity_index >= 0.40 or scenario.water_level >= 2.5 or scenario.unrest_level >= 60.0:
            level = "ELEVATED"
            alert_level = "AMBER"
        else:
            level = "NORMAL"
            alert_level = "GREEN"

        reasoning = "Calculating multi-hazard risk index; alert level determined by flood heights and unrest escalation."
        
        detection = DetectionOutput(
            crisis_detected=crisis_detected,
            alert_level=alert_level,
            severity_index=severity_index,
            level=level,
            triggers=triggers,
            reasoning=reasoning
        )
        
        state.detection = detection
        impact = "Computed severity score and resolved threat classification"
        self.log(state, intent, action, reasoning, impact, detection.dict())
