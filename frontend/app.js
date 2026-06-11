// AEGIS v2 Frontend Orchestrator Client

const API_BASE = '/api';

// Cache Controls
const selectVariant = document.getElementById('select-variant');
const btnStart = document.getElementById('btn-control-start');
const btnPause = document.getElementById('btn-control-pause');
const btnStep = document.getElementById('btn-control-step');
const btnStop = document.getElementById('btn-control-stop');
const btnReset = document.getElementById('btn-reset');

// Readouts
const readoutStatus = document.getElementById('readout-status-val');
const readoutAgent = document.getElementById('readout-agent-val');
const systemStatusVal = document.getElementById('system-status-val');
const alertLevelVal = document.getElementById('alert-level-val');

// Metrics
const metricAgents = document.getElementById('metric-agents-count');
const metricIterations = document.getElementById('metric-iterations-count');
const metricFailures = document.getElementById('metric-failures-count');
const metricReplans = document.getElementById('metric-replans-count');

// Panels
const noTelemetryMsg = document.getElementById('no-telemetry-msg');
const telemetryGrid = document.getElementById('telemetry-grid');
const noPlansMsg = document.getElementById('no-plans-msg');
const plansContainer = document.getElementById('plans-container');
const noDecisionMsg = document.getElementById('no-decision-msg');
const decisionContent = document.getElementById('decision-content');
const decisionMainPanel = document.getElementById('decision-main-panel');
const fallbackEscalationAlert = document.getElementById('fallback-escalation-alert');
const replanComparisonCard = document.getElementById('replan-comparison-card');
const replanEmptyCard = document.getElementById('replan-empty-card');
const disruptionFeedbackMsg = document.getElementById('disruption-feedback-msg');

// Terminal Log
const terminalLogs = document.getElementById('terminal-logs');

// Disruption Buttons
const btnEventBridge = document.getElementById('btn-event-bridge');
const btnEventRiot = document.getElementById('btn-event-riot');
const btnEventStorm = document.getElementById('btn-event-storm');

let pollingInterval = null;
let appConfig = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    resetUIState();
    try {
        const response = await fetch(`${API_BASE}/config`);
        appConfig = await response.json();
        renderDefaultCrisisContext();
    } catch (err) {
        console.error("Error fetching AEGIS configurations:", err);
    }
});

// Event Listeners
btnStart.addEventListener('click', startExecution);
btnPause.addEventListener('click', togglePauseResume);
btnStep.addEventListener('click', stepExecution);
btnStop.addEventListener('click', stopExecution);
btnReset.addEventListener('click', resetSystemState);

btnEventBridge.addEventListener('click', () => injectDisruption('bridge_collapse'));
btnEventRiot.addEventListener('click', () => injectDisruption('riot_outbreak'));
btnEventStorm.addEventListener('click', () => injectDisruption('severe_downpour'));

// Set default Crisis Context placeholder values matching prompt initially
function renderDefaultCrisisContext() {
    const floodEl = document.getElementById('context-flood-val');
    const unrestEl = document.getElementById('context-unrest-val');
    
    floodEl.innerText = "3.2m (CRITICAL)";
    floodEl.className = "value text-red bold";
    unrestEl.innerText = "82 (HIGH)";
    unrestEl.className = "value text-red bold";
    
    document.getElementById('context-teams-val').innerText = "2";
    document.getElementById('context-hospitals-val').innerText = "2";
}

// Reset system state
async function resetSystemState() {
    stopPolling();
    try {
        await fetch(`${API_BASE}/reset`, { method: 'POST' });
        resetUIState();
        if (appConfig) {
            renderDefaultCrisisContext();
        }
    } catch (err) {
        console.error("Error resetting AEGIS state:", err);
    }
}

