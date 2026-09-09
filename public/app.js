let currentScenarios = [];
let activeScenarioId = "S1";
let currentData = null;
let signedClears = new Set();
let currentTab = "scenarios";
window.currentRequiredClears = [];

// 1. Terminal Log Animation
async function animateTerminalLogs(scenarioName) {
    const termBody = document.getElementById('term-logs');
    const statusText = document.getElementById('telemetry-status-text');
    termBody.innerHTML = '';
    if (statusText) {
        statusText.textContent = 'ANALYSIS REQUEST SENT...';
        statusText.style.color = 'var(--accent)';
    }
    
    const logs = [
        `> [REQUEST] Scenario ${scenarioName} queued for structured analysis.`,
        `> [SCHEMA] Expected order: DiffOutput -> CascadeOutput -> HazardTagOutput.`,
        `> [SAFETY_ENGINE] Python safety gate owns the final severity decision.`,
        `> [GRAFANA] Publish status will be reported from the backend response.`
    ];

    for (let log of logs) {
        await new Promise(r => setTimeout(r, 70));
        const line = document.createElement('div');
        line.className = 'term-line';
        line.textContent = log;
        termBody.appendChild(line);
        termBody.scrollTop = termBody.scrollHeight;
    }

    await new Promise(r => setTimeout(r, 300));
    if(statusText) {
        statusText.textContent = 'WAITING FOR BACKEND RECEIPT...';
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
    appendTerminalLine(`> [SAFETY_ENGINE] Severity returned by backend: ${severity}.`, severity === 'GREEN' ? 'success' : 'warning');

    if (grafana.published) {
        appendTerminalLine(`> [GRAFANA] MCP publish verified by backend. Annotation: ${grafana.annotation_id || 'created'}.`, 'success');
    } else {
        appendTerminalLine(`> [GRAFANA] Not published: ${grafana.error || 'No Grafana receipt returned.'}`, 'warning');
    }

    if (statusText) {
        statusText.textContent = mode === 'google_adk_gemini'
            ? 'LIVE ADK ANALYSIS COMPLETE'
            : 'OFFLINE STRUCTURED FALLBACK COMPLETE';
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
        mode === 'google_adk_gemini' ? 'Live Gemini' : mode.replaceAll('_', ' '),
        mode === 'google_adk_gemini' ? 'live' : 'fallback'
    );
    setChainStep(
        'chain-safety',
        severity,
        severity === 'GREEN' ? 'live' : severity === 'STOP' ? 'stop' : severity.toLowerCase()
    );
    setChainStep(
        'chain-grafana',
        grafana.published ? 'Published' : 'Skipped',
        grafana.published ? 'live' : 'skipped'
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
    try {
        const resp = await fetch('/api/context');
        if (resp.ok) {
            const ctx = await resp.json();
            document.getElementById('ctx-prod').textContent = ctx.production_name || 'Stage 4';
            document.getElementById('ctx-day').textContent = ctx.call_sheet_day || 'Day 2 (Night)';
            document.getElementById('ctx-loc').textContent = `${ctx.location.name} (${ctx.location.hospital_minutes}m to ${ctx.location.nearest_hospital})`;
            document.getElementById('ctx-leads').textContent = `1st AD: ${ctx.crew_on_duty.first_ad} | Safety: ${ctx.crew_on_duty.safety_officer}`;
            document.getElementById('ctx-juris').textContent = ctx.jurisdiction.name;
        }
    } catch(e) {
        console.warn("Could not load production context:", e);
    }
}

// 4. Load Scenarios Deck
async function loadScenarios() {
    try {
        const resp = await fetch('/api/scenarios');
        if (resp.ok) {
            currentScenarios = await resp.json();
            renderScenarioDeck(currentScenarios);
            
            // Set initial custom editor text from first scenario
            if (currentScenarios.length > 0) {
                document.getElementById('custom-orig-text').value = currentScenarios[0].original_text;
                document.getElementById('custom-rev-text').value = currentScenarios[0].revised_text;
            }
        }
    } catch(e) {
        console.warn("Could not load scenarios:", e);
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

// 5. Trigger Analysis (Live API Call)
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
            revised_text: document.getElementById('custom-rev-text').value
        };
        await animateTerminalLogs("CUSTOM SCREENPLAY");
    } else {
        const sc = currentScenarios.find(s => s.id === activeScenarioId) || { id: "S1", title: "Scene 1" };
        payload = {
            scenario_id: sc.id,
            scene_id: sc.id,
            scene_heading: sc.heading,
            original_text: sc.original_text,
            revised_text: sc.revised_text
        };
        await animateTerminalLogs(sc.title);
    }

    try {
        const resp = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error(`Analysis server returned ${resp.status}`);
        const data = await resp.json();
        renderDashboard(data);
        renderAnalysisReceipt(data);
        setNetworkStatus(true);
    } catch(e) {
        console.error("Analysis Error:", e);
        appendTerminalLine(`> [ERROR] ${e.message}. Loading latest cached JSON.`, 'warning');
        // Fallback to latest
        loadLatestData();
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Execute Gemini ADK Pipeline`;
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
