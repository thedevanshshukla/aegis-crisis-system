import json
from app.models import TaskState, ActionPlan, PlanStep
from app.agents.base import BaseAgent
from app.agents.llm import LLMService
from typing import List

class PlannerAgent(BaseAgent):
    name: str = "PlannerAgent"

    def run(self, state: TaskState, validation_issues: List[str] = None, evaluator_feedback: str = None) -> None:
        if validation_issues:
            intent = "refining plan due to budget/safety violations"
        elif evaluator_feedback:
            intent = "refining plan due to evaluator feedback"
        else:
            intent = "initial plan generation"

        action = "generate_plans"

        scenario = state.scenario
        if not scenario:
            raise ValueError("No scenario telemetry found in TaskState for PlannerAgent.")

        # 2. Compile prompt for LLM planning agent
        prompt = f"""
        System Instruction: You are the AEGIS PlannerAgent. You must generate exactly three strategy options for the crisis:
        - 'Fastest': Swift air-ground routing, higher risks.
        - 'Safest': Cordoned paths, armed escorts if unrest index > 70%, shelter networks.
        - 'Balanced': Triage safe zones, drone grids, ground patrols.
        
        Current Scenario Metrics:
        - rainfall: {scenario.rainfall} mm/h
        - water_level: {scenario.water_level}m
        - crowd_size: {scenario.crowd_size} persons
        - unrest_level: {scenario.unrest_level}%
        - active_disruption: {state.disruption_event or "None"}
        
        Feedback Signals:
        - validation_issues: {validation_issues or "None"}
        - evaluator_feedback: {evaluator_feedback or "None"}
        
        Return a strict JSON object mapping 'Fastest', 'Safest', and 'Balanced' strategies.
        Each plan must specify: steps, cost, duration_hours, risk_level (1.0 to 5.0), and coverage_percentage.
        """

        # 3. Request LLM Inference
        llm_response = LLMService.generate(prompt, system_instruction="AEGIS Strategic Planning Protocol")
        
        # 4. Parse and serialize back to Pydantic objects
        try:
            plans_dict = json.loads(llm_response)
            
            plans = {}
            for name in ["Fastest", "Safest", "Balanced"]:
                plan_data = plans_dict[name]
                steps = [PlanStep(**step) for step in plan_data["steps"]]
                plans[name] = ActionPlan(
                    name=plan_data["name"],
                    steps=steps,
                    cost=plan_data["cost"],
                    duration_hours=plan_data["duration_hours"],
                    risk_level=plan_data["risk_level"],
                    coverage_percentage=plan_data["coverage_percentage"],
                    description=plan_data["description"]
                )
            
            state.plans = plans
            
        except Exception as e:
            raise RuntimeError(f"Error parsing Planner LLM JSON: {e}. Output was: {llm_response}")

        if validation_issues:
            reasoning = "High flood level requires safer planning. Planner adjusting parameters based on validation failures."
            impact = "Refined strategy variants to meet system rules"
        elif evaluator_feedback:
            reasoning = "High flood level requires safer planning. Planner adjusting coverage density based on evaluator feedback."
            impact = "Refined strategy variants based on evaluator scoring"
        else:
            reasoning = "Evolving strategic routes; water level and crowd unrest require secure air/ground transit variations."
            impact = "Formulated 3 candidate response strategies"

        self.log(state, intent, action, reasoning, impact, {
            "prompt_sent": prompt,
            "llm_response": plans_dict
        })