function resetUIState() {
    // Reset buttons
    if (btnStart) btnStart.disabled = false;
    if (btnPause) {
        btnPause.disabled = true;
        btnPause.innerText = '⏸ Pause';
    }
    if (btnStep) btnStep.disabled = false;
    if (btnStop) btnStop.disabled = true;
    
    if (btnEventBridge) btnEventBridge.disabled = true;
    if (btnEventRiot) btnEventRiot.disabled = true;
    if (btnEventStorm) btnEventStorm.disabled = true;

    // Reset status labels
    if (systemStatusVal) {
        systemStatusVal.innerText = 'Ready';
        systemStatusVal.className = 'value text-cyan';
    }
    if (alertLevelVal) {
        alertLevelVal.innerText = 'GREEN';
        alertLevelVal.className = 'value badge badge-green';
    }
    
    if (readoutStatus) {
        readoutStatus.innerText = 'READY';
        readoutStatus.className = 'text-cyan';
    }
    if (readoutAgent) readoutAgent.innerText = 'None';
    
    // Performance
    if (metricAgents) metricAgents.innerText = '0';
    if (metricIterations) metricIterations.innerText = '0';
    if (metricFailures) metricFailures.innerText = '0';
    if (metricReplans) metricReplans.innerText = '0';

    // Timeline steps reset
    for (let i = 1; i <= 6; i++) {
        const stepNode = document.getElementById(`step-node-${i}`);
        if (stepNode) {
            stepNode.className = 'timeline-step';
            const badge = stepNode.querySelector('.step-status');
            if (badge) badge.innerText = 'Pending';
        }
    }

    // Hide panels and display empty states
    if (noTelemetryMsg) noTelemetryMsg.classList.remove('hidden');
    if (telemetryGrid) telemetryGrid.classList.add('hidden');
    
    if (noPlansMsg) noPlansMsg.classList.remove('hidden');
    if (plansContainer) plansContainer.classList.add('hidden');
    
    if (noDecisionMsg) {
        noDecisionMsg.classList.remove('hidden');
        noDecisionMsg.innerText = "No active decision. Run simulation to begin.";
    }
    
    if (decisionContent) decisionContent.classList.add('hidden');
    if (decisionMainPanel) decisionMainPanel.classList.remove('hidden');
    if (fallbackEscalationAlert) fallbackEscalationAlert.classList.add('hidden');
    
    if (replanComparisonCard) replanComparisonCard.classList.add('hidden');
    if (replanEmptyCard) replanEmptyCard.classList.remove('hidden');
    
    if (disruptionFeedbackMsg) {
        disruptionFeedbackMsg.style.display = 'none';
        disruptionFeedbackMsg.innerText = '';
    }

    const evalContainer = document.getElementById('evaluation-container');
    const noEvalMsg = document.getElementById('no-eval-msg');
    if (evalContainer) evalContainer.classList.add('hidden');
    if (noEvalMsg) noEvalMsg.classList.remove('hidden');

    // Terminal
    if (terminalLogs) terminalLogs.innerHTML = '<div class="log-line text-dim">AEGIS ready. Awaiting crisis simulation...</div>';
}

// Polling triggers
function startPolling() {
    stopPolling();
    pollingInterval = setInterval(fetchState, 500);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

async function fetchState() {
    try {
        const response = await fetch(`${API_BASE}/state`);
        const state = await response.json();
        
        renderState(state);
        
        // Stop polling if complete or halted
        if (state.status === 'completed' || state.status === 'no_feasible_plan' || state.status === 'stopped' || state.status === 'ready') {
            stopPolling();
            updateControlsForCompletedState(state);
        } else {
            updateControlsForRunningState(state);
        }
    } catch (err) {
        console.error("Error polling state:", err);
        stopPolling();
    }
}

// START FULL RUN
async function startExecution() {
    const variant = selectVariant.value;
    resetUIState();
    try {
        await fetch(`${API_BASE}/run_full`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ variant: variant, mode: "auto" })
        });
        startPolling();
    } catch (err) {
        console.error("Error starting auto flow:", err);
    }
}

// STEP RUN
async function stepExecution() {
    try {
        const method = 'POST';
        const headers = { 'Content-Type': 'application/json' };
        
        if (readoutStatus.innerText === 'READY') {
            const variant = selectVariant.value;
            await fetch(`${API_BASE}/run_full`, {
                method: method,
                headers: headers,
                body: JSON.stringify({ variant: variant, mode: "step" })
            });
        } else {
            await fetch(`${API_BASE}/step`, { method: method });
        }
        
        startPolling();
    } catch (err) {
        console.error("Error executing step:", err);
    }
}

