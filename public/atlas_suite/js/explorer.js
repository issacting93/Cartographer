
// --- 4. INIT ---
function init() {
    // Layout Selector
    DOM.layoutSelect.on("change", function () {
        STATE.mode = this.value;
        if (STATE.data) updateLayout();
    });

    // Filtering
    d3.selectAll(".filter-cb").on("change", function () {
        const type = d3.select(this).attr("data-type");
        const pill = this.closest('.pill');
        if (this.checked) {
            STATE.activeTypes.add(type);
            pill.classList.add('active');
        } else {
            STATE.activeTypes.delete(type);
            pill.classList.remove('active');
        }
        if (STATE.data) renderGraph(STATE.data);
    });

    // Drag & Drop
    const handleFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                processData(data);
            } catch (err) {
                console.error(err);
                alert("Error parsing JSON: " + err.message);
            }
        };
        reader.readAsText(file);
    };

    DOM.dropZone.on("click", () => DOM.fileInput.node().click());
    DOM.fileInput.on("change", (e) => e.target.files[0] && handleFile(e.target.files[0]));

    document.addEventListener("dragover", e => e.preventDefault());
    document.addEventListener("drop", e => {
        e.preventDefault();
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });

    // URL Params
    const urlParams = new URLSearchParams(window.location.search);
    const autoLoadFile = urlParams.get('file');
    if (autoLoadFile) {
        setTimeout(() => {
            DOM.fileSearch.value = autoLoadFile;
            DOM.loadBtn.click();
        }, 500);
    }

    // Populate File List
    if (typeof files !== 'undefined') {
        files.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f;
            DOM.fileList.appendChild(opt);
        });
    }

    DOM.loadBtn.addEventListener('click', async () => {
        const filename = DOM.fileSearch.value;
        if (!filename) return;
        const basePath = window.GRAPH_BASE_PATH || 'data/graphs/';
        try {
            const res = await fetch(`${basePath}${filename}`);
            if (!res.ok) throw new Error("File not found");
            const data = await res.json();
            processData(data);
        } catch (err) {
            alert(`Load error: ${err.message}`);
        }
    });

    // Scrubber controls
    initScrubber();

    // Resize listener
    window.addEventListener('resize', () => {
        if (STATE.data) updateLayout();
    });
}

// --- 5. DATA PROCESSING ---
function processData(data) {
    STATE.data = data;
    // Pre-calculate degrees/meta
    const nodeMap = new Map(data.nodes.map(n => [n.id, n]));
    data.links.forEach(l => {
        l.source = typeof l.source === 'object' ? l.source : nodeMap.get(l.source);
        l.target = typeof l.target === 'object' ? l.target : nodeMap.get(l.target);
    });

    // Identify start/end turns & Mode Turns
    const turns = data.nodes.filter(n => n.node_type === 'Turn');
    if (turns.length > 0) {
        turns.sort((a, b) => (a.turn_index || 0) - (b.turn_index || 0));
        STATE.turnBoundaries = {
            start: turns[0].id,
            end: turns[turns.length - 1].id
        };
        STATE.maxTurn = turns[turns.length - 1].turn_index || 0;

        // Detect Mode Turns (change in OPERATES_IN)
        const turnModeMap = new Map();
        data.links.forEach(l => {
            if (l.edge_type === 'OPERATES_IN' && l.source.node_type === 'Turn') {
                turnModeMap.set(l.source.id, l.target.id);
            }
        });

        let currentModeId = null;
        turns.forEach(t => {
            const modeId = turnModeMap.get(t.id);
            if (modeId && modeId !== currentModeId) {
                t.is_mode_turn = true;
                currentModeId = modeId;
            } else {
                t.is_mode_turn = false;
            }
        });

    } else {
        STATE.turnBoundaries = null;
        STATE.maxTurn = 0;
    }

    // Extract PAD data for sparklines
    STATE.padData = turns
        .sort((a, b) => (a.turn_index || 0) - (b.turn_index || 0))
        .map(t => ({
            turn: t.turn_index || 0,
            role: t.role || 'user',
            pleasure: t.pad_pleasure,
            arousal: t.pad_arousal,
            dominance: t.pad_dominance,
            intensity: t.pad_intensity,
        }))
        .filter(d => d.pleasure != null);

    // Extract SRT data
    const convNode = data.nodes.find(n => n.node_type === 'Conversation');
    STATE.srtData = convNode ? {
        humanRoleDist: convNode.human_role_dist || null,
        aiRoleDist: convNode.ai_role_dist || null,
        interactionPattern: convNode.srt_interactionPattern,
        powerDynamics: convNode.srt_powerDynamics,
        emotionalTone: convNode.srt_emotionalTone,
        stability: convNode.stability_class,
    } : null;

    // Extract constraint data for state tracking
    STATE.constraints = data.nodes.filter(n => n.node_type === 'Constraint');

    // Set scrubber to show all turns initially
    STATE.scrubTurn = STATE.maxTurn;

    const stats = computeSummary(data);
    renderSummary(stats);
    renderConstraintTimeline(stats);
    renderGraph(data);

    // Show new panels
    setupScrubber();
    renderRolePanel();
    renderISPPanel();
    renderPADSparkline();
    updateScrubView(STATE.maxTurn);
}

