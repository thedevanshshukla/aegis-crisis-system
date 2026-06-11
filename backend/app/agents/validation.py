from app.models import TaskState, ValidationOutput
from app.agents.base import BaseAgent
from app import config

class ValidationAgent(BaseAgent):
    name: str = "ValidationAgent"

    def run(self, state: TaskState) -> None:
        intent = "auditing plan constraints compliance"
        action = "validate_plans"

        if not state.plans:
            raise ValueError("No action plans found in TaskState for ValidationAgent.")

        issues = []
        warnings = []

        scenario = state.scenario
        unrest_level = scenario.unrest_level if scenario else 0.0

        for name, plan in state.plans.items():
            # Constraint 1: Budget limit audit
            if plan.cost > config.MAX_BUDGET:
                issues.append(f"Plan '{name}' cost (${plan.cost:,.2f}) exceeds MAX_BUDGET constraint of ${config.MAX_BUDGET:,.2f}.")

            # Constraint 2: Risk limit audit
            if plan.risk_level > config.MAX_RISK:
                issues.append(f"Plan '{name}' risk level ({plan.risk_level}) exceeds MAX_RISK constraint of {config.MAX_RISK}.")

            # Constraint 3: Coverage limit audit
            if plan.coverage_percentage < config.MIN_COVERAGE:
                issues.append(f"Plan '{name}' coverage ({plan.coverage_percentage}%) falls below MIN_COVERAGE constraint of {config.MIN_COVERAGE}%.")

            # Escort Check: If unrest > 70%, ground operations require tactical protection
            if unrest_level > 70.0:
                has_escort = False
                uses_ground = False
                for step in plan.steps:
                    action_lower = step.action.lower()
                    resource_lower = step.resource.lower()
                    if "bus" in action_lower or "truck" in action_lower or "ground" in action_lower or any(ind in action_lower for ind in ["transport", "evacuation"]):
                        uses_ground = True
                    if "escort" in action_lower or "police" in resource_lower or "tactical" in resource_lower or "guard" in resource_lower:
                        has_escort = True
                
                if uses_ground and not has_escort:
                    issues.append(
                        f"Plan '{name}' uses ground evacuation under high unrest ({unrest_level}%) "
                        f"without tactical or police escort squads."
                    )

            # Constraint 4: Flood limit safety (Water level > 4.0m blocks ground transit)
            if scenario and scenario.water_level > 4.0:
                uses_ground_transit = False
                for step in plan.steps:
                    action_lower = step.action.lower()
                    if "bus" in action_lower or "truck" in action_lower or "ground" in action_lower or any(ind in action_lower for ind in ["transport", "evacuation"]):
                        uses_ground_transit = True
                if uses_ground_transit:
                    issues.append(f"Plan '{name}' schedules ground transport which is blocked under catastrophic water level ({scenario.water_level}m > 4.0m limit).")

            # Constraint 5: Severe storm safety (Precipitation > 100 mm/h grounds flight rescue assets)
            if scenario and scenario.rainfall > 100.0:
                uses_air_transit = False
                for step in plan.steps:
                    action_lower = step.action.lower()
                    if "helicopter" in action_lower or "air" in action_lower:
                        uses_air_transit = True
                if uses_air_transit:
                    issues.append(f"Plan '{name}' uses helicopter rescue assets which are grounded under storm precipitation ({scenario.rainfall} mm/h > 100 mm/h limit).")

        valid = len(issues) == 0
        validation_res = ValidationOutput(
            valid=valid,
            issues=issues,
            warnings=warnings
        )

        # Update performance stats on failures
        if not valid:
            state.performance_metrics.validation_failures += 1

        state.validation = validation_res
        
        reasoning = "Checking budget limit ($220k), risk ceilings, and escort rules for unrest areas."
        impact = "Audited plan boundaries and marked compliance flags"

        self.log(state, intent, action, reasoning, impact, validation_res.dict())