// PAUSE & RESUME
async function togglePauseResume() {
    try {
        let endpoint = '/api/pause';
        if (btnPause.innerText.includes('Resume')) {
            endpoint = '/api/resume';
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
        const data = await response.json();
        const state = data.state;
        
        renderState(state);
        startPolling();
    } catch (err) {
        console.error("Error toggling pause state:", err);
    }
}

// STOP RUN
async function stopExecution() {
    try {
        const response = await fetch(`${API_BASE}/stop`, { method: 'POST' });
        const data = await response.json();
        const state = data.state;
        stopPolling();
        renderState(state);
        updateControlsForCompletedState(state);
    } catch (err) {
        console.error("Error stopping execution:", err);
    }
}

// INJECT DISRUPTIONS WITH FEEDBACK TOAST
async function injectDisruption(eventType) {
    const eventLabels = {
        'bridge_collapse': 'Bridge Collapse',
        'riot_outbreak': 'Riot Outbreak',
        'severe_downpour': 'Severe Downpour'
    };
    
    if (disruptionFeedbackMsg) {
        disruptionFeedbackMsg.innerText = `⚡ Injecting disruption: ${eventLabels[eventType]}...`;
        disruptionFeedbackMsg.style.display = 'block';
        disruptionFeedbackMsg.className = "disruption-feedback font-mono text-red bold animate-pulse";
    }

    try {
        const response = await fetch(`${API_BASE}/replan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_type: eventType })
        });
        const data = await response.json();
        const state = data.state;
        
        renderState(state);
        renderReplanComparison(state, eventType);
        startPolling();
    } catch (err) {
        console.error("Error replanning:", err);
    }
}

// Button state managers
function updateControlsForRunningState(state) {
    btnStart.disabled = true;
    btnStep.disabled = true;
    btnStop.disabled = false;
    btnPause.disabled = false;
    
    readoutStatus.innerText = state.execution_mode.toUpperCase() === 'PAUSED' ? 'PAUSED' : 'RUNNING';
    readoutStatus.className = state.execution_mode.toUpperCase() === 'PAUSED' ? 'text-amber' : 'text-cyan';
    readoutAgent.innerText = state.current_agent;
    
    if (state.execution_mode === 'paused') {
        btnPause.innerText = '▶ Resume';
        btnPause.className = 'btn btn-outline text-cyan';
        btnStep.disabled = false;
        btnStart.disabled = false; // allow starting a new variant
        systemStatusVal.innerText = 'Paused';
        systemStatusVal.className = 'value text-amber';
    } else {
        btnPause.innerText = '⏸ Pause';
        btnPause.className = 'btn btn-outline';
        systemStatusVal.innerText = 'Calculating...';
        systemStatusVal.className = 'value text-amber pulse-indicator-inline';
    }
}

function updateControlsForCompletedState(state) {
    btnStart.disabled = false;
    btnStep.disabled = false;
    btnStop.disabled = true;
    btnPause.disabled = true;
    btnPause.innerText = '⏸ Pause';
    btnPause.className = 'btn btn-outline';
    
    readoutStatus.innerText = state.status.toUpperCase();
    readoutStatus.className = state.status === 'completed' ? 'text-green' : 'text-red';
    readoutAgent.innerText = 'None';

    if (state.status === 'completed') {
        systemStatusVal.innerText = 'Resolved';
        systemStatusVal.className = 'value text-green';
        
        btnEventBridge.disabled = false;
        btnEventRiot.disabled = false;
        btnEventStorm.disabled = false;
    } else if (state.status === 'no_feasible_plan') {
        systemStatusVal.innerText = 'FAILED LIMITS';
        systemStatusVal.className = 'value text-red';
        
        btnEventBridge.disabled = true;
        btnEventRiot.disabled = true;
        btnEventStorm.disabled = true;
    } else if (state.status === 'stopped') {
        systemStatusVal.innerText = 'Stopped';
        systemStatusVal.className = 'value text-dim';
    }
}

// RENDER ALL STATE
function renderState(state) {
    // 1. Logs
    renderLogs(state.logs);

    // 2. Stepper Timeline View
    renderTimeline(state);

    // 3. Performance Metrics
    metricAgents.innerText = state.performance_metrics.agents_executed;
    metricIterations.innerText = state.performance_metrics.iterations;
    metricFailures.innerText = state.performance_metrics.validation_failures;
    metricReplans.innerText = state.performance_metrics.replans_triggered;

    // 4. Incident Telemetry
    if (state.scenario) {
        if (noTelemetryMsg) noTelemetryMsg.classList.add('hidden');
        if (telemetryGrid) telemetryGrid.classList.remove('hidden');
        
        // Severity Index & level badge
        if (state.detection) {
            const indexEl = document.getElementById('telemetry-severity-idx');
            if (indexEl) indexEl.innerText = state.detection.severity_index.toFixed(2);
            
            const severityLevel = document.getElementById('telemetry-severity-level');
            if (severityLevel) {
                severityLevel.innerText = state.detection.level;
                let badgeClass = 'badge-white';
                if (state.detection.level === 'ELEVATED') badgeClass = 'badge-amber';
                if (state.detection.level === 'CRITICAL') badgeClass = 'badge-red';
                severityLevel.className = `badge ${badgeClass}`;
            }
            
            // Header Alert
            alertLevelVal.innerText = state.detection.alert_level;
            let headerBadge = 'badge-green';
            if (state.detection.alert_level === 'AMBER') headerBadge = 'badge-amber';
            if (state.detection.alert_level === 'RED') headerBadge = 'badge-red';
            alertLevelVal.className = `value badge ${headerBadge}`;
        }
        
        // Update top strip context metrics dynamically using severity labels from config
        const floodEl = document.getElementById('context-flood-val');
        const unrestEl = document.getElementById('context-unrest-val');
        
        let floodSeverity = "NORMAL";
        let unrestSeverity = "LOW";
        
        if (appConfig && appConfig.SEVERITY_LABELS) {
            const labels = appConfig.SEVERITY_LABELS;
            for (const [thresh, label] of labels.flood) {
                if (state.scenario.water_level >= thresh) {
                    floodSeverity = label;
                    break;
                }
            }
            for (const [thresh, label] of labels.unrest) {
                if (state.scenario.unrest_level >= thresh) {
                    unrestSeverity = label;
                    break;
                }
            }
        } else {
            // fallback checking
            if (state.scenario.water_level >= 3.0) floodSeverity = "CRITICAL";
            else if (state.scenario.water_level >= 2.0) floodSeverity = "HIGH";
            else if (state.scenario.water_level >= 1.0) floodSeverity = "MEDIUM";

            if (state.scenario.unrest_level >= 80) unrestSeverity = "HIGH";
            else if (state.scenario.unrest_level >= 50) unrestSeverity = "MEDIUM";
        }

        floodEl.innerText = `${state.scenario.water_level.toFixed(1)}m (${floodSeverity})`;
        floodEl.className = floodSeverity === "CRITICAL" ? "value text-red bold" : (floodSeverity === "HIGH" ? "value text-amber bold" : "value text-cyan");

        unrestEl.innerText = `${Math.round(state.scenario.unrest_level)} (${unrestSeverity})`;
        unrestEl.className = unrestSeverity === "HIGH" ? "value text-red bold" : (unrestSeverity === "MEDIUM" ? "value text-amber bold" : "value text-green");

        document.getElementById('context-teams-val').innerText = "2";
        document.getElementById('context-hospitals-val').innerText = "2";

        const rainVal = document.getElementById('telemetry-rainfall-val');
        const rainFill = document.getElementById('telemetry-rainfall-fill');
        if (rainVal) rainVal.innerText = `${state.scenario.rainfall} mm/h`;
        if (rainFill) rainFill.style.width = `${Math.min(100, state.scenario.rainfall)}%`;
        
        const waterVal = document.getElementById('telemetry-water-val');
        const waterFill = document.getElementById('telemetry-water-fill');
        if (waterVal) waterVal.innerText = `${state.scenario.water_level}m`;
        if (waterFill) waterFill.style.width = `${Math.min(100, (state.scenario.water_level / 5.0) * 100)}%`;
        
        const crowdVal = document.getElementById('telemetry-crowd-val');
        const crowdFill = document.getElementById('telemetry-crowd-fill');
        if (crowdVal) crowdVal.innerText = state.scenario.crowd_size.toLocaleString();
        if (crowdFill) crowdFill.style.width = `${Math.min(100, (state.scenario.crowd_size / 4000) * 100)}%`;
        
        const unrestVal = document.getElementById('telemetry-unrest-val');
        const unrestFill = document.getElementById('telemetry-unrest-fill');
        if (unrestVal) unrestVal.innerText = `${state.scenario.unrest_level}%`;
        if (unrestFill) unrestFill.style.width = `${state.scenario.unrest_level}%`;
        
        const descVal = document.getElementById('telemetry-desc-val');
        if (descVal) descVal.innerText = state.scenario.description;
    }

    // 5. Draft Strategies
    if (state.plans && Object.keys(state.plans).length > 0) {
        noPlansMsg.classList.add('hidden');
        plansContainer.classList.remove('hidden');

        for (const name of ['Fastest', 'Safest', 'Balanced']) {
            const plan = state.plans[name];
            if (!plan) continue;

            document.getElementById(`plan-${name}-desc`).innerText = plan.description;
            document.getElementById(`plan-${name}-time`).innerText = `${plan.duration_hours} hours`;
            document.getElementById(`plan-${name}-cost`).innerText = `$${plan.cost.toLocaleString()}`;
            document.getElementById(`plan-${name}-coverage`).innerText = `${plan.coverage_percentage}%`;

            const stepsOl = document.getElementById(`plan-${name}-steps`);
            stepsOl.innerHTML = '';
            plan.steps.forEach(step => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="bold text-dim">[${step.resource}]</span> ${step.action} <span class="text-cyan font-small">(${step.estimated_duration_hours}h)</span>`;
                stepsOl.appendChild(li);
            });
        }
    }

    // 6. Plan Comparison Grid
    if (state.plans && state.evaluations && Object.keys(state.evaluations).length > 0) {
        const noEvalMsg = document.getElementById('no-eval-msg');
        const evalContainer = document.getElementById('evaluation-container');
        if (noEvalMsg) noEvalMsg.classList.add('hidden');
        if (evalContainer) evalContainer.classList.remove('hidden');

        for (const name of ['Fastest', 'Safest', 'Balanced']) {
            const plan = state.plans[name];
            const evalData = state.evaluations[name];
            if (!plan || !evalData) continue;

            // Update row fields with qualitative labels
            document.getElementById(`eval-${name}-time`).innerText = `${Math.round(plan.duration_hours)}h`;
            
            // Risk mapping
            let riskLabel = "Med";
            if (plan.risk_level > 3.5) riskLabel = "High";
            else if (plan.risk_level < 2.0) riskLabel = "Low";
            document.getElementById(`eval-${name}-risk`).innerText = riskLabel;
            
            // Cost mapping
            let costLabel = "Med";
            if (plan.cost > 200000) costLabel = "High";
            else if (plan.cost < 150000) costLabel = "Low";
            document.getElementById(`eval-${name}-cost`).innerText = costLabel;
            
            // Coverage mapping
            let coverageLabel = "Medium";
            if (plan.coverage_percentage >= 95) coverageLabel = "High";
            else if (plan.coverage_percentage < 85) coverageLabel = "Low";
            document.getElementById(`eval-${name}-coverage`).innerText = coverageLabel;
            
            // Aggregate score
            document.getElementById(`eval-${name}-agg`).innerText = Math.round(evalData.aggregate_score);
        }

        const valBadge = document.getElementById('validation-badge');
        if (state.validation) {
            valBadge.innerText = state.validation.valid ? 'PASSED AUDIT' : 'FAILED AUDIT';
            valBadge.className = state.validation.valid ? 'audit-badge badge-green' : 'audit-badge badge-red';
            
            const issuesList = document.getElementById('validation-issues-list');
            issuesList.innerHTML = '';
            state.validation.issues.forEach(issue => {
                const li = document.createElement('li');
                li.innerText = issue;
                issuesList.appendChild(li);
            });
        }
    }

    // 7. Decision & Escalations Panel
    if (state.status === "no_feasible_plan" && state.current_decision) {
        if (fallbackEscalationAlert) fallbackEscalationAlert.classList.remove('hidden');
        if (decisionMainPanel) decisionMainPanel.classList.add('hidden');
        
        const dec = state.current_decision;
        const fallbackValEl = document.getElementById('escalation-fallback-val');
        if (fallbackValEl) {
            fallbackValEl.innerText = state.fallback || 'Partial evacuation with delayed full deployment until escorts or air bridges are established.';
        }
        
        const alertRejUl = document.getElementById('escalation-reasons-list') || document.getElementById('escalation-rejections-list');
        if (alertRejUl) {
            alertRejUl.innerHTML = '';
            if (state.validation && state.validation.issues && state.validation.issues.length > 0) {
                state.validation.issues.forEach(issue => {
                    const li = document.createElement('li');
                    li.innerText = issue;
                    alertRejUl.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.innerText = dec.justification;
                alertRejUl.appendChild(li);
            }
        }
        
        // Remove selection highlight classes
        for (const name of ['Fastest', 'Safest', 'Balanced']) {
            const card = document.getElementById(`card-${name}`);
            if (card) card.classList.remove('selected');
        }
    } else if (state.current_decision) {
        if (fallbackEscalationAlert) fallbackEscalationAlert.classList.add('hidden');
        if (decisionMainPanel) decisionMainPanel.classList.remove('hidden');
        if (noDecisionMsg) noDecisionMsg.classList.add('hidden');
        if (decisionContent) decisionContent.classList.remove('hidden');

        const dec = state.current_decision;
        document.getElementById('decision-plan-name').innerText = dec.selected_plan.toUpperCase();
        document.getElementById('decision-confidence-val').innerText = `${Math.round(dec.confidence * 100)}%`;

        // Update STATUS row
        const statusEl = document.getElementById('decision-status-text');
        if (state.disruption_event) {
            let eventLabel = "Bridge Collapse";
            if (state.disruption_event === "riot_outbreak") eventLabel = "Riot Outbreak";
            if (state.disruption_event === "severe_downpour") eventLabel = "Severe Downpour";
            statusEl.innerText = `Replanned after ${eventLabel}`;
            statusEl.className = "status-value text-red bold animate-pulse";
        } else {
            statusEl.innerText = "Nominal Execution";
            statusEl.className = "status-value text-green bold";
        }

        // Explainability summarize block lists
        const whyUl = document.getElementById('decision-why-list');
        whyUl.innerHTML = '';
        dec.why_this_plan.forEach(item => {
            const li = document.createElement('li');
            li.innerText = item;
            whyUl.appendChild(li);
        });

        const tradeoffsUl = document.getElementById('decision-tradeoffs-list');
        tradeoffsUl.innerHTML = '';
        dec.trade_offs.forEach(item => {
            const li = document.createElement('li');
            li.innerText = item;
            tradeoffsUl.appendChild(li);
        });

        // Rankings Leaderboard Grid
        const leaderboard = document.getElementById('leaderboard-container');
        leaderboard.innerHTML = '';
        dec.ranking.forEach(rankInfo => {
            const row = document.createElement('div');
            let medalClass = 'medal-bronze';
            if (rankInfo.rank === 1) medalClass = 'medal-gold';
            if (rankInfo.rank === 2) medalClass = 'medal-silver';
            
            row.className = `leaderboard-row rank-${rankInfo.rank}`;
            row.innerHTML = `
                <div class="row-left">
                    <span class="rank-badge ${medalClass}">#${rankInfo.rank}</span>
                    <span class="bold ml-2">${rankInfo.plan} Strategy</span>
                </div>
                <div class="row-right font-mono text-cyan bold">Score: ${rankInfo.score}</div>
            `;
            leaderboard.appendChild(row);
        });

        // Justification reasoning
        document.getElementById('decision-justification-val').innerText = dec.justification;

        // Precedent memory narrative
        const memNarrative = dec.memory_narrative;
        if (memNarrative && memNarrative.memory_used) {
            document.getElementById('decision-memory-case').innerText = memNarrative.reference_case;
            document.getElementById('decision-memory-narrative').innerText = memNarrative.impact;
        } else {
            document.getElementById('decision-memory-case').innerText = 'None';
            document.getElementById('decision-memory-narrative').innerText = memNarrative ? memNarrative.impact : 'No history matched.';
        }

        // Alternative rejections list
        const rejList = document.getElementById('rejected-plans-list');
        rejList.innerHTML = '';
        dec.rejected_plans.forEach(planInfo => {
            const li = document.createElement('li');
            li.innerHTML = `<span class="bold text-red">[Rejected: ${planInfo.plan}]</span> ${planInfo.reason}`;
            rejList.appendChild(li);
        });

        // Highlight selected plan card
        for (const name of ['Fastest', 'Safest', 'Balanced']) {
            const card = document.getElementById(`card-${name}`);
            if (card) {
                if (name === dec.selected_plan) {
                    card.classList.add('selected');
                } else {
                    card.classList.remove('selected');
                }
            }
        }
    }

    // 8. Disruption comparison rendering
    if (state.disruption_event && state.original_decision && state.current_decision) {
        renderReplanComparison(state, state.disruption_event);
    } else {
        if (replanComparisonCard) replanComparisonCard.classList.add('hidden');
        if (replanEmptyCard) replanEmptyCard.classList.remove('hidden');
    }
}

// RENDER SYSTEM EXECUTION TIMELINE WITH ITERATIONS / FAILURE TAGS
function renderTimeline(state) {
    const activeStep = state.active_step;
    const mode = state.execution_mode;
    const status = state.status;
    
    const metrics = state.performance_metrics || {};
    const failures = metrics.validation_failures || 0;
    const iterations = metrics.iterations || 0;

    for (let i = 1; i <= 6; i++) {
        const stepNode = document.getElementById(`step-node-${i}`);
        const badge = stepNode.querySelector('.step-status');
        
        stepNode.className = 'timeline-step';

        if (status === 'stopped') {
            badge.innerText = 'Cancelled';
            badge.className = 'step-status text-dim';
            continue;
        }

        if (i < activeStep || (i === 6 && status === 'completed')) {
            // Completed step
            stepNode.classList.add('completed');
            badge.innerText = '✓';
            badge.className = 'step-status text-green bold';
            
            // Loop modifications display on completed tags exactly matching user prompt format
            if (i === 3 && iterations > 1) {
                badge.innerText = `✓ (${iterations} iterations)`;
            }
            if (i === 4 && failures > 0) {
                badge.innerText = `✓ (${failures} fail → 1 pass)`;
            }
        } else if (i === activeStep && status !== 'completed' && status !== 'no_feasible_plan') {
            // Active Step
            if (mode === 'paused') {
                stepNode.classList.add('active');
                badge.innerText = '⏸ Paused';
                badge.className = 'step-status text-amber bold';
            } else {
                stepNode.classList.add('active');
                badge.innerText = '⚡ Processing...';
                badge.className = 'step-status text-cyan bold';
            }
        } else if (i === activeStep && status === 'no_feasible_plan') {
            // Falled validation boundary step
            stepNode.classList.add('failed');
            badge.innerText = '❌ Limit Breached';
            badge.className = 'step-status text-red bold';
        } else {
            // Pending Step
            badge.innerText = 'Pending';
            badge.className = 'step-status text-dim';
        }
    }
}

// RENDER COGNITIVE MESSAGE LOGS
function renderLogs(logs) {
    if (!logs || logs.length === 0) return;

    terminalLogs.innerHTML = '';
    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'log-entry';

        const agentName = `[${log.agent}]`;
        
        // Map technical intents to friendly human-readable ones
        let friendlyIntent = log.intent;
        const intentMapping = {
            'initial plan generation': 'Generate evacuation strategies',
            'refining plan due to budget/safety violations': 'Generate evacuation strategies',
            'refining plan due to evaluator feedback': 'Generate evacuation strategies',
            'evaluating plan parameters': 'Compare strategies',
            're-scoring refined plan parameters': 'Compare strategies',
            'auditing plan constraints compliance': 'Audit strategies against constraints',
            'consulting empirical memory library': 'Retrieve historical precedent logs',
            'resolving strategic recommendation': 'Select optimal response plan',
            'injecting new incident disruption parameters': 'Inject environmental disruption event',
            'Generate simulated weather and social telemetry based on selected scenario variant': 'Collect disaster and social indicators',
            'Evaluate threat boundaries and compute normalized Crisis Severity Index': 'Evaluate threat boundaries and compute severity index'
        };
        if (intentMapping[log.intent]) {
            friendlyIntent = intentMapping[log.intent];
        }

        const intentText = friendlyIntent ? `<div class="log-intent"><span class="label text-dim">Intent:</span> ${friendlyIntent}</div>` : '';
        const reasoningText = log.reasoning ? `<div class="log-reason">&gt; <span class="label text-dim">Reasoning:</span> ${log.reasoning}</div>` : '';
        const impactText = log.impact ? `<div class="log-impact"><span class="label text-dim">Impact:</span> ${log.impact}</div>` : '';
        
        let dataText = '';
        if (log.data && Object.keys(log.data).length > 0) {
            let logData = JSON.stringify(log.data, null, 2);
            if (logData.length > 400) {
                logData = logData.slice(0, 400) + "\n  ... [truncated payload for display]";
            }
            dataText = `<pre class="log-data">${logData}</pre>`;
        }

        // Color-coding log agent text
        let agentClass = 'text-cyan';
        if (log.agent === 'SignalAgent') agentClass = 'text-cyan';
        if (log.agent === 'DetectionAgent') agentClass = 'text-amber';
        if (log.agent === 'PlannerAgent') agentClass = 'text-cyan';
        if (log.agent === 'ValidationAgent') agentClass = 'text-red';
        if (log.agent === 'MemoryAgent') agentClass = 'text-purple';
        if (log.agent === 'DecisionAgent') agentClass = 'text-purple';

        div.innerHTML = `
            <div class="log-agent ${agentClass}">${agentName} <span class="text-dim font-small" style="float: right;">${log.timestamp}</span></div>
            ${intentText}
            ${reasoningText}
            ${impactText}
            ${dataText}
        `;

        terminalLogs.appendChild(div);
    });

    terminalLogs.scrollTop = terminalLogs.scrollHeight;
}

// RENDER REPLAN MATRIX
function renderReplanComparison(state, eventType) {
    if (!state.original_decision || !state.current_decision) return;

    replanComparisonCard.classList.remove('hidden');
    replanEmptyCard.classList.add('hidden');

    // Hide feedback toast after replanning resolves
    if (disruptionFeedbackMsg) {
        disruptionFeedbackMsg.style.display = 'none';
    }

    const eventNames = {
        'bridge_collapse': 'Bridge Collapse',
        'riot_outbreak': 'Riot Outbreak',
        'severe_downpour': 'Severe Downpour'
    };

    document.getElementById('disruption-name-val').innerText = eventNames[eventType] || eventType;

    const before = state.original_decision;
    const after = state.current_decision;

    document.getElementById('replan-before-plan').innerText = `${before.selected_plan} Plan`;
    document.getElementById('replan-before-conf').innerText = `${Math.round(before.confidence * 100)}%`;

    document.getElementById('replan-after-plan').innerText = `${after.selected_plan} Plan`;
    document.getElementById('replan-after-conf').innerText = `${Math.round(after.confidence * 100)}%`;

    document.getElementById('replan-adaptation-reason').innerText = after.justification;
}
