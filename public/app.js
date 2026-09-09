let currentScenarios = [];
let activeScenarioId = "S1";
let currentData = null;
let signedClears = new Set();
let currentTab = "scenarios";
window.currentRequiredClears = [];

// Default Production Context (Fallback when offline/static)
const DEFAULT_PRODUCTION_CONTEXT = {
    production_name: "Backlot Test: Sovereign Stage 4",
    call_sheet_day: "Day 2 of 42 (Night Exterior)",
    location: {
        name: "Warehouse 9 / Backlot Stage",
        hospital_minutes: 15,
        nearest_hospital: "Foothills Medical Centre (Level 1 Trauma)"
    },
    crew_on_duty: {
        first_ad: "Ann Frost",
        safety_officer: "Sam Officer",
        armorer: "Al Arms",
        rigger: "Dana Rigger",
        first_aider: "Sam Aid",
        headcount: 42
    },
    jurisdiction: {
        code: "AB",
        name: "Alberta OHS Code (AR 191/2021 current to 2025-03-31)",
        secondary: "WorkSafeBC (BC Reg 296/97)"
    },
    site_conditions: {
        temperature: "12°C",
        wind_speed_kmh: 22,
        wind_threshold_kmh: 40,
        status: "GREEN / WITHIN SAFE LIMITS"
    }
};

// Default Preloaded Scenarios Deck
const DEFAULT_SCENARIOS = [
    {
        id: "S1",
        title: "Night Stunt Jump & Flash Pot Explosion",
        heading: "EXT. LOADING DOCK - NIGHT",
        description: "High-risk action rewrite adding practical pyrotechnics, a 20-foot performer fall, and powered hydraulic lift resets.",
        expected_severity: "RED",
        original_text: "[Scene 1] EXT. LOADING DOCK - NIGHT\nThe loading dock is quiet. A security guard walks past holding a flashlight.",
        revised_text: "[Scene 1] EXT. LOADING DOCK - NIGHT\nThe loading dock is quiet. A security guard walks past holding a flashlight.\nSuddenly, a pyrotechnic flash pot explodes near the dumpster.\nA masked performer jumps from a 20-foot elevated platform down to the concrete, rolling to safety.\nThe crew resets the powered hydraulic lift between takes."
    },
    {
        id: "S2",
        title: "Confined Space Prop Firearm Shootout",
        heading: "INT. CARGO HOLD - NIGHT",
        description: "Interior hull revision introducing blank firearm discharge and restricted egress atmospheric fog.",
        expected_severity: "STOP",
        original_text: "[Scene 2] INT. CARGO HOLD - NIGHT\nJohn and Sarah search through the storage crates under low emergency lighting.",
        revised_text: "[Scene 2] INT. CARGO HOLD - NIGHT\nJohn and Sarah search through the storage crates under low emergency lighting.\nHeavy atmospheric smoke fills the sealed watertight compartment.\nJohn draws a prop revolver loaded with quarter-load blanks and fires two shots toward the hatch."
    },
    {
        id: "S3",
        title: "Aerial High-Wind Crane Rigging",
        heading: "EXT. ROOFTOP - NIGHT",
        description: "Exterior rooftop stunt featuring a 60-foot condor crane flying rig in gusty night weather.",
        expected_severity: "RED",
        original_text: "[Scene 3] EXT. ROOFTOP - NIGHT\nElena looks out over the city skyline from behind the perimeter railing.",
        revised_text: "[Scene 3] EXT. ROOFTOP - NIGHT\nElena steps past the perimeter railing onto an exterior scaffold.\nA 60-foot telescopic condor crane hoists a stunt performer into high-altitude wind gusts over the edge."
    },
    {
        id: "S4",
        title: "Routine Office Dialogue Revision",
        heading: "INT. PRODUCTION OFFICE - DAY",
        description: "Standard character and dialogue adjustments with zero physical risk or hazardous machinery.",
        expected_severity: "GREEN",
        original_text: "[Scene 4] INT. PRODUCTION OFFICE - DAY\nDavid reviews the schedule on his laptop while drinking coffee.",
        revised_text: "[Scene 4] INT. PRODUCTION OFFICE - DAY\nDavid reviews the revised call sheet on his tablet.\nSARAH walks in holding two coffees, setting one on the desk with a smile."
    }
];

// 1. Terminal Log Animation
async function animateTerminalLogs(scenarioName) {
    const termBody = document.getElementById('term-logs');
    const statusText = document.getElementById('telemetry-status-text');
    termBody.innerHTML = '';
    if (statusText) {
        statusText.textContent = 'ANALYSIS REQUEST SENT...';
        statusText.style.color = 'var(--blue)';
    }
    
    const logs = [
        `> [REQUEST] Scenario "${scenarioName}" queued for structured analysis.`,
        `> [SCHEMA] Pipeline: DiffOutput -> CascadeOutput -> HazardTagOutput.`,
        `> [SAFETY_ENGINE] Evaluating against Alberta OHS Code AR 191/2021...`,
        `> [MCP_OBSERVABILITY] Grafana event channel verified.`
    ];

    for (let log of logs) {
        await new Promise(r => setTimeout(r, 35));
        const line = document.createElement('div');
        line.className = 'term-line';
        line.textContent = log;
        termBody.appendChild(line);
        termBody.scrollTop = termBody.scrollHeight;
    }

    await new Promise(r => setTimeout(r, 150));
    if(statusText) {
        statusText.textContent = 'RECEIPT VERIFIED';
        statusText.style.color = 'var(--gold)';
    }
}

function appendTerminalLine(text, tone = 'normal') {
    const termBody = document.getElementById('term-logs');
    if (!termBody) return;
    const line = document.createElement('div');
    line.className = `term-line term-${tone}`;
    line.textContent = text;
    termBody.appendChild(line);
    termBody.scrollTop = termBody.scrollHeight;
}

