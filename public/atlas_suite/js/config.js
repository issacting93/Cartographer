// --- 1. CONFIG ---
const CONFIG = {
    colors: {
        "Conversation": "#1a1a1a",
        "Turn": "#f5c542",
        "TurnStart": "#000000", // Black
        "TurnEnd": "#ffffff",   // White
        "Move": "#60a5fa",      // Default Blue
        "MoveRepair": "#22c55e", // Repair Green
        "Constraint": "#e85a3c", // Orange
        "ViolationEvent": "#ef4444", // Red
        "InteractionMode": "#94a3b8"
    },
    edgeColors: {
        'NEXT': '#64748b',
        'CONTAINS': '#60a5fa',
        'VIOLATES': '#f87171',
        'REPAIR_INITIATE': '#4ade80',
        'REPAIR_EXECUTE': '#4ade80',
        'RATIFIES': '#c084fc',
        'TRIGGERS': '#fbbf24',
        'OPERATES_IN': '#2dd4bf',
        'HAS_MOVE': '#94a3b8',
    },
    radii: {
        "Conversation": 25,
        "Turn": 20,
        "Move": 12,
        "Constraint": 12,
        "ViolationEvent": 12,
        "InteractionMode": 14
    },
    icons: {
        "Conversation": "hub",
        "Turn": { "user": "person", "model": "smart_toy", "assistant": "smart_toy" },
        "Move": "arrow_outward",
        "Constraint": "lock",
        "ViolationEvent": "error",
        "InteractionMode": "balance"
    }
};

// --- 2. STATE ---
const STATE = {
    mode: 'radial', // radial, timeline, hierarchical, force
    data: null,
    activeTypes: new Set(["Conversation", "Turn", "Move", "Constraint", "ViolationEvent", "InteractionMode"]),
    simulation: null,
    width: 0,
    height: 0,
    turnBoundaries: null
};

// --- 3. DOM ---
const DOM = {
    svg: d3.select("#viz"),
    tooltip: d3.select("#tooltip"),
    dropZone: d3.select("#drop-zone"),
    fileInput: d3.select("#file-input"),
    layoutSelect: d3.select("#layout-select"),
    centerPanel: document.getElementById('center-panel'),
    fileSearch: document.getElementById('file-search'),
    fileList: document.getElementById('file-list'),
    loadBtn: document.getElementById('load-btn')
};
