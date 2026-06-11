import time
import json
from typing import Dict, Any

class LLMService:
    @staticmethod
    def generate(prompt: str, system_instruction: str = "") -> str:
        """
        Simulates an LLM API call with a short latency delay.
        Parses context parameters in the prompt and returns dynamically formatted JSON payloads.
        """
        # Inject simulated LLM inference latency
        time.sleep(0.6)
        
        prompt_lower = prompt.lower()
        
        # Check if this is a Planning request
        if "generate 3 strategies" in prompt_lower or "planneragent" in prompt_lower:
            # We determine the context by parsing indicators in the prompt string
            water_level = 2.0
            if "water level: 2.8" in prompt_lower or "water_level: 2.85" in prompt_lower or "water_level: 3.2" in prompt_lower or "water level: 3.2" in prompt_lower:
                water_level = 3.2
            elif "water level: 4.2" in prompt_lower or "water_level: 4.2" in prompt_lower:
                water_level = 4.2
                
            unrest_level = 20.0
            if "unrest level: 82" in prompt_lower or "unrest_level: 82" in prompt_lower:
                unrest_level = 82.0
            elif "unrest level: 96" in prompt_lower or "unrest_level: 96" in prompt_lower:
                unrest_level = 96.0

            disruption = ""
            if "bridge_collapse" in prompt_lower or "bridge collapse" in prompt_lower:
                disruption = "bridge_collapse"
            elif "riot_outbreak" in prompt_lower:
                disruption = "riot_outbreak"
            elif "severe_downpour" in prompt_lower:
                disruption = "severe_downpour"

            # Formulate dynamic LLM output based on context metrics
            # Fastest
            fastest_cost = 180000.0
            fastest_duration = 2.5
            fastest_risk = 4.2
            fastest_coverage = 78.0
            fastest_steps = [
                {"step_number": 1, "action": "Deploy regional search & rescue speedboats directly to Sector bypass points", "resource": "Regional Rescue Boat Division", "estimated_duration_hours": 1.0},
                {"step_number": 2, "action": "Dispatch high-clearance military transport trucks through Sector Alpha lanes", "resource": "National Guard Logistics", "estimated_duration_hours": 1.0},
                {"step_number": 3, "action": "Execute direct tactical bypass sweeps to clear road debris blocking routes", "resource": "Tactical Road Sweeper Units", "estimated_duration_hours": 0.5}
            ]

            # Safest
            safest_cost = 210000.0
            safest_duration = 8.5
            safest_risk = 1.2
            safest_coverage = 98.0
            safest_steps = [
                {"step_number": 1, "action": "Establish secure cordoned staging zones and allocate armed police escort columns", "resource": "Metropolitan Security & Tactical Patrols", "estimated_duration_hours": 2.0},
                {"step_number": 2, "action": "Systematic sector-by-sector passenger bus evacuation along secure corridors", "resource": "Civil Transport Bus Lines", "estimated_duration_hours": 4.0},
                {"step_number": 3, "action": "Open three designated central school shelters with food, power, and medical teams", "resource": "Volunteers & Emergency Medical Corps", "estimated_duration_hours": 2.5}
            ]

            # Balanced
            balanced_cost = 110000.0
            balanced_duration = 5.0
            balanced_risk = 2.5
            balanced_coverage = 90.0
            balanced_steps = [
                {"step_number": 1, "action": "Launch quadcopter drones to map water channels and monitor crowd congregation movement", "resource": "UAV Aerial Intelligence Unit", "estimated_duration_hours": 1.0},
                {"step_number": 2, "action": "Deploy medium-clearance transport trucks along secondary pathways to coordinate egress", "resource": "Municipal Operations Command", "estimated_duration_hours": 2.5},
                {"step_number": 3, "action": "Erect local temporary safety zones and dispatch community liaison teams to coordinate assembly", "resource": "Liaison & Triage Division", "estimated_duration_hours": 1.5}
            ]

            # Injected Event adaptations
            if disruption == "bridge_collapse":
                fastest_duration += 3.0
                fastest_cost += 40000.0
                fastest_risk = 5.0
                fastest_steps.insert(1, {"step_number": 99, "action": "Reroute convoys through secondary dirt bypass due to Bridge Collapse", "resource": "Detour Scout Team", "estimated_duration_hours": 1.5})
                
                balanced_duration += 1.5
                balanced_cost += 20000.0
                balanced_risk = 3.5
                balanced_steps.insert(1, {"step_number": 99, "action": "Reroute ground transport through Sector C bridge detours", "resource": "State Patrol", "estimated_duration_hours": 1.0})
                
                safest_duration += 0.5
                
            elif disruption == "riot_outbreak" or unrest_level >= 80.0:
                # Security upgrades required for ground plans
                safest_steps[0] = {"step_number": 1, "action": "Establish secure staging points and deploy armed tactical military escorts", "resource": "Military Police & Local Police", "estimated_duration_hours": 2.0}
                safest_risk = 0.8
                
                balanced_steps.insert(1, {"step_number": 99, "action": "Deploy joint police escorts along transport pathways", "resource": "Riot Control Squads", "estimated_duration_hours": 1.0})
                balanced_duration += 1.0
                balanced_risk = max(1.0, balanced_risk - 0.5)
                balanced_cost += 15000.0
                
                fastest_risk = 4.8

            # Scale and re-index step numbers
            for name, steps in [("Fastest", fastest_steps), ("Safest", safest_steps), ("Balanced", balanced_steps)]:
                for idx, step in enumerate(steps):
                    step["step_number"] = idx + 1

            plans_payload = {
                "Fastest": {
                    "name": "Fastest",
                    "steps": fastest_steps,
                    "cost": fastest_cost,
                    "duration_hours": fastest_duration,
                    "risk_level": fastest_risk,
                    "coverage_percentage": fastest_coverage,
                    "description": "Prioritizes swift rescue operations utilizing high-speed vectors. Accepts elevated risk indices."
                },
                "Safest": {
                    "name": "Safest",
                    "steps": safest_steps,
                    "cost": safest_cost,
                    "duration_hours": safest_duration,
                    "risk_level": safest_risk,
                    "coverage_percentage": safest_coverage,
                    "description": "Prioritizes zero casualty parameters, systematic security escorts, and thorough sheltering. Increases deployment times."
                },
                "Balanced": {
                    "name": "Balanced",
                    "steps": balanced_steps,
                    "cost": balanced_cost,
                    "duration_hours": balanced_duration,
                    "risk_level": balanced_risk,
                    "coverage_percentage": balanced_coverage,
                    "description": "Blends drone surveillance, ground mobilization, and community triage centers. Moderate costs and durations."
                }
            }
            return json.dumps(plans_payload)

        # Check if this is a Decision/Ranking request
        elif "select optimal plan" in prompt_lower or "decisionagent" in prompt_lower:
            # Check if validation failures exist in prompt to trigger fallback escalation
            if '"valid": false' in prompt_lower and ("unrest_level: 96" in prompt_lower or "water_level: 4.2" in prompt_lower):
                # This indicates Variant C where validation failed due to severe budget or water breaches
                # Trigger failure escalation
                failure_payload = {
                    "status": "no_feasible_plan",
                    "selected_plan": "None",
                    "confidence": 0.0,
                    "confidence_factors": {"score": 0.0, "consistency": 0.0, "past_success": 0.0},
                    "ranking": [],
                    "justification": "All drafted strategies violate safety boundaries or budget ceilings. Extreme flooding (4.2m) combined with severe civil hostiles makes safe ground transit impossible.",
                    "rejected_plans": [
                        {"plan": "Fastest", "reason": "Water level exceeds 4m; vehicles will flood instantly."},
                        {"plan": "Safest", "reason": "Cost exceeds budget constraint ($220k limit) due to complex tactical escort requirements."},
                        {"plan": "Balanced", "reason": "Fails safety escorts under 96% riot index and uses unsafe ground vectors."}
                    ],
                    "why_this_plan": [],
                    "trade_offs": [],
                    "fallback": "Partial evacuation with delayed full deployment until escorts or air bridges are established."
                }
                return json.dumps(failure_payload)

            # Parse actual evaluated scores from prompt
            score_fast = 58.0
            score_safe = 68.0
            score_bal = 74.0
            try:
                start_marker = "evaluated plan options:"
                end_marker = "validation status:"
                start_idx = prompt_lower.find(start_marker)
                end_idx = prompt_lower.find(end_marker)
                if start_idx != -1 and end_idx != -1:
                    json_str = prompt[start_idx + len(start_marker):end_idx].strip()
                    evals = json.loads(json_str)
                    score_fast = evals.get("Fastest", {}).get("aggregate_score", score_fast)
                    score_safe = evals.get("Safest", {}).get("aggregate_score", score_safe)
                    score_bal = evals.get("Balanced", {}).get("aggregate_score", score_bal)
            except Exception:
                pass

            # Standard Decision logic parsing
            selected = "Balanced"
            justification = "The Balanced plan matches the current requirements, keeping costs low ($110k) while maintaining adequate safety and speed."
            why_this_plan = [
                "Lowest risk footprint without exceeding budget parameters.",
                "Drone reconnaissance provides real-time oversight of floodways.",
                "Within all budget limits."
            ]
            trade_offs = [
                "+2.5 hours delay compared to Fastest plan.",
                "Leaves 10% of outskirts area unmapped."
            ]

            # Context variables check
            confidence_val = 0.84 if selected == "Balanced" else 0.88
            score_factor = 0.74 if selected == "Balanced" else 0.79
            past_success_factor = 0.88 if selected == "Balanced" else 0.95

            if "bridge_collapse" in prompt_lower or "bridge collapse" in prompt_lower:
                selected = "Safest"
                justification = "Route instability increased risk for fast deployment. Safest routes avoid the collapsed bridge structure to guarantee convoy safety."
                why_this_plan = [
                    "Safest routes avoid the collapsed bridge structure.",
                    "Ensures evacuation convoy security.",
                    "Covers 98% of population."
                ]
                trade_offs = [
                    "Longest duration path (9.0 hours).",
                    "Requires deployment of full shelter assets."
                ]
                confidence_val = 0.89
                score_factor = 0.78
                past_success_factor = 0.96

            elif "riot_outbreak" in prompt_lower or "riot outbreak" in prompt_lower or "unrest_level: 95" in prompt_lower:
                selected = "Safest"
                justification = "Safest plan selected because the active riot outbreak (95% unrest) requires tactical security escorts to ensure safe transit of evacuation convoys."
                why_this_plan = [
                    "Deploys military police escorts to secure transit routes.",
                    "Minimizes casualty risk under active unrest (0.8/5.0).",
                    "Maintains maximum coverage of 98%."
                ]
                trade_offs = [
                    "Requires significant tactical resource allocation.",
                    "Longer duration than Fastest strategy."
                ]
                confidence_val = 0.91
                score_factor = 0.81
                past_success_factor = 0.97

            elif "severe_downpour" in prompt_lower or "severe downpour" in prompt_lower:
                selected = "Safest"
                justification = "Safest plan selected because torrential rainfall (130 mm/h) and high water level (3.9m) compromise secondary routes and ground assets."
                why_this_plan = [
                    "Safest corridors avoid vulnerable low-lying roads.",
                    "Includes specialized flood-response staging assets.",
                    "Mitigates increased transit risks."
                ]
                trade_offs = [
                    "Substantial delay in timeline completion.",
                    "Increases budget usage close to constraint limit."
                ]
                confidence_val = 0.86
                score_factor = 0.75
                past_success_factor = 0.92

            elif "water_level: 2.8" in prompt_lower or "water level: 2.8" in prompt_lower or "water_level: 3.2" in prompt_lower or "water level: 3.2" in prompt_lower or "safest strategy success rate" in prompt_lower:
                selected = "Safest"
                justification = "Safest plan selected because elevated flood heights (3.2m) and unrest (82%) require police escort columns to guarantee safety."
                why_this_plan = [
                    "Guarantees safety with joint armed police escorts.",
                    "Covers 98% of the affected population.",
                    "Reduces risk index to minimal levels (0.8/5.0)."
                ]
                trade_offs = [
                    "+6.0 hours delay compared to Fastest plan.",
                    "+$100,000 cost overhead."
                ]
                confidence_val = 0.88
                score_factor = 0.79
                past_success_factor = 0.95

            # The selected plan must always be Rank 1 on the leaderboard
            other_plans = [p for p in ["Fastest", "Safest", "Balanced"] if p != selected]
            # Sort the remaining plans by their scores descending
            other_plans.sort(key=lambda p: score_fast if p == "Fastest" else (score_safe if p == "Safest" else score_bal), reverse=True)

            ranking = [
                {"plan": selected, "score": score_safe if selected == "Safest" else (score_bal if selected == "Balanced" else score_fast), "rank": 1},
                {"plan": other_plans[0], "score": score_safe if other_plans[0] == "Safest" else (score_bal if other_plans[0] == "Balanced" else score_fast), "rank": 2},
                {"plan": other_plans[1], "score": score_safe if other_plans[1] == "Safest" else (score_bal if other_plans[1] == "Balanced" else score_fast), "rank": 3}
            ]

            decision_payload = {
                "status": "completed",
                "selected_plan": selected,
                "confidence": confidence_val,
                "confidence_factors": {
                    "score": score_factor,
                    "consistency": 0.90,
                    "past_success": past_success_factor
                },
                "ranking": ranking,
                "justification": justification,
                "rejected_plans": [
                    {"plan": "Fastest" if selected != "Fastest" else "Balanced", "reason": "Fastest plan carries extreme risk (4.2/5.0) which is unacceptable in this hazard profile." if selected != "Fastest" else "Balanced plan has lower speed density."},
                    {"plan": "Safest" if selected != "Safest" else "Balanced", "reason": "Safest plan carries a significant duration footprint (8.5 hours) which slows initial egress." if selected != "Safest" else "Balanced plan is selected."}
                ],
                "why_this_plan": why_this_plan,
                "trade_offs": trade_offs,
                "fallback": ""
            }
            return json.dumps(decision_payload)

        # Fallback default response
        return json.dumps({"text": "Inference output resolved."})
