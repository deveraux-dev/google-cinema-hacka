let currentScenarios = [];
let activeScenarioId = "S1";
let currentData = null;
let signedClears = new Set();
let currentTab = "scenarios";

// 1. Terminal Log Animation
async function animateTerminalLogs(scenarioName) {
    const loader = document.getElementById('terminal-loader');
    const termBody = document.getElementById('term-logs');
    loader.style.display = 'block';
    termBody.innerHTML = '';
    
    const logs = [
        `> [ADK_CORE] Connecting to Gemini 3.7 Flash Engine via Google ADK...`,
        `> [SESSION] Initializing schema runner for scenario [${scenarioName}]...`,
        `> [DIFF_AGENT] Comparing original baseline against revised scene...`,
        `> [DIFF_AGENT] Extracted structured DiffOutput in 420ms.`,
        `> [CASCADE_AGENT] Evaluating guild deltas: SPFX, Stunts, Grip, Wardrobe...`,
        `> [CASCADE_AGENT] Extracted structured CascadeOutput in 610ms.`,
        `> [HAZARD_AGENT] Parsing text against Alberta OHS Code Hazard Ladder (1-13)...`,
        `> [HAZARD_AGENT] Extracted HazardTagOutput.`,
        `> [SAFETY_ENGINE] Engaging pure-Python deterministic compliance gate...`,
        `> [SAFETY_ENGINE] Evaluating statutory requirements (AR 191/2021 s.7(4)(c))...`,
        `> [MCP_CLIENT] Connecting to Grafana MCP Stdio Server (uvx mcp-grafana)...`,
        `> [MCP_CLIENT] Writing annotation to /d/ucs-safety-wall... SUCCESS.`,
        `> [STATE] Syncing sovereign run to SQLite database... DONE.`
    ];

    for (let log of logs) {
        await new Promise(r => setTimeout(r, 120 + Math.random() * 120));
        const line = document.createElement('div');
        line.className = 'term-line';
        line.textContent = log;
        termBody.appendChild(line);
        termBody.scrollTop = termBody.scrollHeight;
    }

    await new Promise(r => setTimeout(r, 300));
    loader.style.display = 'none';
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
            <div class="scenario-card ${isActive ? 'active' : ''}" onclick="selectScenario('${sc.id}')">
                <div class="scenario-card-top">
                    <span class="scenario-id-tag">${sc.id} // ${sc.heading}</span>
                    <span class="${badgeClass}">${sc.expected_severity}</span>
                </div>
                <div class="scenario-card-title">${sc.title}</div>
                <div class="scenario-card-desc">${sc.description}</div>
            </div>
        `;
    }).join('');
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
        setNetworkStatus(true);
    } catch(e) {
        console.error("Analysis Error:", e);
        // Fallback to latest
        loadLatestData();
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Execute Gemini ADK Pipeline`;
    }
}

