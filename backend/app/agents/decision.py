import json
from app.models import TaskState, DecisionOutput, ConfidenceFactors, RejectedPlan, MemoryNarrative, PlanRank
from app.agents.base import BaseAgent
from app.agents.llm import LLMService
from app import config

class DecisionAgent(BaseAgent):
    name: str = "DecisionAgent"

    def run(self, state: TaskState) -> None:
        intent = "resolving strategic recommendation"
        action = "select_best_plan"

        if not state.evaluations:
            raise ValueError("No plan evaluations found in TaskState for DecisionAgent.")

        # Serialize current context to compile prompt
        evals_summary = {k: v.dict() for k, v in state.evaluations.items()}
        validation_status = state.validation.dict() if state.validation else {"valid": True, "issues": []}
        memory_narrative = state.metadata.get("memory_narrative")
        
        # Compile prompt
        prompt = f"""
        System Instruction: You are the AEGIS DecisionAgent. Your job is to select the best plan based on the multicriteria evaluations and validation compliance audits.
        
        Evaluated Plan Options:
        {json.dumps(evals_summary, indent=2)}
        
        Validation Status:
        {json.dumps(validation_status, indent=2)}
        
        Memory Precedent Narrative:
        {json.dumps(memory_narrative.dict() if memory_narrative else {}, indent=2)}
        
        Current Telemetry Metrics:
        - rainfall: {state.scenario.rainfall if state.scenario else 0} mm/h
        - water_level: {state.scenario.water_level if state.scenario else 0}m
        - crowd_size: {state.scenario.crowd_size if state.scenario else 0}
        - unrest_level: {state.scenario.unrest_level if state.scenario else 0}%
        - active_disruption: {state.disruption_event or "None"}
        
        If all plans fail validation (e.g. costs exceed $220k budget ceiling or safety limits breached) and cannot be corrected, return 'status': 'no_feasible_plan', and supply a 'fallback' text: 'Partial evacuation with delayed full deployment until escorts or air bridges are established.'.
        Otherwise return 'status': 'completed' and select the highest ranking valid plan.
        Provide structured ranking list, rejected plans list, explainability bullet list 'why_this_plan', and 'trade_offs' list.
        """

        # Request LLM Inference
        llm_response = LLMService.generate(prompt, system_instruction="AEGIS Action Resolution Logic")
        
        try:
            res = json.loads(llm_response)
            
            # Map status code to task state
            if res.get("status") == "no_feasible_plan":
                state.status = "no_feasible_plan"
                state.fallback = res.get("fallback")
            else:
                state.status = "completed"
                state.fallback = None
                
            # Serialize ranking
            ranking = [PlanRank(**rank_item) for rank_item in res.get("ranking", [])]
            
            # Serialize rejected plans
            rejected_plans = [RejectedPlan(**rej_item) for rej_item in res.get("rejected_plans", [])]
            
            decision = DecisionOutput(
                selected_plan=res.get("selected_plan", "None"),
                confidence=res.get("confidence", 0.0),
                confidence_factors=ConfidenceFactors(**res.get("confidence_factors", {"score": 0.0, "consistency": 0.0, "past_success": 0.0})),
                ranking=ranking,
                justification=res.get("justification", "All plans violated system bounds."),
                rejected_plans=rejected_plans,
                memory_narrative=memory_narrative if memory_narrative else MemoryNarrative(memory_used=False),
                why_this_plan=res.get("why_this_plan", []),
                trade_offs=res.get("trade_offs", [])
            )
            
            if not state.original_decision:
                state.original_decision = decision
            state.current_decision = decision
            
        except Exception as e:
            raise RuntimeError(f"Error parsing Decision LLM JSON: {e}. Output was: {llm_response}")

        if state.status == "no_feasible_plan":
            reasoning = "System limits exceeded. No feasible plan found. Triggering fallback escalation protocol."
            impact = "Halted standard deployment; escalated to fallback procedures"
        else:
            reasoning = "Resolving ranking based on audit compliance, memory boosts, and multicriteria scoring."
            impact = "Resolved ranking leaderboard and selected optimal response plan"

        self.log(state, intent, action, reasoning, impact, {
            "prompt_sent": prompt,
            "llm_response": res
        })
