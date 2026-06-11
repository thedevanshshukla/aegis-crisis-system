# operational rules and limits for AEGIS

# System Constraint Layer (Explicit constraints)
MAX_BUDGET = 220000.0   # Max budget in USD
MAX_RISK = 4.0          # Max acceptable risk level (1.0 to 5.0 scale)
MIN_COVERAGE = 70.0     # Minimum acceptable population coverage percentage

DETERMINISTIC_MODE = True

SEVERITY_LABELS = {
    "flood": [(3.0, "CRITICAL"), (2.0, "HIGH"), (1.0, "MEDIUM")],
    "unrest": [(80, "HIGH"), (50, "MEDIUM")]
}

TARGET_SCORE_THRESHOLD = 72.0  # Plan scores under this trigger planning adjustment loops

# Scoring weights
WEIGHT_TIME = 0.30
WEIGHT_RISK = 0.30
WEIGHT_COST = 0.20
WEIGHT_COVERAGE = 0.20

# Scenario Variants Presets
SCENARIO_VARIANTS = {
    "variant_a": {
        "name": "Variant A: Moderate Flood & Low Unrest",
        "rainfall": 58.0,       # mm/h
        "water_level": 2.15,    # meters
        "crowd_size": 250,      # protesters count
        "unrest_level": 20.0,   # 0 to 100
        "description": "Prolonged rainfall causing mild pooling in Sector A. Traffic remains normal, crowd gatherings are peaceful and sparse.",
        "location": "Sector A & Delta"
    },
    "variant_b": {
        "name": "Variant B: Storm Surge & Extreme Civil Unrest",
        "rainfall": 72.0,
        "water_level": 3.2,
        "crowd_size": 1800,
        "unrest_level": 82.0,
        "description": "Active storm center. Heavy debris blocking escape routes. Worker strikes escalating and blocking primary evacuation vehicles.",
        "location": "Sector B & Delta"
    },
    "variant_c": {
        "name": "Variant C: Catastrophic Surge & Active Rioting",
        "rainfall": 130.0,
        "water_level": 4.20,
        "crowd_size": 3100,
        "unrest_level": 96.0,
        "description": "Catastrophic river breach coupled with hostile crowds attacking infrastructure. Extreme weather prevents standard air/ground routing.",
        "location": "All Sectors (Alpha to Delta)"
    }
}

# Historical crisis cases for the Memory Agent
HISTORICAL_CASES = [
    {
        "id": "CASE-101",
        "description": "Flash Flood in Sector D with High-density Protest Group",
        "metrics": {
            "rainfall": 70.0,      # mm/h
            "water_level": 3.2,    # meters
            "crowd_size": 2000,
            "unrest_level": 85.0   # 0 to 100
        },
        "selected_plan": "Safest",
        "outcome": "Successful evacuation with 98% coverage and 0 casualties. Delayed by 2 hours due to police escort protocol but high safety achieved.",
        "success_rate": 0.95
    },
    {
        "id": "CASE-102",
        "description": "Moderate River Overflow in Sector A & Localized Unrest",
        "metrics": {
            "rainfall": 45.0,
            "water_level": 2.1,
            "crowd_size": 600,
            "unrest_level": 40.0
        },
        "selected_plan": "Balanced",
        "outcome": "Successful localized containment and road drainage routing. Balanced deployment cost-efficient and timely.",
        "success_rate": 0.88
    },
    {
        "id": "CASE-103",
        "description": "Extreme Storm Surge & Sector C Infrastructure Outage",
        "metrics": {
            "rainfall": 110.0,
            "water_level": 4.5,
            "crowd_size": 100,
            "unrest_level": 10.0
        },
        "selected_plan": "Safest",
        "outcome": "Severe terrain flooding. Air transport elements deployed. High cost incurred but 100% vital asset protection completed.",
        "success_rate": 0.92
    }
]
