from app.models import TaskState, PlanEvaluation
from app.agents.base import BaseAgent
from app import config

class EvaluatorAgent(BaseAgent):
    name: str = "EvaluatorAgent"

    def run(self, state: TaskState) -> None:
        # Evolve intent based on whether evaluations already exist (re-scoring pass)
        if state.evaluations:
            intent = "re-scoring refined plan parameters"
        else:
            intent = "evaluating plan parameters"

        action = "evaluate_plans"

        if not state.plans:
            raise ValueError("No action plans found in TaskState for EvaluatorAgent.")

        evaluations = {}
        best_score = 0.0
        best_plan_name = ""

        for name, plan in state.plans.items():
            # Time Score: Duration = 2.0h -> 100, 10.0h -> 20.
            time_score = max(0.0, min(100.0, 100.0 - (plan.duration_hours - 2.0) * 10.0))
            
            # Risk Score: Risk Level = 1.0 -> 100, 5.0 -> 0.
            risk_score = max(0.0, min(100.0, 100.0 - (plan.risk_level - 1.0) * 25.0))
            
            # Cost Score: Cost = 50,000 -> 100, 250,000 -> 20.
            cost_score = max(0.0, min(100.0, 100.0 - (plan.cost - 50000.0) * (80.0 / 200000.0)))
            
            # Coverage Score:
            coverage_score = plan.coverage_percentage

            # Weighted aggregate score
            aggregate_score = round(
                config.WEIGHT_TIME * time_score +
                config.WEIGHT_RISK * risk_score +
                config.WEIGHT_COST * cost_score +
                config.WEIGHT_COVERAGE * coverage_score,
                2
            )

            evaluations[name] = PlanEvaluation(
                plan_name=name,
                time_score=round(time_score, 1),
                risk_score=round(risk_score, 1),
                cost_score=round(cost_score, 1),
                coverage_score=round(coverage_score, 1),
                aggregate_score=aggregate_score,
                feedback=""
            )

            if aggregate_score > best_score:
                best_score = aggregate_score
                best_plan_name = name

        # Collaborative feedback loop condition
        feedback_str = ""
        if best_score < config.TARGET_SCORE_THRESHOLD:
            feedback_str = (
                f"The highest ranking strategy '{best_plan_name}' (score: {best_score}) is below "
                f"the target threshold of {config.TARGET_SCORE_THRESHOLD}. Action: Suggesting the planner "
                f"boost coverage parameters by implementing remote communication networks."
            )
            evaluations[best_plan_name].feedback = feedback_str

        state.evaluations = evaluations
        
        # Check if fastest plan is unsafe under current conditions
        fastest_plan = state.plans.get("Fastest")
        if fastest_plan and fastest_plan.risk_level > 3.5:
            reasoning = "Fastest plan unsafe under current conditions; comparing safety margins."
        else:
            reasoning = "Analyzing trade-offs between speed, cost, safety, and population coverage."

        impact = "Calculated multicriteria score matrices"
        self.log(state, intent, action, reasoning, impact, {k: v.dict() for k, v in evaluations.items()})