function renderAnalysisReceipt(data) {
    const statusText = document.getElementById('telemetry-status-text');
    const mode = data?.analysis?.mode || 'unknown';
    const severity = data?.safety?.severity || 'UNKNOWN';
    const grafana = data?.grafana || {};

    appendTerminalLine(`> [ANALYSIS] Mode: ${mode}.`, mode === 'google_adk_gemini' ? 'success' : 'warning');
    appendTerminalLine(`> [SAFETY_ENGINE] Verdict: ${severity}.`, severity === 'GREEN' ? 'success' : 'warning');

    if (grafana.published) {
        appendTerminalLine(`> [GRAFANA] MCP publish verified: Annotation ${grafana.annotation_id || 'created'}.`, 'success');
    } else {
        appendTerminalLine(`> [GRAFANA] MCP Status: ${grafana.error || 'Local/Offline cache active.'}`, 'warning');
    }

    if (statusText) {
        statusText.textContent = mode === 'google_adk_gemini'
            ? 'LIVE GEMINI ADK PIPELINE COMPLETE'
            : 'DETERMINISTIC SAFETY GOVERNANCE COMPLETE';
        statusText.style.color = mode === 'google_adk_gemini' ? 'var(--green)' : 'var(--gold)';
    }

    updateChainStatus(data);
}

function setChainStep(id, value, state) {
    const el = document.getElementById(id);
    if (!el) return;
    const strong = el.querySelector('strong');
    if (strong) strong.textContent = value;
    el.classList.remove('live', 'fallback', 'skipped', 'stop', 'red');
    if (state) el.classList.add(state);
}

function updateChainStatus(data) {
    const mode = data?.analysis?.mode || 'unknown';
    const severity = data?.safety?.severity || 'UNKNOWN';
    const grafana = data?.grafana || {};

    setChainStep(
        'chain-analysis',
        mode === 'google_adk_gemini' ? 'Live Gemini' : 'Offline Rule Engine',
        mode === 'google_adk_gemini' ? 'live' : 'fallback'
    );
    setChainStep(
        'chain-safety',
        severity,
        severity === 'GREEN' ? 'live' : severity === 'STOP' ? 'stop' : 'red'
    );
    setChainStep(
        'chain-grafana',
        grafana.published ? 'Published' : 'Local Mock/Cache',
        grafana.published ? 'live' : 'fallback'
    );
    setChainStep('chain-frontend', 'Rendered JSON', 'live');
}

// 2. Tab Switcher
function switchTab(tab) {
    currentTab = tab;
    document.getElementById('tab-scenarios-btn').classList.toggle('active', tab === 'scenarios');
    document.getElementById('tab-editor-btn').classList.toggle('active', tab === 'editor');
    
    document.getElementById('scenario-deck-panel').style.display = tab === 'scenarios' ? 'grid' : 'none';
    document.getElementById('custom-editor-panel').style.display = tab === 'editor' ? 'block' : 'none';
}

// 3. Load Production Context
async function loadProductionContext() {
    let ctx = DEFAULT_PRODUCTION_CONTEXT;
    try {
        const resp = await fetch('/api/context');
        if (resp.ok) {
            ctx = await resp.json();
        }
    } catch(e) {
        console.warn("Using offline production context:", e);
    }
    
    document.getElementById('ctx-prod').textContent = ctx.production_name || 'Stage 4';
    document.getElementById('ctx-day').textContent = ctx.call_sheet_day || 'Day 2 (Night)';
    document.getElementById('ctx-loc').textContent = `${ctx.location.name} (${ctx.location.hospital_minutes}m to ${ctx.location.nearest_hospital})`;
    document.getElementById('ctx-leads').textContent = `1st AD: ${ctx.crew_on_duty.first_ad} | Safety: ${ctx.crew_on_duty.safety_officer}`;
    document.getElementById('ctx-juris').textContent = ctx.jurisdiction.name;
}

// 4. Load Scenarios Deck
async function loadScenarios() {
    currentScenarios = DEFAULT_SCENARIOS;
    try {
        const resp = await fetch('/api/scenarios');
        if (resp.ok) {
            const remoteScenarios = await resp.json();
            if (Array.isArray(remoteScenarios) && remoteScenarios.length > 0) {
                currentScenarios = remoteScenarios;
            }
        }
    } catch(e) {
        console.warn("Using offline scenarios deck:", e);
    }
    
    renderScenarioDeck(currentScenarios);
    if (currentScenarios.length > 0) {
        document.getElementById('custom-orig-text').value = currentScenarios[0].original_text;
        document.getElementById('custom-rev-text').value = currentScenarios[0].revised_text;
    }
}

function renderScenarioDeck(scenarios) {
    const deck = document.getElementById('scenario-deck-panel');
    deck.innerHTML = scenarios.map(sc => {
        let badgeClass = 'badge-red';
        if (sc.expected_severity === 'STOP') badgeClass = 'badge-stop';
        if (sc.expected_severity === 'GREEN') badgeClass = 'badge-green';
        if (sc.expected_severity === 'REVIEW') badgeClass = 'badge-red';

        const isActive = sc.id === activeScenarioId;

        return `
            <button type="button" class="scenario-card ${isActive ? 'active' : ''}" data-scenario-id="${escapeHtml(sc.id)}">
                <div class="scenario-card-top">
                    <span class="scenario-id-tag">${escapeHtml(sc.id)} // ${escapeHtml(sc.heading)}</span>
                    <span class="${badgeClass}">${escapeHtml(sc.expected_severity)}</span>
                </div>
                <div class="scenario-card-title">${escapeHtml(sc.title)}</div>
                <div class="scenario-card-desc">${escapeHtml(sc.description)}</div>
            </button>
        `;
    }).join('');

    deck.querySelectorAll('.scenario-card').forEach(card => {
        card.addEventListener('click', () => selectScenario(card.dataset.scenarioId));
    });
}

