from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AgentMessage(BaseModel):
    agent: str
    intent: str
    action: str
    reasoning: str
    impact: str = ""
    timestamp: str = ""
    data: Dict[str, Any] = {}

class ScenarioMetrics(BaseModel):
    rainfall: float = Field(..., description="Rainfall rate in mm/hour")
    water_level: float = Field(..., description="Water level in meters")
    crowd_size: int = Field(..., description="Protesting crowd size estimation")
    unrest_level: float = Field(..., description="Unrest/Aggression index from 0 to 100")
    description: str = Field("", description="Human-readable summary of the crisis indicators")
    location: str = Field("Sector A & B", description="Affected regions")

class DetectionOutput(BaseModel):
    crisis_detected: bool
    alert_level: str  # GREEN, AMBER, RED
    severity_index: float  # 0.0 to 1.0
    level: str  # NORMAL, ELEVATED, CRITICAL
    triggers: List[str]
    reasoning: str

class PlanStep(BaseModel):
    step_number: int
    action: str
    resource: str
    estimated_duration_hours: float

class ActionPlan(BaseModel):
    name: str  # Fastest, Safest, Balanced
    steps: List[PlanStep]
    cost: float
    duration_hours: float
    risk_level: float  # 1.0 (Low) to 5.0 (Critical)
    coverage_percentage: float  # 0 to 100
    description: str

class PlanEvaluation(BaseModel):
    plan_name: str
    time_score: float
    risk_score: float
    cost_score: float
    coverage_score: float
    aggregate_score: float
    feedback: str = ""

class ValidationOutput(BaseModel):
    valid: bool
    issues: List[str] = []
    warnings: List[str] = []

class ConfidenceFactors(BaseModel):
    score: float
    consistency: float
    past_success: float

class RejectedPlan(BaseModel):
    plan: str
    reason: str

class MemoryNarrative(BaseModel):
    memory_used: bool
    reference_case: str = "N/A"
    impact: str = "No prior cases matched."

class PlanRank(BaseModel):
    plan: str
    score: float
    rank: int

class DecisionOutput(BaseModel):
    selected_plan: str
    confidence: float
    confidence_factors: ConfidenceFactors
    ranking: List[PlanRank] = []
    justification: str
    rejected_plans: List[RejectedPlan] = []
    memory_narrative: MemoryNarrative
    why_this_plan: List[str] = []
    trade_offs: List[str] = []

class PerformanceSummary(BaseModel):
    agents_executed: int = 0
    iterations: int = 1
    validation_failures: int = 0
    replans_triggered: int = 0

class TaskState(BaseModel):
    status: str = "ready"  # ready, running, paused, stopped, completed, no_feasible_plan
    execution_mode: str = "auto"  # auto, step, paused
    current_agent: str = "None"
    active_step: int = 0
    scenario: Optional[ScenarioMetrics] = None
    detection: Optional[DetectionOutput] = None
    plans: Dict[str, ActionPlan] = {}
    evaluations: Dict[str, PlanEvaluation] = {}
    validation: Optional[ValidationOutput] = None
    original_decision: Optional[DecisionOutput] = None
    current_decision: Optional[DecisionOutput] = None
    disruption_event: Optional[str] = None
    logs: List[AgentMessage] = []
    performance_metrics: PerformanceSummary = PerformanceSummary()
    fallback: Optional[str] = None
    metadata: Dict[str, Any] = {}

def validate_state(state: TaskState):
    assert state.status in ["ready", "running", "paused", "stopped", "completed", "no_feasible_plan"]
    assert state.execution_mode in ["auto", "step", "paused"]