// --- 6. RENDERING ---
function renderGraph(data) {
    // Clear
    DOM.svg.selectAll("*").remove();

    STATE.width = DOM.centerPanel.clientWidth;
    STATE.height = DOM.centerPanel.clientHeight - 56; // Account for scrubber

    const filteredNodes = data.nodes.filter(n => STATE.activeTypes.has(n.node_type));
    const filteredIds = new Set(filteredNodes.map(n => n.id));
    const filteredLinks = data.links.filter(l =>
        filteredIds.has(l.source.id) && filteredIds.has(l.target.id)
    );

    // Container for zoom
    const container = DOM.svg.append("g");
    const zoom = d3.zoom()
        .scaleExtent([0.1, 8])
        .on("zoom", (e) => container.attr("transform", e.transform));
    DOM.svg.call(zoom);

    // Markers
    const defs = DOM.svg.append("defs");
    const edges = [...new Set(filteredLinks.map(l => l.edge_type))];
    edges.forEach(et => {
        defs.append("marker")
            .attr("id", `arrow-${et}`)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 22)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", CONFIG.edgeColors[et] || '#999');
    });

    // Initial Simulation
    STATE.simulation = d3.forceSimulation(filteredNodes)
        .force("link", d3.forceLink(filteredLinks).id(d => d.id))
        .force("charge", d3.forceManyBody())
        .force("center", d3.forceCenter(STATE.width / 2, STATE.height / 2))
        .force("collide", d3.forceCollide());

    // Render Links
    const link = container.append("g")
        .selectAll("line")
        .data(filteredLinks)
        .enter().append("line")
        .attr("stroke", d => CONFIG.edgeColors[d.edge_type])
        .attr("stroke-width", d => ["VIOLATES", "REPAIR_INITIATE"].includes(d.edge_type) ? 2.5 : 1.5)
        .attr("stroke-opacity", d => ["VIOLATES", "REPAIR_INITIATE"].includes(d.edge_type) ? 0.7 : 0.2)
        .attr("marker-end", d => `url(#arrow-${d.edge_type})`);

    // Render Nodes
    const node = container.append("g")
        .selectAll("g")
        .data(filteredNodes)
        .enter().append("g")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    // Circle
    node.append("circle")
        .attr("r", d => CONFIG.radii[d.node_type] || 10)
        .attr("fill", d => {
            if (d.node_type === 'Turn' && STATE.turnBoundaries) {
                if (d.id === STATE.turnBoundaries.start) return CONFIG.colors.TurnStart;
                if (d.id === STATE.turnBoundaries.end) return CONFIG.colors.TurnEnd;
            }
            if (d.node_type === 'Move') {
                if (d.move_type && d.move_type.toLowerCase().includes('repair')) {
                    return CONFIG.colors.MoveRepair;
                }
            }
            return CONFIG.colors[d.node_type];
        })
        .attr("stroke", d => {
            if (d.node_type === 'Turn' && STATE.turnBoundaries && d.id === STATE.turnBoundaries.end) {
                return "#000000";
            }
            return "#fff";
        })
        .attr("stroke-width", 1.5);

    // Icon
    node.append("text")
        .attr("class", "material-symbols-rounded")
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "central")
        .attr("fill", d => {
            if (d.node_type === 'Turn' && STATE.turnBoundaries && d.id === STATE.turnBoundaries.end) {
                return "#000000";
            }
            return (d.node_type === "Conversation" || d.node_type === "Turn" || d.node_type === "Move" || d.node_type === "Constraint" || d.node_type === "ViolationEvent") ? "#fff" : "#1a1a1a";
        })
        .attr("font-size", d => (CONFIG.radii[d.node_type] || 10) * 1.2)
        .style("font-weight", "bold")
        .style("pointer-events", "none")
        .text(d => {
            const icon = CONFIG.icons[d.node_type];
            if (typeof icon === 'object') return icon[d.role] || icon['assistant'] || "circle";
            return icon || "circle";
        });

    // Interaction
    node.on("mouseover", (e, d) => {
        DOM.tooltip.style("opacity", 1)
            .html(`<strong>${d.node_type}</strong><br>${d.id}`)
            .style("left", (e.pageX + 10) + "px")
            .style("top", (e.pageY - 10) + "px");
    }).on("mouseout", () => DOM.tooltip.style("opacity", 0));

    node.on("click", (e, d) => {
        e.stopPropagation();
        showMetadata(d);
        highlightNeighbors(d);
    });
    DOM.svg.on("click", () => {
        document.getElementById('metadata-panel').style.display = 'none';
        document.getElementById('empty-details').style.display = 'block';
        resetHighlight();
    });

    STATE.elements = { link, node };
    updateLayout();
    // Apply scrub visibility after render
    applyScrubVisibility(STATE.scrubTurn);
}