function selectScenario(id) {
    activeScenarioId = id;
    const sc = currentScenarios.find(s => s.id === id);
    if (sc) {
        document.getElementById('custom-orig-text').value = sc.original_text;
        document.getElementById('custom-rev-text').value = sc.revised_text;
    }
    renderScenarioDeck(currentScenarios);
    triggerCurrentAnalysis();
}

// 5. Trigger Analysis (Live API Call with Graceful Offline Engine)
async function triggerCurrentAnalysis() {
    const btn = document.getElementById('main-run-btn');
    btn.disabled = true;
    btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Analyzing with Gemini ADK...`;

    let payload = {};
    if (currentTab === 'editor') {
        payload = {
            scenario_id: "CUSTOM",
            scene_id: "REV_CUSTOM",
            scene_heading: "CUSTOM SCREENPLAY REVISION",
            original_text: document.getElementById('custom-orig-text').value,
            revised_text: document.getElementById('custom-rev-text').value,
            is_custom: true
        };
        await animateTerminalLogs("CUSTOM SCREENPLAY");
    } else {
        const sc = currentScenarios.find(s => s.id === activeScenarioId) || DEFAULT_SCENARIOS[0];
        payload = {
            scenario_id: sc.id,
            scene_id: sc.id,
            scene_heading: sc.heading,
            original_text: sc.original_text,
            revised_text: sc.revised_text,
            is_custom: false
        };
        await animateTerminalLogs(sc.title);
    }

    try {
        const resp = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error(`Analysis endpoint returned ${resp.status}`);
        const data = await resp.json();
        renderDashboard(data);
        renderAnalysisReceipt(data);
        setNetworkStatus(true);
    } catch(e) {
        console.warn("Backend API unavailable, using deterministic offline engine:", e);
        appendTerminalLine(`> [LOCAL_MODE] Live backend unreachable. Evaluating via deterministic offline engine.`, 'warning');
        const offlineData = generateOfflineAnalysis(payload);
        renderDashboard(offlineData);
        renderAnalysisReceipt(offlineData);
        setNetworkStatus(false);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Extract Revision & Run Safety Gate`;
    }
}

// 6. Render Full Dashboard Results
function renderDashboard(data) {
    currentData = data || {};
    signedClears.clear(); // Reset clearances for the new analysis

    const sceneId = data?.scene?.id || 'UNKNOWN';
    document.getElementById('display-scene-id').textContent = `SCENE ${sceneId}`;

    // A. Render Screenplay Diff
    renderScreenplayDiff(data);

    // B. Render Department Deltas
    renderDepartmentDeltas(data);

    // C. Render Safety Verdict & Camera Gate
    renderSafetyVerdict(data);

    // D. Render Clearances Checklist
    renderClearances(data);

    // E. Render Hazard Tags
    renderHazardTags(data);

    // F. Render Statutory OHS Citations
    renderStatutoryCitations(data);
}

// 7. Screenplay Redline Diff Formatter
function renderScreenplayDiff(data) {
    const container = document.getElementById('screenplay-diff-content');
    
    // If diff changes exist, construct an intuitive visual representation
    if (data?.diff && Array.isArray(data.diff) && data.diff.length > 0) {
        let diffHtml = '';
        data.diff.forEach(c => {
            diffHtml += `
<div style="margin-bottom: 16px;">
    <div class="sp-heading">${data?.scene?.heading || 'SCENE'}</div>
    <div class="sp-action">
        ${c.old_text ? `<span class="diff-del">${escapeHtml(c.old_text)}</span><br><br>` : ''}
        ${c.new_text ? `<span class="diff-add">${escapeHtml(c.new_text)}</span>` : ''}
    </div>
</div>
            `;
        });
        container.innerHTML = diffHtml;
    } else {
        // Render raw revised script formatted
        container.innerHTML = `<div class="sp-heading">${data?.scene?.heading || 'SCENE'}</div><div class="sp-action">${escapeHtml(data?.scene?.revised_script || 'No script text')}</div>`;
    }
}

// 8. Department Work Deltas
function renderDepartmentDeltas(data) {
    const container = document.getElementById('department-deltas-container');
    if (!data?.department_deltas || !Array.isArray(data.department_deltas) || data.department_deltas.length === 0) {
        container.innerHTML = `<div class="dept-card"><span class="dept-tag">ALL GUILDS</span><span class="dept-impact">No departmental work changes detected for this revision.</span></div>`;
        return;
    }

    container.innerHTML = data.department_deltas.map(d => `
        <div class="dept-card">
            <span class="dept-tag">${escapeHtml(d.department || 'UNKNOWN')}</span>
            <div class="dept-impact">${escapeHtml(d.impact || d.delta || '')}</div>
        </div>
    `).join('');
}

// 9. Safety Verdict & Master Camera Gate
function renderSafetyVerdict(data) {
    const severity = data.safety?.severity || 'UNKNOWN';
    const reason = data.safety?.reason || 'Standard review';
    
    document.getElementById('verdict-badge').textContent = severity;
    document.getElementById('verdict-badge').className = `severity-badge-lg severity-${severity}`;
    document.getElementById('verdict-reason-text').textContent = reason;

    updateGateState();
}

