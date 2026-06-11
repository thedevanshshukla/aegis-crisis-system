# AEGIS: Autonomous Crisis Intelligence System

AEGIS is an orchestrated, feedback-driven, memory-aware multi-agent autonomous decision system designed for disaster/crisis response scenarios (floods and civil unrest). 

Unlike a sequential pipeline, AEGIS utilizes **active collaboration, feasibility audits, and experience-based memory tuning** to formulate, evaluate, and dynamically adapt strategic decisions in real-time under uncertainty.

---

## 🧠 Core System Architecture

AEGIS is built around a central, shared **Task State** and orchestrated by a **Master Orchestrator**. The active components operate as follows:

```
                  User Input / Telemetry Injector
                               ↓
                   MasterAgent (Orchestrator)
                               ↓
            SignalAgent  ──>  DetectionAgent (Threshold checks)
                               ↓
         ┌─────────────────────┴─────────────────────┐
         │                                           ▼
         │                            PlannerAgent (Drafts Fastest, Safest, Balanced)
         │                                           ▲
         │                                           │ (Planner-Evaluator Loop)
         │                                           ▼
         │                            EvaluatorAgent (Scores criteria: Time, Risk, Cost, Coverage)
         │                                           ▲
         │                                           │ (Validation-Planner Correction Loop)
         │                                           ▼
         │                            ValidationAgent (Audits Cost limits & Riot Escort rules)
         │                                           │
         ▼                                           ▼
MemoryAgent (Searches precedents) ──>  DecisionAgent (Selected choice, Confidence weights, Rejection reasons)
         │                                           │
         └───────────────────┬───────────────────────┘
                             ▼
                ReplanningAgent (Injects Anomaly) ──> Re-orchestrates loops
```

### Key "Perceived Intelligence" Features:
1. **Cognitive Message Logging**: Every agent posts to the message bus containing its `intent` (purpose) and `reasoning` (conclusion), making its internal thoughts visible.
2. **Confidence Engine Breakdown**: Confidences are computed dynamically based on a weighted blend of plan performance scores (40%), safety audit compatibility (30%), and historical precedents matching (30%).
3. **Experience-based Score Tuning**: The `MemoryAgent` correlates current parameters with historical cases and boosts the evaluation index of historically successful plans, detailing the precedent's success rate and outcomes.
4. **Deliberate Plan Rejection**: The final decision documents specific, structured reasons why the alternative plan designs were rejected.
5. **Disruption Comparison Matrix**: When anomalies are injected (e.g. Bridge Collapse), the system preserves the "Before" decision side-by-side with the "After" adaptation, illustrating the system's ability to think under pressure.

---

## 📁 File Structure

```
d:\projects\far away\
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI Server & Routes
│   │   ├── models.py           # Shared Pydantic models & central TaskState
│   │   ├── config.py           # Thresholds, weights, and memory precedent seeds
│   │   └── agents/
│   │       ├── __init__.py
│   │       ├── base.py         # Base Agent logging structure
│   │       ├── master.py       # Orchestration & loop controller
│   │       ├── signal.py       # Telemetry simulation agent
│   │       ├── detection.py    # Danger zone/threshold detection
│   │       ├── planner.py      # Refineable plan generator (Fastest, Safest, Balanced)
│   │       ├── evaluator.py    # Weighted metric evaluator & feedback loop
│   │       ├── validation.py   # Active safety and budget audit guardrail
│   │       ├── memory.py       # Historic precedent matching and score booster
│   │       ├── decision.py     # Plan selection & Confidence engine
│   │       └── replanning.py   # Incident disruption injector
│   └── requirements.txt        # Package requirements
├── frontend/
│   ├── index.html              # AEGIS Control Dashboard
│   ├── style.css               # Neon-styled Glassmorphism stylesheet
│   └── app.js                  # Frontend binding script and REST client
├── run.py                      # Unified FastAPI server runner
├── test_cognitive.py           # Integration and logic correctness test suite
└── README.md                   # System documentation
```

---

## ⚡ Setup & Execution

### 1. Install Dependencies
Make sure you have Python 3.8+ installed. Navigate to the project root and install requirements:
```bash
pip install -r backend/requirements.txt
```

### 2. Run Automated Validation Tests
Run the cognitive test suite to verify agent logic, memory boosts, feedback loops, and reasoning formats:
```bash
python test_cognitive.py
```

### 3. Launch the Server
Boot the FastAPI application and serve the frontend at the same time:
```bash
python run.py
```
Open your web browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🛠️ API Documentation

The backend exposes the following REST endpoints:

- `GET /api/state`: Returns the current system `TaskState` payload.
- `POST /api/reset`: Wipes the global in-memory state back to ready defaults.
- `POST /api/simulate`: Step 1 - SignalAgent simulates metrics, DetectionAgent checks alerts.
- `POST /api/plan`: Step 2 - PlannerAgent drafts action steps.
- `POST /api/evaluate`: Step 3 - Evaluator & Validation agents run scoring and correction loops.
- `POST /api/decide`: Step 4 - Memory precedent matching boosts scores, Decision selects optimal plan.
- `POST /api/replan`: Step 5 - Inject a disruption (e.g. `bridge_collapse`, `riot_outbreak`, `severe_downpour`) and run evaluations/decisions again.
- `POST /api/run_full`: Performs the entire orchestrated sequence in a single network pass.