function highlightNeighbors(d) {
    const connectedLinks = STATE.elements.link.filter(l => l.source.id === d.id || l.target.id === d.id);
    const neighborIds = new Set();
    neighborIds.add(d.id);
    connectedLinks.each(l => {
        neighborIds.add(l.source.id);
        neighborIds.add(l.target.id);
    });

    STATE.elements.node.style("opacity", 0.1);
    STATE.elements.link.style("opacity", 0.05);

    STATE.elements.node.filter(n => neighborIds.has(n.id))
        .style("opacity", 1);

    connectedLinks
        .style("opacity", 1)
        .attr("stroke-opacity", 1);
}

function resetHighlight() {
    if (!STATE.elements) return;
    // Re-apply scrub visibility instead of showing everything
    applyScrubVisibility(STATE.scrubTurn);
}

// --- 7. LAYOUTS ---
function updateLayout() {
    const { simulation, width, height, elements } = STATE;
    const nodes = simulation.nodes();

    simulation.force("x", null).force("y", null).force("radial", null);
    nodes.forEach(n => {
        if (!n.dragged) {
            n.fx = null;
            n.fy = null;
        }
    });

    simulation.force("collide", d3.forceCollide().radius(d => (CONFIG.radii[d.node_type] || 10) + 5));

    if (STATE.mode === 'force') {
        simulation.force("charge", d3.forceManyBody().strength(-300));
        simulation.force("center", d3.forceCenter(width / 2, height / 2));
        simulation.force("link").strength(0.5).distance(80);
    }
    else if (STATE.mode === 'radial') {
        const center = { x: width / 2, y: height / 2 };
        const turns = nodes.filter(n => n.node_type === "Turn")
            .sort((a, b) => (a.turn_index || 0) - (b.turn_index || 0));
        const nTurns = turns.length;
        const TAU = Math.PI * 2;
        const baseR = 140;
        const ringStep = 70;
        let ring = 0;

        turns.forEach((d, i) => {
            const angle = (-Math.PI / 2) + (i / nTurns) * TAU;
            if (i > 0 && d.is_mode_turn) ring += 1;
            const r = baseR + (ring * ringStep);
            d.fx = center.x + Math.cos(angle) * r;
            d.fy = center.y + Math.sin(angle) * r;
        });

        simulation.force("link").strength(0.8).distance(30);
        simulation.force("charge", d3.forceManyBody().strength(-50));
        simulation.force("center", d3.forceCenter(center.x, center.y).strength(0.05));
    }
    else if (STATE.mode === 'timeline') {
        simulation.force("charge", d3.forceManyBody().strength(-50));
        simulation.force("link").strength(0.1);

        simulation.force("x", d3.forceX(d => {
            if (d.node_type === "Turn") return width / 2;
            if (d.node_type === "Move") return width / 2 - 200;
            if (d.node_type === "Constraint") return width / 2 + 200;
            return width / 2 + 100;
        }).strength(1));

        simulation.force("y", d3.forceY(d => {
            const idx = d.turn_index || 0;
            return 100 + idx * 100;
        }).strength(0.5));
    }
    else if (STATE.mode === 'hierarchical') {
        simulation.force("charge", d3.forceManyBody().strength(-200));
        simulation.force("link").strength(0.5);

        simulation.force("y", d3.forceY(d => {
            if (d.node_type === "Conversation") return 100;
            if (d.node_type === "Turn") return 300;
            return 500;
        }).strength(1));

        simulation.force("x", d3.forceX(width / 2).strength(0.05));
    }

    simulation.alpha(1).restart();
    simulation.on("tick", () => {
        elements.link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
        elements.node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    });
}