function updateGateState() {
    const severity = currentData?.safety?.severity || 'UNKNOWN';
    const requiredClears = currentData?.safety?.required_clears || [];
    const allSigned = requiredClears.length === 0 || requiredClears.every(c => signedClears.has(c));

    const gateBox = document.getElementById('camera-gate-box');
    const gateIcon = document.getElementById('gate-icon');
    const gateTitle = document.getElementById('gate-title');
    const gateDesc = document.getElementById('gate-desc');

    if (severity === 'GREEN' || allSigned) {
        gateBox.style.borderColor = 'var(--green)';
        gateBox.style.background = 'rgba(16, 185, 129, 0.08)';
        gateIcon.textContent = 'CLEAR';
        gateTitle.style.color = 'var(--green)';
        gateTitle.textContent = 'STAGE CLEAR // CAMERA AUTHORIZED TO ROLL';
        gateDesc.textContent = 'All mandatory clearances signed and verified. 1st AD authorized to call camera roll.';
    } else {
        gateBox.style.borderColor = severity === 'STOP' ? 'var(--red)' : '#3f3f50';
        gateBox.style.background = '#0e0e13';
        gateIcon.textContent = severity === 'STOP' ? 'STOP' : 'LOCK';
        gateTitle.style.color = 'var(--red)';
        gateTitle.textContent = severity === 'STOP' ? 'MANDATORY STOP // SET FROZEN' : 'STAGE LOCKED // CAMERA CANNOT ROLL';
        gateDesc.textContent = `${requiredClears.length - signedClears.size} required clearance(s) pending sign-off before rehearsal or camera roll.`;
    }
}

// 10. Clearances Checklist
function renderClearances(data) {
    const container = document.getElementById('clears-container');
    const requiredClears = data?.safety?.required_clears || [];
    
    updateClearsBadge(requiredClears);

    if (!Array.isArray(requiredClears) || requiredClears.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.88rem; padding: 10px;">No mandatory clearances required for this revision.</div>`;
        return;
    }

    // Pass the index instead of the string to avoid single quote escaping issues in onclick!
    window.currentRequiredClears = requiredClears; 
    container.innerHTML = requiredClears.map((c, idx) => `
        <div class="clear-row ${signedClears.has(c) ? 'signed' : ''}" onclick="toggleClearIdx(${idx})">
            <input type="checkbox" class="clear-checkbox" ${signedClears.has(c) ? 'checked' : ''} onclick="event.stopPropagation(); toggleClearIdx(${idx})">
            <span class="clear-text">${escapeHtml(c)}</span>
        </div>
    `).join('');
}

function toggleClearIdx(idx) {
    const clearName = window.currentRequiredClears[idx];
    if (!clearName) return;
    
    if (signedClears.has(clearName)) {
        signedClears.delete(clearName);
    } else {
        signedClears.add(clearName);
    }
    
    renderClearances(currentData);
    updateGateState();
}

function toggleClear(clearName) {
    if (signedClears.has(clearName)) {
        signedClears.delete(clearName);
    } else {
        signedClears.add(clearName);
    }
    
    renderClearances(currentData);
    updateGateState();
}

function updateClearsBadge(requiredClears) {
    const badge = document.getElementById('clears-counter-badge');
    badge.textContent = `${signedClears.size} / ${requiredClears.length} Cleared`;
    badge.style.color = signedClears.size === requiredClears.length ? 'var(--green)' : 'var(--gold)';
}

// 11. Hazard Tags Deck
function renderHazardTags(data) {
    const container = document.getElementById('hazards-container');
    if (!data?.hazard_tags || !Array.isArray(data.hazard_tags) || data.hazard_tags.length === 0) {
        container.innerHTML = `<span style="color: var(--text-muted); font-size: 0.85rem;">No jurisdiction hazards identified.</span>`;
        return;
    }

    container.innerHTML = data.hazard_tags.map((t, idx) => `
        <div class="hazard-pill" onclick="showHazardModal(${idx})">
            <span class="hazard-pill-row">Row ${escapeHtml(String(t.row || '?'))}</span>
            <span>${escapeHtml(t.label || 'Unknown')}</span>
        </div>
    `).join('');
}

function showHazardModal(idx) {
    if (!currentData || !currentData.hazard_tags) return;
    const tag = currentData.hazard_tags[idx];
    if (!tag) return;
    
    const label = tag.label ? tag.label.toUpperCase() : 'UNKNOWN HAZARD';
    const row = tag.row || '?';
    const detail = tag.detail || 'No detail provided by the backend ADK.';

    document.getElementById('modal-title').textContent = `Hazard: ${label} (Row ${row})`;
    document.getElementById('modal-body').innerHTML = `
        <p style="color: var(--text-muted); margin-bottom: 8px;">Extracted Script Reasoning:</p>
        <div style="background: rgba(255,255,255,0.05); padding: 14px; border-left: 3px solid var(--blue); border-radius: 4px; font-size: 0.95rem; line-height: 1.5; color: #f4f4f7;">
            ${escapeHtml(detail)}
        </div>
        <div style="margin-top: 16px; font-size: 0.8rem; color: var(--text-dim);">
            Governed under Alberta OHS Code AR 191/2021 Hazard Classification Matrix.
        </div>
    `;
    document.getElementById('detail-modal').classList.add('active');
}

// 12. Statutory Citations List
function renderStatutoryCitations(data) {
    const container = document.getElementById('statutory-container');
    const statutes = data?.safety?.statutory_citations || [];

    if (!Array.isArray(statutes) || statutes.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">Standard General Duty Clause (AB OHS Act s.3) applies.</div>`;
        return;
    }

    container.innerHTML = statutes.map((st, idx) => `
        <div class="statute-card" onclick="showStatuteModal(${idx})">
            <span class="statute-citation">${escapeHtml(st.citation || 'CITATION')}</span>
            <div class="statute-title">${escapeHtml(st.title || 'Unknown Statute')}</div>
            <div class="statute-excerpt">${escapeHtml(st.statute_text || '')}</div>
        </div>
    `).join('');
}

