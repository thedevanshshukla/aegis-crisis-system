import os
import sys

# Resolve paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.models import TaskState
from app.agents.master import MasterAgent
from app.agents.replanning import ReplanningAgent
from app import config

def run_tests():
    print("==================================================")
    print("   AEGIS: RUNNING AGENT COGNITIVE LOGIC TESTS    ")
    print("==================================================")
    
    # Initialize state
    state = TaskState()
    master = MasterAgent()
    
    print("\n[TEST 1] Orchestrating complete multi-agent pipeline...")
    # Inject a deterministic scenario to verify validation and loop behaviors
    override = {
        "rainfall": 72.0,      # mm/h (Breaches 50.0 flood threshold)
        "water_level": 3.2,    # meters (Breaches 2.2 alert threshold and requires escort check)
        "crowd_size": 1900,
        "unrest_level": 82.0,  # unrest > 70 requires police escort
        "description": "Severe atmospheric system dumping rainfall; workers strikes escalating sector access boundaries.",
        "location": "Sectors Alpha & Beta"
    }
    
    master.run(state, scenario_override=override)
    
    # Assertions on state
    assert state.scenario is not None, "Scenario generation failed."
    assert state.detection is not None, "Threat detection failed."
    assert state.detection.alert_level == "AMBER", f"Expected AMBER alert level, got {state.detection.alert_level}"
    assert len(state.plans) == 3, "Expected 3 generated plan strategies."
    
    print("[SUCCESS] Scenario, Threat detection, and Strategies created.")
    
    # Verify cognitive logs trace structure
    print("\n[TEST 2] Verifying Agent Message Bus logs for Cognitive intent/reasoning keys...")
    assert len(state.logs) > 0, "No logs collected in state."
    
    for idx, log in enumerate(state.logs):
        # Assert keys are populated
        assert log.agent != "", f"Log index {idx} missing agent name."
        assert log.intent != "", f"Log index {idx} by {log.agent} missing intent."
        assert log.action != "", f"Log index {idx} by {log.agent} missing action."
        assert log.reasoning != "", f"Log index {idx} by {log.agent} missing reasoning."
        print(f"  [{log.agent}] action: '{log.action}' | reasoning: '{log.reasoning[:70]}...'")
        
    print("[SUCCESS] All log records contain cognitive intent, action, and reasoning structures.")

    # Verify Decision outputs (Perceived intelligence features)
    print("\n[TEST 3] Auditing Decision outputs (Confidence breakdown, Rejected reasons)...")
    dec = state.current_decision
    assert dec is not None, "No decision reached."
    print(f"  Selected optimal strategy: {dec.selected_plan}")
    print(f"  Confidence Score: {int(dec.confidence * 100)}%")
    print(f"  Confidence Factors -> score: {dec.confidence_factors.score}, consistency: {dec.confidence_factors.consistency}, past_success: {dec.confidence_factors.past_success}")
    
    assert dec.confidence > 0, "Confidence calculation failed."
    assert len(dec.rejected_plans) == 2, "Expected exactly 2 rejected plan traces."
    
    for rej in dec.rejected_plans:
        assert rej.plan in ["Fastest", "Safest", "Balanced"], f"Invalid rejected plan: {rej.plan}"
        assert rej.reason != "", f"Missing rejection reasoning for plan {rej.plan}"
        print(f"  * Rejected alternative '{rej.plan}': {rej.reason}")
        
    print("[SUCCESS] Confidence breakdown and rejected plan justifications are intact.")

    # Verify Memory Narrative
    print("\n[TEST 4] Auditing Memory precedent retrieval & score boost narrative...")
    assert dec.memory_narrative.memory_used == True, "Memory retrieval failed for close scenario matching (CASE-101)."
    assert "CASE-101" in dec.memory_narrative.reference_case, "Did not match expected CASE-101 precedent."
    print(f"  Memory Matched Reference: {dec.memory_narrative.reference_case}")
    print(f"  Narrative Impact: {dec.memory_narrative.impact}")
    
    # Verify score boost applied
    rec_plan = "Safest" # CASE-101 recommends Safest
    assert "Historical Boost" in state.evaluations[rec_plan].feedback, "Historical score boost not applied to evaluations."
    print("[SUCCESS] Memory precedents mapped and scores successfully updated with narrative traces.")

    # Verify Replanning & Detours
    print("\n[TEST 5] Injecting environmental anomaly (Bridge Collapse) and checking Adaptation...")
    master.run_replan(state, "bridge_collapse")
    
    assert state.disruption_event == "bridge_collapse", "Disruption event state marker missing."
    assert state.original_decision is not None, "Original decision backup was lost on replan."
    assert state.current_decision is not None, "Updated current decision was not computed."
    
    print(f"  Before Anomaly Decision: {state.original_decision.selected_plan}")
    print(f"  After Anomaly Decision: {state.current_decision.selected_plan}")
    print(f"  Replan Justification: {state.current_decision.justification}")
    
    # Check if Fastest plan duration has detour delay added (originally 2.5h, detoured to 5.5h)
    assert state.plans["Fastest"].duration_hours == 5.5, f"Fastest detour duration expected 5.5, got {state.plans['Fastest'].duration_hours}"
    
    print("[SUCCESS] Bridge Collapse successfully rerouted; scores adjusted and decisions re-orchestrated.")
    print("\n==================================================")
    print("   ALL COGNITIVE SYSTEM INTEGRATION TESTS PASSED   ")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