// --- 8. HELPERS ---
function dragstarted(event, d) {
    if (!event.active) STATE.simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) STATE.simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function showMetadata(d) {
    document.getElementById('empty-details').style.display = 'none';
    const panel = document.getElementById('metadata-panel');
    panel.style.display = 'block';

    const clean = { ...d };
    delete clean.index; delete clean.x; delete clean.y;
    delete clean.vx; delete clean.vy; delete clean.fx; delete clean.fy;
    // Don't show full content in inspector (it's in transcript)
    if (clean.content && clean.content.length > 200) {
        clean.content = clean.content.substring(0, 200) + '...';
    }

    document.getElementById('metadata-content').textContent = JSON.stringify(clean, null, 2);
}

function computeSummary(data) {
    const nodes = data.nodes || [];
    const constraints = nodes.filter(n => n.node_type === 'Constraint');
    const violations = nodes.filter(n => n.node_type === 'ViolationEvent');
    const turns = nodes.filter(n => n.node_type === 'Turn');

    return {
        convId: (nodes.find(n => n.node_type === 'Conversation') || {}).id || 'Unknown',
        turns: turns.length,
        constraints: constraints.length,
        constraintViols: violations.length,
        repairs: nodes.filter(n => n.node_type === 'Move' && n.move_type && n.move_type.startsWith('REPAIR')).length,
        driftVelocity: turns.length ? violations.length / turns.length : 0,
        survived: constraints.filter(c => c.current_state === 'SURVIVED' || c.current_state === 'ACTIVE').length,
        constraintNodes: constraints,
        totalTurns: turns.length,
        stability: (nodes.find(n => n.node_type === 'Conversation') || {}).stability_class || '—'
    };
}

function renderSummary(stats) {
    document.getElementById('summary-stats').style.display = 'block';
    document.getElementById('stat-conv-id').textContent = stats.convId.substring(0, 16) + '...';
    document.getElementById('stat-turns').textContent = stats.turns;
    document.getElementById('stat-constraints').textContent = stats.constraints;
    document.getElementById('stat-violations').textContent = stats.constraintViols;
    document.getElementById('stat-repairs').textContent = stats.repairs;
    document.getElementById('stat-drift').textContent = stats.driftVelocity.toFixed(2);
    document.getElementById('stat-stability').textContent = stats.stability;
}

