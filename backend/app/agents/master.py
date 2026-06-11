import time
import asyncio
from app.models import TaskState, PerformanceSummary, validate_state, ScenarioMetrics
from app.agents.base import BaseAgent
from app.agents.signal import SignalAgent
from app.agents.detection import DetectionAgent
from app.agents.planner import PlannerAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.validation import ValidationAgent
from app.agents.memory import MemoryAgent
from app.agents.decision import DecisionAgent
from app.agents.replanning import ReplanningAgent
from app import config

class MasterAgent(BaseAgent):
    name: str = "MasterAgent"

    async def wait_for_resume_signal(self, state: TaskState, start_time: float):
        """Asynchronously wait while execution_mode is paused, checking for timeout."""
        while state.execution_mode == "paused":
            if time.time() - start_time > 15.0:
                state.status = "stopped"
                self.log(state, "Orchestrate multi-agent decision flow", "timeout_check", "Execution halted due to timeout safety limit.", "Halted system run", {})
                break
            await asyncio.sleep(0.3)

    async def check_stopped(self, state: TaskState) -> bool:
        """Check if execution was explicitly stopped."""
        if state.status == "stopped":
            self.log(state, "Orchestrate multi-agent decision flow", "stop_execution", "Execution terminated by manual user stop command.", "Halted system run", {})
            return True
        return False

    def check_timeout_and_validate(self, state: TaskState, start_time: float) -> bool:
        """Audits state consistency and halts execution if timeout threshold is crossed."""
        # Validate consistency of state
        validate_state(state)
        # Check timeout limit
        if time.time() - start_time > 15.0:
            state.status = "stopped"
            self.log(state, "Orchestrate multi-agent decision flow", "timeout_check", "Execution halted due to timeout safety limit.", "Halted system run", {})
            return True
        return False

    async def run_async(self, state: TaskState, variant: str = None) -> None:
        """Runs the complete multi-agent pipeline asynchronously."""
        intent = "Orchestrate multi-agent decision flow"
        action = "orchestrate_decision_flow"
        reasoning = "Coordinating sequential cognitive agents and feedback loops to resolve optimal response strategy."
        
        start_time = time.time()

        # Reset logs and state structure for fresh run
        state.logs = []
        state.original_decision = None
        state.current_decision = None
        state.disruption_event = None
        state.fallback = None
        state.performance_metrics = PerformanceSummary(
            agents_executed=0,
            iterations=1,
            validation_failures=0,
            replans_triggered=0
        )
        state.status = "running"
        
        self.log(state, intent, action, reasoning, "Initiating deliberative multi-agent cognitive simulation...", {})

        # --- STEP 1: SIGNAL GENERATION ---
        await self.wait_for_resume_signal(state, start_time)
        if await self.check_stopped(state) or self.check_timeout_and_validate(state, start_time): return
        
        state.active_step = 1
        state.current_agent = "SignalAgent"
        state.performance_metrics.agents_executed += 1
        
        signal_agent = SignalAgent()
        signal_agent.run(state, variant)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.2)  # Latency to let UI animate

        # --- STEP 2: CRISIS DETECTION ---
        await self.wait_for_resume_signal(state, start_time)
        if await self.check_stopped(state) or self.check_timeout_and_validate(state, start_time): return
        
        state.active_step = 2
        state.current_agent = "DetectionAgent"
        state.performance_metrics.agents_executed += 1
        
        detection_agent = DetectionAgent()
        detection_agent.run(state)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.2)

        # Pause if step mode is active
        if state.execution_mode == "step":
            state.execution_mode = "paused"

        # --- STEP 3: PLAN DRAFTING ---
        await self.wait_for_resume_signal(state, start_time)
        if await self.check_stopped(state) or self.check_timeout_and_validate(state, start_time): return
        
        state.active_step = 3
        state.current_agent = "PlannerAgent"
        state.performance_metrics.agents_executed += 1
        
        planner_agent = PlannerAgent()
        planner_agent.run(state)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.2)

        if state.execution_mode == "step":
            state.execution_mode = "paused"

        # --- STEP 4: EVALUATION & CONSTRAINT AUDITING ---
        await self.wait_for_resume_signal(state, start_time)
        if await self.check_stopped(state) or self.check_timeout_and_validate(state, start_time): return
        
        state.active_step = 4
        state.current_agent = "ValidationAgent"
        state.performance_metrics.agents_executed += 2  # Evaluator and Validation
        
        evaluator_agent = EvaluatorAgent()
        evaluator_agent.run(state)
        
        validation_agent = ValidationAgent()
        validation_agent.run(state)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.2)

        # Feedback Loop 1: Planner-Evaluator Collaboration
        best_score = max(ev.aggregate_score for ev in state.evaluations.values())
        if best_score < config.TARGET_SCORE_THRESHOLD:
            feedback = state.evaluations[
                max(state.evaluations, key=lambda k: state.evaluations[k].aggregate_score)
            ].feedback
            
            self.log(state, "Orchestrate plan refinement loop", "refining_plans", f"Best score ({best_score}) is below target threshold ({config.TARGET_SCORE_THRESHOLD}). Refinement active.", "Requested plan refinement due to low evaluation score", {"feedback": feedback})
            state.performance_metrics.iterations += 1
            
            planner_agent.run(state, evaluator_feedback=feedback)
            evaluator_agent.run(state)
            validation_agent.run(state)
            if self.check_timeout_and_validate(state, start_time): return
            await asyncio.sleep(1.0)

        # Feedback Loop 2: Validation Correction
        if not state.validation.valid:
            issues = state.validation.issues
            self.log(state, "Orchestrate plan correction loop", "correcting_plans", "Validation failures detected. Requesting planner adjustment.", "Requested plan correction due to validation issues", {"issues": issues})
            state.performance_metrics.iterations += 1
            
            planner_agent.run(state, validation_issues=issues)
            evaluator_agent.run(state)
            validation_agent.run(state)
            if self.check_timeout_and_validate(state, start_time): return
            await asyncio.sleep(1.0)

        if state.execution_mode == "step":
            state.execution_mode = "paused"

        # --- STEP 5: MEMORY CORRELATION ---
        await self.wait_for_resume_signal(state, start_time)
        if await self.check_stopped(state) or self.check_timeout_and_validate(state, start_time): return
        
        state.active_step = 5
        state.current_agent = "MemoryAgent"
        state.performance_metrics.agents_executed += 1
        
        memory_agent = MemoryAgent()
        memory_agent.run(state)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.2)

        if state.execution_mode == "step":
            state.execution_mode = "paused"

        # --- STEP 6: DECISION RESOLUTION ---
        await self.wait_for_resume_signal(state, start_time)
        if await self.check_stopped(state) or self.check_timeout_and_validate(state, start_time): return
        
        state.active_step = 6
        state.current_agent = "DecisionAgent"
        state.performance_metrics.agents_executed += 1
        
        decision_agent = DecisionAgent()
        decision_agent.run(state)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.2)

        # Set final completion state (if not already no_feasible_plan)
        if state.status != "no_feasible_plan":
            state.status = "completed"
        
        state.active_step = 6
        state.current_agent = "None"
        validate_state(state)
        
        self.log(state, intent, "completed_flow", reasoning, "Decision flow successfully completed.", {
            "selected": state.current_decision.selected_plan,
            "status": state.status,
            "metrics": state.performance_metrics.dict()
        })

    async def run_replan_async(self, state: TaskState, event_type: str) -> None:
        """Injects a disruption event and re-runs evaluation/decision loops asynchronously."""
        intent = "Adapt current strategic plans to new environmental disruption"
        action = "orchestrate_replanning_flow"
        reasoning = "Replanning cycle completed."

        start_time = time.time()
        self.log(state, intent, action, f"Disruption injection triggered: '{event_type}'. Initiating replanning loop...", "Initiated replanning cycle", {})

        # 1. Inject event
        replan_agent = ReplanningAgent()
        replan_agent.run(state, event_type)
        if self.check_timeout_and_validate(state, start_time): return
        await asyncio.sleep(1.0)

        # 2. Re-run loops
        evaluator_agent = EvaluatorAgent()
        evaluator_agent.run(state)
        state.performance_metrics.agents_executed += 1
        if self.check_timeout_and_validate(state, start_time): return

        validation_agent = ValidationAgent()
        validation_agent.run(state)
        state.performance_metrics.agents_executed += 1
        if self.check_timeout_and_validate(state, start_time): return

        # Re-check validation
        if not state.validation.valid:
            issues = state.validation.issues
            self.log(state, "replan correction loop", "replan_correction", f"Validation issues on replan: {issues}. Planner correcting...", "Requested detour route validations", {"issues": issues})
            state.performance_metrics.iterations += 1
            
            planner_agent = PlannerAgent()
            planner_agent.run(state, validation_issues=issues)
            evaluator_agent.run(state)
            validation_agent.run(state)
            if self.check_timeout_and_validate(state, start_time): return
            await asyncio.sleep(1.0)

        # 3. Memory Precedents
        memory_agent = MemoryAgent()
        memory_agent.run(state)
        state.performance_metrics.agents_executed += 1
        if self.check_timeout_and_validate(state, start_time): return

        # 4. Final Decision
        decision_agent = DecisionAgent()
        decision_agent.run(state)
        state.performance_metrics.agents_executed += 1
        
        validate_state(state)

        self.log(state, intent, "replan_completed_flow", reasoning, "Updated final decision and alternate strategies", {
            "before": state.original_decision.selected_plan,
            "after": state.current_decision.selected_plan,
            "status": state.status
        })

    def run(self, state: TaskState, variant: str = None, scenario_override: dict = None) -> None:
        """Runs the complete multi-agent pipeline synchronously (for testing/direct usage)."""
        intent = "Orchestrate multi-agent decision flow"
        action = "orchestrate_decision_flow"
        reasoning = "Coordinating sequential cognitive agents and feedback loops to resolve optimal response strategy."

        # Reset logs and state structure for fresh run
        state.logs = []
        state.original_decision = None
        state.current_decision = None
        state.disruption_event = None
        state.fallback = None
        state.performance_metrics = PerformanceSummary(
            agents_executed=0,
            iterations=1,
            validation_failures=0,
            replans_triggered=0
        )
        state.status = "running"
        
        self.log(state, intent, action, reasoning, "Initiating deliberative multi-agent cognitive simulation...", {})

        # --- STEP 1: SIGNAL GENERATION ---
        state.active_step = 1
        state.current_agent = "SignalAgent"
        state.performance_metrics.agents_executed += 1
        
        if scenario_override:
            state.scenario = ScenarioMetrics(**scenario_override)
            state.metadata["scenario_variant"] = "custom_override"
            SignalAgent().log(state, "Generate simulated weather and social telemetry based on selected scenario variant", "simulate_environment", "Acquiring real-time rainfall sensors, river gauges, crowd estimates, and social media agitation signals.", "Mapped incident telemetry to scenario state", state.scenario.dict())
        else:
            SignalAgent().run(state, variant)

        # --- STEP 2: CRISIS DETECTION ---
        state.active_step = 2
        state.current_agent = "DetectionAgent"
        state.performance_metrics.agents_executed += 1
        DetectionAgent().run(state)

        # --- STEP 3: PLAN DRAFTING ---
        state.active_step = 3
        state.current_agent = "PlannerAgent"
        state.performance_metrics.agents_executed += 1
        planner_agent = PlannerAgent()
        planner_agent.run(state)

        # --- STEP 4: EVALUATION & CONSTRAINT AUDITING ---
        state.active_step = 4
        state.current_agent = "ValidationAgent"
        state.performance_metrics.agents_executed += 2  # Evaluator and Validation
        evaluator_agent = EvaluatorAgent()
        evaluator_agent.run(state)
        validation_agent = ValidationAgent()
        validation_agent.run(state)

        # Feedback Loop 1: Planner-Evaluator Collaboration
        best_score = max(ev.aggregate_score for ev in state.evaluations.values())
        if best_score < config.TARGET_SCORE_THRESHOLD:
            feedback = state.evaluations[
                max(state.evaluations, key=lambda k: state.evaluations[k].aggregate_score)
            ].feedback
            self.log(state, "Orchestrate plan refinement loop", "refining_plans", f"Best score ({best_score}) is below target threshold ({config.TARGET_SCORE_THRESHOLD}). Refinement active.", "Requested plan refinement due to low evaluation score", {"feedback": feedback})
            state.performance_metrics.iterations += 1
            planner_agent.run(state, evaluator_feedback=feedback)
            evaluator_agent.run(state)
            validation_agent.run(state)

        # Feedback Loop 2: Validation Correction
        if not state.validation.valid:
            issues = state.validation.issues
            self.log(state, "Orchestrate plan correction loop", "correcting_plans", "Validation failures detected. Requesting planner adjustment.", "Requested plan correction due to validation issues", {"issues": issues})
            state.performance_metrics.iterations += 1
            planner_agent.run(state, validation_issues=issues)
            evaluator_agent.run(state)
            validation_agent.run(state)

        # --- STEP 5: MEMORY CORRELATION ---
        state.active_step = 5
        state.current_agent = "MemoryAgent"
        state.performance_metrics.agents_executed += 1
        MemoryAgent().run(state)

        # --- STEP 6: DECISION RESOLUTION ---
        state.active_step = 6
        state.current_agent = "DecisionAgent"
        state.performance_metrics.agents_executed += 1
        DecisionAgent().run(state)

        # Set final completion state (if not already no_feasible_plan)
        if state.status != "no_feasible_plan":
            state.status = "completed"
        
        state.active_step = 6
        state.current_agent = "None"
        validate_state(state)
        
        self.log(state, intent, "completed_flow", reasoning, "Decision flow successfully completed.", {
            "selected": state.current_decision.selected_plan,
            "status": state.status,
            "metrics": state.performance_metrics.dict()
        })

    def run_replan(self, state: TaskState, event_type: str) -> None:
        """Injects a disruption event and re-runs evaluation/decision loops synchronously."""
        intent = "Adapt current strategic plans to new environmental disruption"
        action = "orchestrate_replanning_flow"
        reasoning = "Replanning cycle completed."

        self.log(state, intent, action, f"Disruption injection triggered: '{event_type}'. Initiating replanning loop...", "Initiated replanning cycle", {})

        # 1. Inject event
        replan_agent = ReplanningAgent()
        replan_agent.run(state, event_type)

        # 2. Re-run loops
        evaluator_agent = EvaluatorAgent()
        evaluator_agent.run(state)
        state.performance_metrics.agents_executed += 1

        validation_agent = ValidationAgent()
        validation_agent.run(state)
        state.performance_metrics.agents_executed += 1

        # Re-check validation
        if not state.validation.valid:
            issues = state.validation.issues
            self.log(state, "replan correction loop", "replan_correction", f"Validation issues on replan: {issues}. Planner correcting...", "Requested detour route validations", {"issues": issues})
            state.performance_metrics.iterations += 1
            
            planner_agent = PlannerAgent()
            planner_agent.run(state, validation_issues=issues)
            evaluator_agent.run(state)
            validation_agent.run(state)

        # 3. Memory Precedents
        memory_agent = MemoryAgent()
        memory_agent.run(state)
        state.performance_metrics.agents_executed += 1

        # 4. Final Decision
        decision_agent = DecisionAgent()
        decision_agent.run(state)
        state.performance_metrics.agents_executed += 1
        
        validate_state(state)

        self.log(state, intent, "replan_completed_flow", reasoning, "Updated final decision and alternate strategies", {
            "before": state.original_decision.selected_plan,
            "after": state.current_decision.selected_plan,
            "status": state.status
        })