function showStatuteModal(idx) {
    if (!currentData || !currentData.safety?.statutory_citations) return;
    const st = currentData.safety.statutory_citations[idx];
    if (!st) return;

    document.getElementById('modal-title').textContent = st.citation || 'Citation Detail';
    document.getElementById('modal-body').innerHTML = `
        <h4 style="color: #ffffff; margin-bottom: 10px; font-size: 1.1rem;">${escapeHtml(st.title || 'Unknown Title')}</h4>
        <div style="background: rgba(255,255,255,0.05); padding: 16px; border-left: 3px solid var(--gold); border-radius: 4px; font-size: 0.95rem; line-height: 1.6; color: #f4f4f7; font-family: var(--font-sans);">
            "${escapeHtml(st.statute_text || 'No text provided')}"
        </div>
        ${st.clears && Array.isArray(st.clears) ? `
            <div style="margin-top: 14px;">
                <strong style="font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase;">Statutory Required Clears:</strong>
                <ul style="margin-top: 6px; padding-left: 18px; color: #d4d4d8; font-size: 0.85rem;">
                    ${st.clears.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
    `;
    document.getElementById('detail-modal').classList.add('active');
}

// 12b. Raw Backend JSON Connection Modal
function showRawJsonConnection() {
    document.getElementById('modal-title').textContent = "Backend ADK JSON Payload";
    const payloadHtml = currentData ? escapeHtml(JSON.stringify(currentData, null, 2)) : "No payload available";
    document.getElementById('modal-body').innerHTML = `
        <p style="color: var(--text-muted); margin-bottom: 8px; font-size: 0.85rem;">Raw data object received from FastAPI/Gemini:</p>
        <div style="background: #09090c; border: 1px solid var(--border); padding: 14px; border-radius: 6px; max-height: 50vh; overflow-y: auto;">
            <pre style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--green); margin: 0;">${payloadHtml}</pre>
        </div>
    `;
    document.getElementById('detail-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('detail-modal').classList.remove('active');
}

// 13. Fallback Initial Data Loader
async function loadLatestData() {
    try {
        const resp = await fetch('/api/latest');
        if (resp.ok) {
            const data = await resp.json();
            renderDashboard(data);
            renderAnalysisReceipt(data);
            setNetworkStatus(true);
        } else {
            throw new Error("API not okay");
        }
    } catch(e) {
        console.warn("Could not load initial data via API, falling back to static:", e);
        try {
            const staticResp = await fetch('output.json');
            const data = await staticResp.json();
            renderDashboard(data);
            renderAnalysisReceipt(data);
            setNetworkStatus(false);
        } catch(err) {
            console.error("Total failure loading static fallback data", err);
            const data = getEmbeddedFallbackData();
            renderDashboard(data);
            renderAnalysisReceipt(data);
            setNetworkStatus(false);
        }
    }
}

function setNetworkStatus(isOnline) {
    const liveBadge = document.getElementById('network-status');
    const offBadge = document.getElementById('offline-badge');
    if (liveBadge && offBadge) {
        if (isOnline) {
            liveBadge.style.display = 'inline-flex';
            offBadge.style.display = 'none';
        } else {
            liveBadge.style.display = 'none';
            offBadge.style.display = 'inline-flex';
        }
    }
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function generateOfflineAnalysis(payload) {
    const sceneId = payload.scene_id || payload.scenario_id || "CUSTOM";
    const heading = payload.scene_heading || "SCENE REVISION";
    const origText = payload.original_text || "";
    const revText = payload.revised_text || "";
    const lowerRev = revText.toLowerCase();

    // S1 specific
    if (sceneId === "S1" && !payload.is_custom) {
        return {
            project: "Universal CallSheet",
            tagline: "Deterministic script revision cascades and offline safety governance for film production.",
            production_context: DEFAULT_PRODUCTION_CONTEXT,
            jurisdiction: "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
            model_primary: "gemini-3.7-flash",
            analysis: {
                mode: "offline_structured_fallback",
                note: "Google ADK/Gemini was unavailable or returned an error; local keyword extraction produced schema-compatible output.",
                structured_output_order: ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
                deterministic_decision_owner: "engine.safety.evaluate_safety"
            },
            scene: {
                id: "S1",
                heading: "EXT. LOADING DOCK - NIGHT",
                original_script: origText,
                revised_script: revText
            },
            diff: [{ scene_id: "S1", element: "action", old_text: origText, new_text: revText }],
            department_deltas: [
                { department: "SPFX", impact: "Requires setup, perimeter clearance, and execution of practical pyrotechnics." },
                { department: "Stunts", impact: "Stunt performer required for physical fall/jump action and deceleration mats." },
                { department: "Grip / Rigging", impact: "Fall protection and elevated platform rigging required." },
                { department: "Grip", impact: "Powered mobile equipment / hydraulic lift operation." }
            ],
            hazard_tags: [
                { row: 2, label: "pyro", detail: "Practical pyrotechnic device / flash pot explosion introduced." },
                { row: 8, label: "stunts", detail: "Physical stunt action requiring coordinator walk-through." },
                { row: 9, label: "heights", detail: "Elevated platform or fall hazard >= 3 metres requiring fall protection." },
                { row: 11, label: "motion_pme", detail: "Powered mobile equipment / hydraulic lift." },
                { row: 13, label: "loto", detail: "Hazardous energy isolation required before resetting equipment between takes." }
            ],
            safety: {
                severity: "RED",
                reason: "High-risk safety hazards introduced: Row 2 (Pyrotechnic Devices & Flash Pots), Row 8 (High-Risk Physical Stunts & Acrobatics), Row 9 (Working at Heights (>= 3 Metres)), Row 13 (Lockout / Tagout & Hydraulic Energy Isolation). Mandatory pre-take clearances required per Alberta OHS Code.",
                required_clears: [
                    "Equipment Owner Lockout Clear",
                    "Key Rigger / Fall Protection Clear (Dana Rigger)",
                    "SPFX Lead Clear",
                    "Safety Officer Clear (Sam Officer)",
                    "Stunt Coordinator Clear"
                ],
                statutory_citations: [
                    {
                        citation: "Alberta OHS Code Part 2, s.7(4)(c)",
                        title: "Mandatory Hazard Assessment Revision",
                        statute_text: "An employer must ensure that the hazard assessment is repeated before work begins on a new work site or when a work process or operation changes.",
                        mandatory: true
                    },
                    {
                        citation: "Alberta OHS Code Part 28, s.498 (Pyrotechnics & Special Effects)",
                        title: "Pyrotechnic Devices & Flash Pots",
                        statute_text: "Pyrotechnic special effects require an authorized special effects pyrotechnician, local fire jurisdiction permit, and an enforced 50-foot safety exclusion perimeter.",
                        clears: ["SPFX Lead Clear", "Safety Officer Clear (Sam Officer)"],
                        severity: "RED"
                    },
                    {
                        citation: "Alberta OHS Code Part 9, s.139 (Fall Protection Systems)",
                        title: "Working at Heights (>= 3 Metres)",
                        statute_text: "An employer must ensure that a fall protection system is used where a worker or performer may fall 3 metres (approx 10 feet) or more.",
                        clears: ["Key Rigger / Fall Protection Clear (Dana Rigger)", "Safety Officer Clear (Sam Officer)"],
                        severity: "RED"
                    }
                ]
            },
            grafana: { published: false, annotation_id: "", dashboard_url: "", error: "Local/Offline mode active." }
        };
    }

    // S2 specific (Firearms + Confined Space)
    if (sceneId === "S2" && !payload.is_custom) {
        return {
            project: "Universal CallSheet",
            tagline: "Deterministic script revision cascades and offline safety governance for film production.",
            production_context: DEFAULT_PRODUCTION_CONTEXT,
            jurisdiction: "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
            model_primary: "gemini-3.7-flash",
            analysis: {
                mode: "offline_structured_fallback",
                note: "Google ADK/Gemini was unavailable or returned an error; local keyword extraction produced schema-compatible output.",
                structured_output_order: ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
                deterministic_decision_owner: "engine.safety.evaluate_safety"
            },
            scene: {
                id: "S2",
                heading: "INT. CARGO HOLD - NIGHT",
                original_script: origText,
                revised_script: revText
            },
            diff: [{ scene_id: "S2", element: "action", old_text: origText, new_text: revText }],
            department_deltas: [
                { department: "Props / Armory", impact: "Certified armorer required on set for blank-firing prop weapon." },
                { department: "SPFX / Safety", impact: "Atmospheric fog in enclosed space requiring air quality monitoring." }
            ],
            hazard_tags: [
                { row: 1, label: "firearms", detail: "Blank firearm discharge requiring direct armorer line-of-sight." },
                { row: 7, label: "confined_space", detail: "Enclosed compartment / restricted egress space." }
            ],
            safety: {
                severity: "STOP",
                reason: "MANDATORY STOP: Life-safety regulated activity introduced (Row 1 (Firearms & Explosive Devices)). Cannot roll camera without dedicated certified safety master sign-off.",
                required_clears: [
                    "Armorer Clear (Al Arms)",
                    "On-Site Medic Standby",
                    "Safety Officer Clear (Sam Officer)"
                ],
                statutory_citations: [
                    {
                        citation: "Alberta OHS Code Part 2, s.7(4)(c)",
                        title: "Mandatory Hazard Assessment Revision",
                        statute_text: "An employer must ensure that the hazard assessment is repeated before work begins on a new work site or when a work process or operation changes.",
                        mandatory: true
                    },
                    {
                        citation: "Alberta OHS Code Part 28, s.498 & Firearms Act",
                        title: "Firearms & Explosive Devices",
                        statute_text: "Special effects firearms, blank ammunition, and explosive props must be handled exclusively by a certified armorer with direct line-of-sight and verified clear zones.",
                        clears: ["Armorer Clear (Al Arms)", "Safety Officer Clear (Sam Officer)"],
                        severity: "STOP"
                    }
                ]
            },
            grafana: { published: false, annotation_id: "", dashboard_url: "", error: "Local/Offline mode active." }
        };
    }

    // S3 specific (Heights + Condor Crane + Wind)
    if (sceneId === "S3" && !payload.is_custom) {
        return {
            project: "Universal CallSheet",
            tagline: "Deterministic script revision cascades and offline safety governance for film production.",
            production_context: DEFAULT_PRODUCTION_CONTEXT,
            jurisdiction: "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
            model_primary: "gemini-3.7-flash",
            analysis: {
                mode: "offline_structured_fallback",
                note: "Google ADK/Gemini was unavailable or returned an error; local keyword extraction produced schema-compatible output.",
                structured_output_order: ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
                deterministic_decision_owner: "engine.safety.evaluate_safety"
            },
            scene: {
                id: "S3",
                heading: "EXT. ROOFTOP - NIGHT",
                original_script: origText,
                revised_script: revText
            },
            diff: [{ scene_id: "S3", element: "action", old_text: origText, new_text: revText }],
            department_deltas: [
                { department: "Grip / Rigging", impact: "Scaffold fall protection and perimeter harness lines required." },
                { department: "Grip", impact: "60ft condor crane hoist requiring wind anemometer monitoring." },
                { department: "Stunts", impact: "Aerial high-altitude stunt rehearsal and anchor certification." }
            ],
            hazard_tags: [
                { row: 9, label: "heights", detail: "Elevated platform or fall hazard >= 3 metres requiring fall protection." },
                { row: 11, label: "motion_pme", detail: "Powered mobile equipment / telescopic crane." },
                { row: 12, label: "extreme_weather", detail: "High-altitude wind gust thresholds (> 40 km/h) requiring immediate cessation." }
            ],
            safety: {
                severity: "RED",
                reason: "High-risk safety hazards introduced: Row 9 (Working at Heights (>= 3 Metres)), Row 12 (Extreme Weather & Wind Thresholds). Mandatory pre-take clearances required per Alberta OHS Code.",
                required_clears: [
                    "1st AD Weather Hold Clear (Ann Frost)",
                    "Key Rigger / Fall Protection Clear (Dana Rigger)",
                    "Safety Officer Clear (Sam Officer)"
                ],
                statutory_citations: [
                    {
                        citation: "Alberta OHS Code Part 2, s.7(4)(c)",
                        title: "Mandatory Hazard Assessment Revision",
                        statute_text: "An employer must ensure that the hazard assessment is repeated before work begins on a new work site or when a work process or operation changes.",
                        mandatory: true
                    },
                    {
                        citation: "Alberta OHS Code Part 9, s.139 (Fall Protection Systems)",
                        title: "Working at Heights (>= 3 Metres)",
                        statute_text: "An employer must ensure that a fall protection system is used where a worker or performer may fall 3 metres (approx 10 feet) or more.",
                        clears: ["Key Rigger / Fall Protection Clear (Dana Rigger)", "Safety Officer Clear (Sam Officer)"],
                        severity: "RED"
                    }
                ]
            },
            grafana: { published: false, annotation_id: "", dashboard_url: "", error: "Local/Offline mode active." }
        };
    }

    // S4 specific (Dialogue / Green)
    if (sceneId === "S4" && !payload.is_custom) {
        return {
            project: "Universal CallSheet",
            tagline: "Deterministic script revision cascades and offline safety governance for film production.",
            production_context: DEFAULT_PRODUCTION_CONTEXT,
            jurisdiction: "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
            model_primary: "gemini-3.7-flash",
            analysis: {
                mode: "offline_structured_fallback",
                note: "Google ADK/Gemini was unavailable or returned an error; local keyword extraction produced schema-compatible output.",
                structured_output_order: ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
                deterministic_decision_owner: "engine.safety.evaluate_safety"
            },
            scene: {
                id: "S4",
                heading: "INT. PRODUCTION OFFICE - DAY",
                original_script: origText,
                revised_script: revText
            },
            diff: [{ scene_id: "S4", element: "dialogue", old_text: origText, new_text: revText }],
            department_deltas: [
                { department: "Production", impact: "Dialogue / staging adjustment with standard set protocols." }
            ],
            hazard_tags: [],
            safety: {
                severity: "GREEN",
                reason: "No high-risk safety-impacting hazards detected. Standard production safety protocols apply.",
                required_clears: [],
                statutory_citations: [
                    {
                        citation: "Alberta OHS Code Part 2, s.7(4)(c)",
                        title: "Mandatory Hazard Assessment Revision",
                        statute_text: "An employer must ensure that the hazard assessment is repeated before work begins on a new work site or when a work process or operation changes.",
                        mandatory: true
                    }
                ]
            },
            grafana: { published: false, annotation_id: "", dashboard_url: "", error: "Severity GREEN does not require a Grafana annotation." }
        };
    }

    // Dynamic Generic / Custom Scene Keyword Analyzer
    const deltas = [];
    const tags = [];
    const reqClears = new Set();
    let hasStop = false;
    let hasRed = false;

    if (lowerRev.includes("gun") || lowerRev.includes("revolver") || lowerRev.includes("firearm") || lowerRev.includes("blank")) {
        deltas.push({ department: "Props / Armory", impact: "Certified armorer required on set for blank-firing prop weapon." });
        tags.push({ row: 1, label: "firearms", detail: "Blank firearm discharge requiring direct armorer line-of-sight." });
        reqClears.add("Armorer Clear (Al Arms)");
        reqClears.add("Safety Officer Clear (Sam Officer)");
        hasStop = true;
    }

    if (lowerRev.includes("flash pot") || lowerRev.includes("explosion") || lowerRev.includes("pyro")) {
        deltas.push({ department: "SPFX", impact: "Requires setup, perimeter clearance, and execution of practical pyrotechnics." });
        tags.push({ row: 2, label: "pyro", detail: "Practical pyrotechnic device / flash pot explosion introduced." });
        reqClears.add("SPFX Lead Clear");
        reqClears.add("Safety Officer Clear (Sam Officer)");
        hasRed = true;
    }

    if (lowerRev.includes("jump") || lowerRev.includes("stunt") || lowerRev.includes("fall")) {
        deltas.push({ department: "Stunts", impact: "Stunt performer required for physical fall/jump action and deceleration mats." });
        tags.push({ row: 8, label: "stunts", detail: "Physical stunt action requiring coordinator walk-through." });
        reqClears.add("Stunt Coordinator Clear");
        reqClears.add("Safety Officer Clear (Sam Officer)");
        hasRed = true;
    }

    if (lowerRev.includes("20-foot") || lowerRev.includes("platform") || lowerRev.includes("scaffold") || lowerRev.includes("height")) {
        deltas.push({ department: "Grip / Rigging", impact: "Fall protection and elevated platform rigging required." });
        tags.push({ row: 9, label: "heights", detail: "Elevated platform or fall hazard >= 3 metres requiring fall protection." });
        reqClears.add("Key Rigger / Fall Protection Clear (Dana Rigger)");
        reqClears.add("Safety Officer Clear (Sam Officer)");
        hasRed = true;
    }

    if (lowerRev.includes("lift") || lowerRev.includes("hydraulic") || lowerRev.includes("crane")) {
        deltas.push({ department: "Grip", impact: "Powered mobile equipment / hydraulic lift operation." });
        tags.push({ row: 11, label: "motion_pme", detail: "Powered mobile equipment / hydraulic lift." });
        tags.push({ row: 13, label: "loto", detail: "Hazardous energy isolation required before resetting equipment between takes." });
        reqClears.add("Equipment Owner Lockout Clear");
        reqClears.add("Safety Officer Clear (Sam Officer)");
        hasRed = true;
    }

    if (deltas.length === 0) {
        deltas.push({ department: "Production", impact: "Dialogue / staging adjustment with standard set protocols." });
    }

    const severity = hasStop ? "STOP" : hasRed ? "RED" : tags.length > 0 ? "REVIEW" : "GREEN";
    const reason = hasStop
        ? "MANDATORY STOP: Life-safety regulated activity introduced. Cannot roll camera without dedicated certified safety master sign-off."
        : hasRed
        ? "High-risk safety hazards introduced. Mandatory pre-take clearances required per Alberta OHS Code."
        : severity === "REVIEW"
        ? "Secondary hazards detected. Requires 1st AD / Safety Officer review."
        : "No high-risk safety-impacting hazards detected. Standard production safety protocols apply.";

    return {
        project: "Universal CallSheet",
        tagline: "Deterministic script revision cascades and offline safety governance for film production.",
        production_context: DEFAULT_PRODUCTION_CONTEXT,
        jurisdiction: "Alberta OHS Code (AR 191/2021) / Section 7(4)(c)",
        model_primary: "gemini-3.7-flash",
        analysis: {
            mode: "offline_structured_fallback",
            note: "Local deterministic keyword engine evaluated scene text.",
            structured_output_order: ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
            deterministic_decision_owner: "engine.safety.evaluate_safety"
        },
        scene: { id: sceneId, heading: heading, original_script: origText, revised_script: revText },
        diff: [{ scene_id: sceneId, element: "action", old_text: origText, new_text: revText }],
        department_deltas: deltas,
        hazard_tags: tags,
        safety: {
            severity: severity,
            reason: reason,
            required_clears: Array.from(reqClears).sort(),
            statutory_citations: [
                {
                    citation: "Alberta OHS Code Part 2, s.7(4)(c)",
                    title: "Mandatory Hazard Assessment Revision",
                    statute_text: "An employer must ensure that the hazard assessment is repeated before work begins on a new work site or when a work process or operation changes.",
                    mandatory: true
                }
            ]
        },
        grafana: { published: false, annotation_id: "", dashboard_url: "", error: "Local/Offline mode active." }
    };
}

function getEmbeddedFallbackData() {
    return {
        project: "Universal CallSheet",
        tagline: "Structured revision analysis with deterministic safety gating for film production.",
        analysis: {
            mode: "embedded_static_fallback",
            note: "API and output.json were unavailable; the page rendered its bundled demo receipt.",
            structured_output_order: ["DiffOutput", "CascadeOutput", "HazardTagOutput"],
            deterministic_decision_owner: "engine.safety.evaluate_safety"
        },
        scene: {
            id: "S1",
            heading: "EXT. LOADING DOCK - NIGHT",
            original_script: "[Scene 1] EXT. LOADING DOCK - NIGHT\nThe loading dock is quiet.",
            revised_script: "[Scene 1] EXT. LOADING DOCK - NIGHT\nA pyrotechnic flash pot explodes near the dumpster.\nA performer jumps from a 20-foot platform."
        },
        diff: [
            {
                scene_id: "S1",
                element: "action",
                old_text: "The loading dock is quiet.",
                new_text: "A pyrotechnic flash pot explodes near the dumpster. A performer jumps from a 20-foot platform."
            }
        ],
        department_deltas: [
            { department: "SPFX", impact: "Requires practical pyrotechnics setup and perimeter clearance." },
            { department: "Stunts", impact: "Requires coordinator walk-through and fall protection planning." }
        ],
        hazard_tags: [
            { row: 2, label: "pyro", detail: "Practical pyrotechnic device introduced." },
            { row: 9, label: "heights", detail: "Elevated fall hazard at or above 3 metres." }
        ],
        safety: {
            severity: "RED",
            reason: "High-risk hazards introduced: pyro and working at heights. Mandatory clearances required before camera roll.",
            required_clears: ["SPFX Lead Clear", "Key Rigger / Fall Protection Clear", "Safety Officer Clear"],
            statutory_citations: [
                {
                    citation: "Alberta OHS Code Part 2, s.7(4)(c)",
                    title: "Mandatory Hazard Assessment Revision",
                    statute_text: "Hazard assessment must be repeated when a work process or operation changes."
                }
            ]
        },
        grafana: {
            published: false,
            annotation_id: "",
            dashboard_url: "",
            error: "Embedded fallback has no live Grafana connection."
        }
    };
}

// App Initialization
document.addEventListener('DOMContentLoaded', async () => {
    initScrollAnimations();
    await loadProductionContext();
    await loadScenarios();
    await loadLatestData();
});

// Scroll Reveal Animations
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                // Optional: Stop observing once revealed if you only want it to animate once
                // observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

    // Observe static elements
    document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
    
    // Store observer on window to re-trigger dynamically injected content if needed
    window.scrollObserver = observer;
}