function renderConstraintTimeline(stats) {
    // Existing constraint timeline logic (simplified)
    const container = document.getElementById('timeline-content');
    container.innerHTML = '';

    if (!stats.constraintNodes || stats.constraintNodes.length === 0) {
        container.innerHTML = '<div style="font-size: 12px; color: var(--text-dim);">No constraints found</div>';
        return;
    }

    stats.constraintNodes.forEach(c => {
        const row = document.createElement('div');
        row.style.cssText = 'margin-bottom: 8px;';

        const label = document.createElement('div');
        label.style.cssText = 'font-size: 11px; color: var(--text-dim); margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;';
        label.textContent = (c.text || c.constraint_id || '').substring(0, 40);
        label.title = c.text || '';
        row.appendChild(label);

        const bar = document.createElement('div');
        bar.className = 'timeline-bar';
        bar.style.cssText = 'height: 8px; display: flex; border-radius: 4px; overflow: hidden;';

        const history = c.state_history || [];
        const totalTurns = stats.totalTurns || 1;

        if (history.length > 0) {
            for (let i = 0; i < history.length; i++) {
                const [startTurn, state] = history[i];
                const endTurn = (i + 1 < history.length) ? history[i + 1][0] : totalTurns;
                const width = ((endTurn - startTurn) / totalTurns) * 100;

                const seg = document.createElement('div');
                seg.className = `timeline-seg seg-${state === 'VIOLATED' ? 'violated' : state === 'ACTIVE' || state === 'STATED' ? 'active' : 'survived'}`;
                seg.style.width = `${Math.max(width, 2)}%`;
                bar.appendChild(seg);
            }
        }

        row.appendChild(bar);
        container.appendChild(row);
    });
}


// ============= PHASE 2: TIMELINE SCRUBBER =============

function initScrubber() {
    const slider = document.getElementById('scrub-slider');
    const playBtn = document.getElementById('scrub-play');
    const resetBtn = document.getElementById('scrub-reset');
    const endBtn = document.getElementById('scrub-end');

    slider.addEventListener('input', function () {
        const turn = parseInt(this.value);
        STATE.scrubTurn = turn;
        updateScrubView(turn);
    });

    playBtn.addEventListener('click', () => {
        if (STATE.playing) {
            stopPlayback();
        } else {
            startPlayback();
        }
    });

    resetBtn.addEventListener('click', () => {
        stopPlayback();
        STATE.scrubTurn = 0;
        document.getElementById('scrub-slider').value = 0;
        updateScrubView(0);
    });

    endBtn.addEventListener('click', () => {
        stopPlayback();
        STATE.scrubTurn = STATE.maxTurn;
        document.getElementById('scrub-slider').value = STATE.maxTurn;
        updateScrubView(STATE.maxTurn);
    });
}

function setupScrubber() {
    const scrubber = document.getElementById('timeline-scrubber');
    const slider = document.getElementById('scrub-slider');
    scrubber.style.display = 'block';
    slider.max = STATE.maxTurn;
    slider.value = STATE.maxTurn;
    document.getElementById('empty-details').style.display = 'none';
}

function startPlayback() {
    STATE.playing = true;
    document.querySelector('#scrub-play .material-symbols-rounded').textContent = 'pause';

    if (STATE.scrubTurn >= STATE.maxTurn) {
        STATE.scrubTurn = 0;
    }

    STATE.playInterval = setInterval(() => {
        STATE.scrubTurn++;
        if (STATE.scrubTurn > STATE.maxTurn) {
            stopPlayback();
            return;
        }
        document.getElementById('scrub-slider').value = STATE.scrubTurn;
        updateScrubView(STATE.scrubTurn);
    }, 1200);
}

function stopPlayback() {
    STATE.playing = false;
    document.querySelector('#scrub-play .material-symbols-rounded').textContent = 'play_arrow';
    if (STATE.playInterval) {
        clearInterval(STATE.playInterval);
        STATE.playInterval = null;
    }
}

