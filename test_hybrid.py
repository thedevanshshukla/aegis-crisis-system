import os
import sys
import asyncio

# Resolve paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.models import TaskState
from app.agents.master import MasterAgent
from app import config

async def test_execution_variants():
    print("==================================================")
    print("   AEGIS v2: RUNNING HYBRID SYSTEM COGNITIVE TESTS")
    print("==================================================")
    
    # -----------------------------------------------------------------
    # TEST 1: Variant A (Moderate Flood & Low Unrest) -> Balanced Plan
    # -----------------------------------------------------------------
    print("\n[TEST 1] Orchestrating Preset Variant A (Moderate Flood)...")
    state_a = TaskState()
    master = MasterAgent()
    
    await master.run_async(state_a, variant="variant_a")
    
    assert state_a.status == "completed", f"Variant A failed, status: {state_a.status}"
    assert state_a.detection.level in ["NORMAL", "ELEVATED"], f"Variant A threat expected NORMAL/ELEVATED, got {state_a.detection.level}"
    assert state_a.current_decision.selected_plan == "Balanced", f"Expected Balanced plan for Variant A, got {state_a.current_decision.selected_plan}"
    print(f"  [OK] Choice resolved to: {state_a.current_decision.selected_plan}")
    print(f"  [OK] Crisis Severity Index: {state_a.detection.severity_index} ({state_a.detection.level})")
    
    # -----------------------------------------------------------------
    # TEST 2: Variant B (Severe Flood & High Unrest) -> Safest Plan
    # -----------------------------------------------------------------
    print("\n[TEST 2] Orchestrating Preset Variant B (Severe Unrest & Surge)...")
    state_b = TaskState()
    
    await master.run_async(state_b, variant="variant_b")
    
    assert state_b.status == "completed", f"Variant B failed, status: {state_b.status}"
    assert state_b.detection.level == "ELEVATED", f"Variant B threat expected ELEVATED, got {state_b.detection.level}"
    assert state_b.current_decision.selected_plan == "Safest", f"Expected Safest plan for Variant B, got {state_b.current_decision.selected_plan}"
    print(f"  [OK] Choice resolved to: {state_b.current_decision.selected_plan}")
    print(f"  [OK] Crisis Severity Index: {state_b.detection.severity_index} ({state_b.detection.level})")

    # -----------------------------------------------------------------
    # TEST 3: Variant C (Catastrophic Surge & active Riot) -> Failure Escalation
    # -----------------------------------------------------------------
    print("\n[TEST 3] Orchestrating Preset Variant C (Catastrophic Failure Path)...")
    state_c = TaskState()
    
    await master.run_async(state_c, variant="variant_c")
    
    assert state_c.status == "no_feasible_plan", f"Expected no_feasible_plan, got {state_c.status}"
    assert state_c.detection.level == "CRITICAL", f"Variant C threat expected CRITICAL, got {state_c.detection.level}"
    assert state_c.current_decision.selected_plan == "None", f"Expected selected plan to be None, got {state_c.current_decision.selected_plan}"
    assert state_c.fallback == "Partial evacuation with delayed full deployment until escorts or air bridges are established.", f"Unexpected fallback payload: {state_c.fallback}"
    print("  [OK] Failure path successfully triggered.")
    print(f"  [OK] Escalated Threat: {state_c.detection.level} (Severity Index: {state_c.detection.severity_index})")
    print(f"  [OK] Escalation Fallback Action: '{state_c.fallback}'")

    # -----------------------------------------------------------------
    # TEST 4: Agent Intent Evolution Checking
    # -----------------------------------------------------------------
    print("\n[TEST 4] Verifying Agent Intent Evolution logs...")
    # Let's inspect logs in Variant B where validation failed once and triggered a correction loop
    planner_intents = [log.intent for log in state_b.logs if log.agent == "PlannerAgent"]
    
    # Checking for intent transition
    assert "initial plan generation" in planner_intents, "Missing initial plan generation intent."
    assert "refining plan due to budget/safety violations" in planner_intents, "Missing refinement loop intent."
    
    print("  Intents recorded by PlannerAgent:")
    for intent in planner_intents:
        print(f"    - Intent state: '{intent}'")
    print("  [OK] Cognitive intent evolved correctly from initial generation to loop refinements.")

    # -----------------------------------------------------------------
    # TEST 5: Observability & Agent Performance Metrics
    # -----------------------------------------------------------------
    print("\n[TEST 5] Auditing Performance Summaries...")
    perf = state_b.performance_metrics
    assert perf.agents_executed >= 6, f"Expected at least 6 agents executed, got {perf.agents_executed}"
    assert perf.iterations > 1, f"Expected loop iterations to occur, got {perf.iterations}"
    assert perf.validation_failures > 0, f"Expected validation failure count, got {perf.validation_failures}"
    print(f"  Agents Executed: {perf.agents_executed}")
    print(f"  Loop Iterations: {perf.iterations}")
    print(f"  Validation Failures: {perf.validation_failures}")
    print("  [OK] Performance telemetry correctly compiled.")

    print("\n==================================================")
    print("   ALL AEGIS v2 HYBRID SYSTEM TESTS PASSED        ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_execution_variants())
