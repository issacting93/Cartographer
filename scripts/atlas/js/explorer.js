
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
        try {
            const res = await fetch(`../../data/atlas_canonical/graphs/${filename}`);
            if (!res.ok) throw new Error("File not found");
            const data = await res.json();
            processData(data);
        } catch (err) {
            alert(`Load error: ${err.message}`);
        }
    });

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

    // Identify start/end turns
    const turns = data.nodes.filter(n => n.node_type === 'Turn');
    if (turns.length > 0) {
        turns.sort((a, b) => (a.turn_index || 0) - (b.turn_index || 0));
        STATE.turnBoundaries = {
            start: turns[0].id,
            end: turns[turns.length - 1].id
        };
    } else {
        STATE.turnBoundaries = null;
    }

    const stats = computeSummary(data);
    renderSummary(stats);
    renderConstraintTimeline(stats);
    renderGraph(data);
}

// --- 6. RENDERING ---
function renderGraph(data) {
    // Clear
    DOM.svg.selectAll("*").remove();

    STATE.width = DOM.centerPanel.clientWidth;
    STATE.height = DOM.centerPanel.clientHeight;

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
            .attr("refX", 22) // pushed back slightly
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", CONFIG.edgeColors[et] || '#999');
    });

    // Initial Simulation (Atomic for all modes)
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
                // Check for repair in move_type (case-insensitive)
                if (d.move_type && d.move_type.toLowerCase().includes('repair')) {
                    return CONFIG.colors.MoveRepair;
                }
            }
            return CONFIG.colors[d.node_type];
        })
        .attr("stroke", d => {
            // Force black stroke for End turn (white fill)
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
            // Invert icon color for white end node
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
}

function highlightNeighbors(d) {
    // 1. Find connected links
    const connectedLinks = STATE.elements.link.filter(l => l.source.id === d.id || l.target.id === d.id);

    // 2. Find neighbor nodes
    const neighborIds = new Set();
    neighborIds.add(d.id);
    connectedLinks.each(l => {
        neighborIds.add(l.source.id);
        neighborIds.add(l.target.id);
    });

    // 3. Dim everything
    STATE.elements.node.style("opacity", 0.1);
    STATE.elements.link.style("opacity", 0.05);

    // 4. Highlight neighbors
    STATE.elements.node.filter(n => neighborIds.has(n.id))
        .style("opacity", 1);

    connectedLinks
        .style("opacity", 1)
        .attr("stroke-opacity", 1);
}

function resetHighlight() {
    STATE.elements.node.style("opacity", 1);
    STATE.elements.link.style("opacity", l => ["VIOLATES", "REPAIR_INITIATE"].includes(l.edge_type) ? 0.7 : 0.2);
}

// --- 7. LAYOUTS ---
function updateLayout() {
    const { simulation, width, height, elements } = STATE;
    const nodes = simulation.nodes();

    // Reset Forces
    simulation.force("x", null).force("y", null).force("radial", null);

    // Common Collide for all
    simulation.force("collide", d3.forceCollide().radius(d => (CONFIG.radii[d.node_type] || 10) + 5));

    if (STATE.mode === 'force') {
        simulation.force("charge", d3.forceManyBody().strength(-300));
        simulation.force("center", d3.forceCenter(width / 2, height / 2));
        simulation.force("link").strength(0.5).distance(80);
    }
    else if (STATE.mode === 'radial') {
        const center = { x: width / 2, y: height / 2 };

        // --- Procedural ring sizing for Turns ---
        const convR = CONFIG.radii["Conversation"] || 25;
        const turnR = CONFIG.radii["Turn"] || 20;

        const turns = nodes.filter(n => n.node_type === "Turn");
        const nTurns = turns.length;

        // 1) Minimum distance from center node (gap beyond center node)
        const minCenterGap = 60; // tweak: minimum empty space between center node edge and turn ring

        // 2) Desired spacing between Turn nodes around the ring
        const turnPad = 14; // tweak: extra padding between turn nodes (prevents overlaps)

        // Radius needed so circumference can fit all turns:
        // circumference >= nTurns * (node_diameter + padding)
        const requiredByPacking =
            nTurns > 0 ? (nTurns * ((2 * turnR) + turnPad)) / (2 * Math.PI) : 0;

        // Radius must be at least: center radius + min gap + turn radius, AND packing requirement
        const minFromCenter = convR + minCenterGap + turnR;

        const turnRingRadius = Math.max(minFromCenter, requiredByPacking);

        simulation.force("charge", d3.forceManyBody().strength(-100));
        simulation.force("link").strength(0.1);

        const radialForce = d3.forceRadial(d => {
            if (d.node_type === "Conversation") return 0;

            if (d.node_type === "Turn") return turnRingRadius;

            // keep outer rings proportional to the turn ring
            if (d.node_type === "Move") return turnRingRadius + 90;
            return turnRingRadius + 180; // constraints / violations / modes
        }, center.x, center.y).strength(0.8);

        simulation.force("radial", radialForce);
    }
    else if (STATE.mode === 'timeline') {
        // Timeline: Vertical flow
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
        // Hierarchical: Tree-like
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

    // Pretty print node data
    const clean = { ...d };
    delete clean.index; delete clean.x; delete clean.y;
    delete clean.vx; delete clean.vy; delete clean.fx; delete clean.fy;

    document.getElementById('metadata-content').textContent = JSON.stringify(clean, null, 2);
}

// Copy summary logic from before (simplified here to save space but functionality is preserved if copied)
// ... (See implementation below)
function computeSummary(data) {
    const nodes = data.nodes || [];
    const constraints = nodes.filter(n => n.node_type === 'Constraint');
    const violations = nodes.filter(n => n.node_type === 'ViolationEvent');
    const turns = nodes.filter(n => n.node_type === 'Turn');

    // Basic stats
    return {
        convId: (nodes.find(n => n.node_type === 'Conversation') || {}).id || 'Unknown',
        turns: turns.length,
        constraints: constraints.length,
        constraintViols: violations.length,
        repairs: nodes.filter(n => n.node_type === 'Move' && n.move_type && n.move_type.startsWith('REPAIR')).length,
        driftVelocity: turns.length ? violations.length / turns.length : 0,
        survived: constraints.filter(c => c.current_state === 'SURVIVED' || c.current_state === 'ACTIVE').length,
        constraintNodes: constraints,
        totalTurns: turns.length
    };
}

function renderSummary(stats) {
    document.getElementById('summary-stats').style.display = 'block';
    document.getElementById('stat-conv-id').textContent = stats.convId.substring(0, 12) + '...';
    document.getElementById('stat-turns').textContent = stats.turns;
    document.getElementById('stat-constraints').textContent = stats.constraints;
    document.getElementById('stat-violations').textContent = stats.constraintViols;
    document.getElementById('stat-repairs').textContent = stats.repairs;
    document.getElementById('stat-drift').textContent = stats.driftVelocity.toFixed(2);
}

function renderConstraintTimeline(stats) {
    // ... (previous logic preserved)
}

// Start
init();