function updateScrubView(turn) {
    // Update label
    document.getElementById('scrub-label').textContent = `Turn ${turn} / ${STATE.maxTurn}`;

    // Update graph visibility
    applyScrubVisibility(turn);

    // Update PAD sparkline marker
    updatePADMarker(turn);

    // Update transcript
    updateTranscript(turn);

    // Update constraint states
    updateConstraintStates(turn);

    // Update dominance
    updateDominanceBar(turn);
}

function applyScrubVisibility(maxVisibleTurn) {
    if (!STATE.elements) return;

    // Determine which node IDs should be visible based on turn_index
    const visibleNodeIds = new Set();
    STATE.data.nodes.forEach(n => {
        if (n.node_type === 'Conversation') {
            visibleNodeIds.add(n.id);
            return;
        }
        if (n.node_type === 'Turn') {
            if ((n.turn_index || 0) <= maxVisibleTurn) visibleNodeIds.add(n.id);
            return;
        }
        // For moves, constraints, violations, modes — check if connected to a visible turn
        // We use a simpler heuristic: check the turn_index or introduced_at field
        if (n.node_type === 'Constraint') {
            if ((n.introduced_at || 0) <= maxVisibleTurn) visibleNodeIds.add(n.id);
            return;
        }
        if (n.node_type === 'ViolationEvent') {
            if ((n.turn_index || 0) <= maxVisibleTurn) visibleNodeIds.add(n.id);
            return;
        }
        if (n.node_type === 'InteractionMode') {
            if ((n.turn_index || 0) <= maxVisibleTurn) visibleNodeIds.add(n.id);
            return;
        }
        // Moves: extract turn_index from ID (m_convid_turnidx_seq)
        if (n.node_type === 'Move') {
            const parts = n.id.split('_');
            const turnIdx = parseInt(parts[parts.length - 2]);
            if (!isNaN(turnIdx) && turnIdx <= maxVisibleTurn) visibleNodeIds.add(n.id);
            return;
        }
        // Default: show
        visibleNodeIds.add(n.id);
    });

    // Apply visibility to nodes
    STATE.elements.node
        .style("opacity", d => visibleNodeIds.has(d.id) ? 1 : 0.05)
        .style("pointer-events", d => visibleNodeIds.has(d.id) ? 'all' : 'none');

    // Apply visibility to links
    STATE.elements.link
        .style("opacity", d => {
            const srcVisible = visibleNodeIds.has(d.source.id);
            const tgtVisible = visibleNodeIds.has(d.target.id);
            if (!srcVisible || !tgtVisible) return 0.02;
            return ["VIOLATES", "REPAIR_INITIATE"].includes(d.edge_type) ? 0.7 : 0.2;
        });
}


// ============= PHASE 3: PAD SPARKLINE =============

function renderPADSparkline() {
    const svg = d3.select('#pad-sparkline');
    svg.selectAll('*').remove();

    if (!STATE.padData || STATE.padData.length === 0) {
        document.getElementById('pad-sparkline-container').style.display = 'none';
        return;
    }
    document.getElementById('pad-sparkline-container').style.display = 'block';

    const container = document.getElementById('pad-sparkline-container');
    const w = container.clientWidth - 24;
    const h = 100;
    const margin = { top: 5, right: 5, bottom: 20, left: 25 };
    const iw = w - margin.left - margin.right;
    const ih = h - margin.top - margin.bottom;

    svg.attr('width', w).attr('height', h);

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain([0, STATE.maxTurn]).range([0, iw]);
    const y = d3.scaleLinear().domain([0, 1]).range([ih, 0]);

    // Axes
    g.append('g').attr('transform', `translate(0,${ih})`)
        .call(d3.axisBottom(x).ticks(Math.min(STATE.maxTurn, 8)).tickFormat(d => `${d}`))
        .selectAll('text').style('font-size', '9px');

    g.append('g')
        .call(d3.axisLeft(y).ticks(3).tickFormat(d3.format('.1f')))
        .selectAll('text').style('font-size', '9px');

    // Lines
    const colors = { pleasure: '#22c55e', arousal: '#e85a3c', dominance: '#60a5fa' };

    ['pleasure', 'arousal', 'dominance'].forEach(dim => {
        const line = d3.line()
            .x(d => x(d.turn))
            .y(d => y(d[dim] || 0.5))
            .curve(d3.curveMonotoneX);

        g.append('path')
            .datum(STATE.padData)
            .attr('fill', 'none')
            .attr('stroke', colors[dim])
            .attr('stroke-width', 2)
            .attr('stroke-opacity', 0.8)
            .attr('d', line);

        // Dots
        g.selectAll(`.dot-${dim}`)
            .data(STATE.padData)
            .enter().append('circle')
            .attr('cx', d => x(d.turn))
            .attr('cy', d => y(d[dim] || 0.5))
            .attr('r', 2.5)
            .attr('fill', colors[dim])
            .attr('opacity', 0.6);
    });

    // Scrub marker line (will be updated)
    g.append('line')
        .attr('class', 'pad-scrub-line')
        .attr('id', 'pad-marker')
        .attr('x1', x(STATE.maxTurn))
        .attr('x2', x(STATE.maxTurn))
        .attr('y1', 0)
        .attr('y2', ih);

    STATE.padScaleX = x;
    STATE.padHeight = ih;
}