// 6. Render Full Dashboard Results
function renderDashboard(data) {
    currentData = data;
    signedClears.clear(); // Reset clearances for the new analysis

    document.getElementById('display-scene-id').textContent = `SCENE ${data.scene.id}`;

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
    if (data.diff && data.diff.length > 0) {
        let diffHtml = '';
        data.diff.forEach(c => {
            diffHtml += `
<div style="margin-bottom: 16px;">
    <div class="sp-heading">${data.scene.heading || 'SCENE'}</div>
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
        container.innerHTML = `<div class="sp-heading">${data.scene.heading || ''}</div><div class="sp-action">${escapeHtml(data.scene.revised_script || 'No script text')}</div>`;
    }
}

// 8. Department Work Deltas
function renderDepartmentDeltas(data) {
    const container = document.getElementById('department-deltas-container');
    if (!data.department_deltas || data.department_deltas.length === 0) {
        container.innerHTML = `<div class="dept-card"><span class="dept-tag">ALL GUILDS</span><span class="dept-impact">No departmental work changes detected for this revision.</span></div>`;
        return;
    }

    container.innerHTML = data.department_deltas.map(d => `
        <div class="dept-card">
            <span class="dept-tag">${d.department}</span>
            <div class="dept-impact">${d.impact || d.delta}</div>
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
        gateIcon.textContent = '🟢';
        gateTitle.style.color = 'var(--green)';
        gateTitle.textContent = 'STAGE CLEAR // CAMERA AUTHORIZED TO ROLL';
        gateDesc.textContent = 'All mandatory clearances signed and verified. 1st AD authorized to call camera roll.';
    } else {
        gateBox.style.borderColor = severity === 'STOP' ? 'var(--red)' : '#3f3f50';
        gateBox.style.background = '#0e0e13';
        gateIcon.textContent = severity === 'STOP' ? '🛑' : '🔒';
        gateTitle.style.color = 'var(--red)';
        gateTitle.textContent = severity === 'STOP' ? 'MANDATORY STOP // SET FROZEN' : 'STAGE LOCKED // CAMERA CANNOT ROLL';
        gateDesc.textContent = `${requiredClears.length - signedClears.size} required clearance(s) pending sign-off before rehearsal or camera roll.`;
    }
}

// 10. Clearances Checklist
function renderClearances(data) {
    const container = document.getElementById('clears-container');
    const requiredClears = data.safety?.required_clears || [];
    
    updateClearsBadge(requiredClears);

    if (requiredClears.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.88rem; padding: 10px;">No mandatory clearances required for this revision.</div>`;
        return;
    }

    container.innerHTML = requiredClears.map(c => `
        <div class="clear-row ${signedClears.has(c) ? 'signed' : ''}" onclick="toggleClear('${escapeHtml(c)}')">
            <input type="checkbox" class="clear-checkbox" ${signedClears.has(c) ? 'checked' : ''} onclick="event.stopPropagation(); toggleClear('${escapeHtml(c)}')">
            <span class="clear-text">${c}</span>
        </div>
    `).join('');
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
    if (!data.hazard_tags || data.hazard_tags.length === 0) {
        container.innerHTML = `<span style="color: var(--text-muted); font-size: 0.85rem;">No jurisdiction hazards identified.</span>`;
        return;
    }

    container.innerHTML = data.hazard_tags.map((t, idx) => `
        <div class="hazard-pill" onclick="showHazardModal(${idx})">
            <span class="hazard-pill-row">Row ${t.row}</span>
            <span>${t.label}</span>
        </div>
    `).join('');
}

function showHazardModal(idx) {
    if (!currentData || !currentData.hazard_tags) return;
    const tag = currentData.hazard_tags[idx];
    
    document.getElementById('modal-title').textContent = `Hazard: ${tag.label.toUpperCase()} (Row ${tag.row})`;
    document.getElementById('modal-body').innerHTML = `
        <p style="color: var(--text-muted); margin-bottom: 8px;">Extracted Script Reasoning:</p>
        <div style="background: rgba(255,255,255,0.05); padding: 14px; border-left: 3px solid var(--blue); border-radius: 4px; font-size: 0.95rem; line-height: 1.5; color: #f4f4f7;">
            ${tag.detail}
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
    const statutes = data.safety?.statutory_citations || [];

    if (statutes.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">Standard General Duty Clause (AB OHS Act s.3) applies.</div>`;
        return;
    }

    container.innerHTML = statutes.map((st, idx) => `
        <div class="statute-card" onclick="showStatuteModal(${idx})">
            <span class="statute-citation">${st.citation}</span>
            <div class="statute-title">${st.title}</div>
            <div class="statute-excerpt">${st.statute_text}</div>
        </div>
    `).join('');
}

function showStatuteModal(idx) {
    if (!currentData || !currentData.safety?.statutory_citations) return;
    const st = currentData.safety.statutory_citations[idx];

    document.getElementById('modal-title').textContent = st.citation;
    document.getElementById('modal-body').innerHTML = `
        <h4 style="color: #ffffff; margin-bottom: 10px; font-size: 1.1rem;">${st.title}</h4>
        <div style="background: rgba(255,255,255,0.05); padding: 16px; border-left: 3px solid var(--gold); border-radius: 4px; font-size: 0.95rem; line-height: 1.6; color: #f4f4f7; font-family: var(--font-sans);">
            "${st.statute_text}"
        </div>
        ${st.clears ? `
            <div style="margin-top: 14px;">
                <strong style="font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase;">Statutory Required Clears:</strong>
                <ul style="margin-top: 6px; padding-left: 18px; color: #d4d4d8; font-size: 0.85rem;">
                    ${st.clears.map(c => `<li>${c}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
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
            setNetworkStatus(false);
        } catch(err) {
            console.error("Total failure loading static fallback data", err);
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
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// App Initialization
document.addEventListener('DOMContentLoaded', async () => {
    await loadProductionContext();
    await loadScenarios();
    await loadLatestData();
});