function updatePADMarker(turn) {
    if (!STATE.padScaleX) return;
    const marker = d3.select('#pad-marker');
    if (!marker.empty()) {
        marker.attr('x1', STATE.padScaleX(turn))
            .attr('x2', STATE.padScaleX(turn));
    }
}


// ============= PHASE 3: CONSTRAINT STATE TRACKING =============

function updateConstraintStates(turn) {
    const container = document.getElementById('constraint-states');
    container.innerHTML = '';

    if (!STATE.constraints || STATE.constraints.length === 0) {
        container.innerHTML = '<div style="font-size: 11px; color: var(--text-dim);">No constraints</div>';
        return;
    }

    STATE.constraints.forEach(c => {
        const state = getConstraintStateAtTurn(c, turn);

        const item = document.createElement('div');
        item.className = 'constraint-state-item';

        const dot = document.createElement('div');
        dot.className = `constraint-state-dot ${state}`;

        const text = document.createElement('div');
        text.className = 'constraint-state-text';
        text.textContent = (c.text || c.constraint_id || '').substring(0, 35);
        text.title = c.text || '';

        const label = document.createElement('span');
        label.className = 'constraint-state-label';
        label.style.color = state === 'violated' ? 'var(--red)' :
            state === 'active' ? 'var(--green)' :
                state === 'abandoned' ? 'var(--gray-dark)' : 'var(--text-dim)';
        label.textContent = state;

        item.appendChild(dot);
        item.appendChild(text);
        item.appendChild(label);
        container.appendChild(item);
    });
}

function getConstraintStateAtTurn(constraint, turn) {
    // Not yet introduced
    if ((constraint.introduced_at || 0) > turn) return 'pending';

    const history = constraint.state_history || [];
    let currentState = 'active';

    for (const entry of history) {
        if (!entry || entry.length < 2) continue;
        const [t, s] = entry;
        if (t > turn) break;
        currentState = s;
    }

    // Map to CSS classes
    const stateMap = {
        'STATED': 'active',
        'ACTIVE': 'active',
        'VIOLATED': 'violated',
        'REPAIRED': 'active',
        'ABANDONED': 'abandoned',
        'SURVIVED': 'active',
    };
    return stateMap[currentState] || 'active';
}


// ============= PHASE 4: TRANSCRIPT & ISP OVERLAY =============

function renderISPPanel() {
    const panel = document.getElementById('isp-panel');
    panel.style.display = 'block';

    // Build transcript
    const transcriptEl = document.getElementById('transcript-view');
    transcriptEl.innerHTML = '';

    const turns = (STATE.data.nodes || [])
        .filter(n => n.node_type === 'Turn' && n.content)
        .sort((a, b) => (a.turn_index || 0) - (b.turn_index || 0));

    turns.forEach(t => {
        const msg = document.createElement('div');
        msg.className = `transcript-msg ${t.role || 'user'}`;
        msg.setAttribute('data-turn', t.turn_index);

        const roleLabel = document.createElement('div');
        roleLabel.className = 'transcript-role';
        roleLabel.textContent = (t.role || 'user').toUpperCase();

        const content = document.createElement('div');
        // Truncate long messages
        const text = t.content || '';
        content.textContent = text.length > 150 ? text.substring(0, 150) + '...' : text;

        msg.appendChild(roleLabel);
        msg.appendChild(content);
        transcriptEl.appendChild(msg);
    });

    // Dominance bar
    renderDominanceBar();
}

function renderRolePanel() {
    if (!STATE.srtData || (!STATE.srtData.humanRoleDist && !STATE.srtData.aiRoleDist)) {
        document.getElementById('role-panel').style.display = 'none';
        return;
    }
    document.getElementById('role-panel').style.display = 'block';

    // Human roles
    if (STATE.srtData.humanRoleDist) {
        renderRoleBars('human-role-bars', STATE.srtData.humanRoleDist, 'human');
    }
    // AI roles
    if (STATE.srtData.aiRoleDist) {
        renderRoleBars('ai-role-bars', STATE.srtData.aiRoleDist, 'ai');
    }
}

function renderRoleBars(containerId, dist, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    // Sort by value descending
    const sorted = Object.entries(dist).sort((a, b) => b[1] - a[1]);

    sorted.forEach(([role, value]) => {
        if (value < 0.01) return; // Skip negligible

        const row = document.createElement('div');
        row.className = 'role-bar-row';

        const label = document.createElement('div');
        label.className = 'role-bar-label';
        label.textContent = role;

        const track = document.createElement('div');
        track.className = 'role-bar-track';

        const fill = document.createElement('div');
        fill.className = `role-bar-fill ${type}`;
        fill.style.width = `${value * 100}%`;

        const val = document.createElement('div');
        val.className = 'role-bar-value';
        val.textContent = `${Math.round(value * 100)}%`;

        track.appendChild(fill);
        row.appendChild(label);
        row.appendChild(track);
        row.appendChild(val);
        container.appendChild(row);
    });
}

function updateTranscript(turn) {
    const msgs = document.querySelectorAll('.transcript-msg');
    let lastVisible = null;
    msgs.forEach(msg => {
        const msgTurn = parseInt(msg.getAttribute('data-turn'));
        msg.classList.remove('current', 'future');
        if (msgTurn > turn) {
            msg.classList.add('future');
        } else if (msgTurn === turn) {
            msg.classList.add('current');
            lastVisible = msg;
        }
    });

    // Scroll to current message
    if (lastVisible) {
        lastVisible.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function renderDominanceBar() {
    const container = document.getElementById('dominance-bar-container');
    container.innerHTML = `
        <div class="dominance-row">
            <div class="dominance-label">Human</div>
            <div class="dominance-track"><div class="dominance-fill human" id="dom-human" style="width:50%"></div></div>
        </div>
        <div class="dominance-row">
            <div class="dominance-label">AI</div>
            <div class="dominance-track"><div class="dominance-fill ai" id="dom-ai" style="width:50%"></div></div>
        </div>
    `;
}

function updateDominanceBar(turn) {
    if (!STATE.padData || STATE.padData.length === 0) return;

    // Get the most recent human and AI dominance values at or before this turn
    let humanDom = 0.5;
    let aiDom = 0.5;

    for (const d of STATE.padData) {
        if (d.turn > turn) break;
        if (d.role === 'user') humanDom = d.dominance || 0.5;
        else aiDom = d.dominance || 0.5;
    }

    const humanEl = document.getElementById('dom-human');
    const aiEl = document.getElementById('dom-ai');
    if (humanEl) humanEl.style.width = `${humanDom * 100}%`;
    if (aiEl) aiEl.style.width = `${aiDom * 100}%`;
}


// Start
init();
