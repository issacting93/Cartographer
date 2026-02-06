import { useState, useEffect } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend, Sankey } from 'recharts'
import { Link } from 'react-router-dom'
import clsx from 'clsx'

interface TaskEvidence {
    constraint_turns: number[]
    violation_turns: number[]
    repair_turns: number[]
}

interface TaskClassification {
    task_goal: string
    primary_constraints: string[]
    stability_class: string
    confidence: number
    violation_count: number
    user_response: string
    reasoning: string
    evidence: TaskEvidence
}

interface ClassifiedConversation {
    id: string
    source: string
    domain: string
    total_turns: number
    classification: TaskClassification
    file_path: string
}

const CLASS_COLORS: Record<string, string> = {
    "Task Maintained": "#4ade80",   // Green
    "Constraint Drift": "#facc15",  // Yellow
    "Agency Collapse": "#f87171",   // Red
    "Task Shift": "#60a5fa",        // Blue
    "No Constraints": "#94a3b8"     // Gray
}

// Sankey Data Helpers
const prepareSankeyData = (data: ClassifiedConversation[]) => {
    // Nodes: 0:Start, 1:Violated, 2:No_Violation, 3:Repaired, 4:Abandoned, 5:Maintained, 6:Drift, 7:Collapse

    // Step 1: Violation Status
    const hasViolation = data.filter(d => d.classification.violation_count > 0)
    const noViolation = data.filter(d => d.classification.violation_count === 0)

    // Step 2: User Response (Only for those with violations)
    const repaired = hasViolation.filter(d => d.classification.user_response.toLowerCase().includes('repaired'))
    const abandoned = hasViolation.filter(d => d.classification.user_response.toLowerCase().includes('abandoned'))
    // Catch-all for others (e.g. "N/A" or unrecognized)
    const noResponse = hasViolation.filter(d =>
        !d.classification.user_response.toLowerCase().includes('repaired') &&
        !d.classification.user_response.toLowerCase().includes('abandoned')
    )

    // Step 3: Outcomes mapping (Counts)
    const driftCount = data.filter(d => d.classification.stability_class === 'Constraint Drift').length
    const collapseCount = data.filter(d => d.classification.stability_class === 'Agency Collapse').length
    const maintainedCount = data.filter(d => d.classification.stability_class === 'Task Maintained').length

    const nodes = [
        { name: `Total (${data.length})` },          // 0
        { name: `Violations (${hasViolation.length})` }, // 1
        { name: `Clean (${noViolation.length})` },       // 2
        { name: `Repaired (${repaired.length})` },       // 3
        { name: `Abandoned (${abandoned.length})` },     // 4
        { name: `Unresolved (${noResponse.length})` },   // 5
        { name: `Drift (${driftCount})` },               // 6
        { name: `Collapse (${collapseCount})` },         // 7
        { name: `Maintained (${maintainedCount})` }      // 8
    ]

    const rawLinks = [
        { source: 0, target: 1, value: hasViolation.length },
        { source: 0, target: 2, value: noViolation.length },

        { source: 1, target: 3, value: repaired.length },
        { source: 1, target: 4, value: abandoned.length },
        { source: 1, target: 5, value: noResponse.length },

        // Clean -> Maintained (mostly)
        { source: 2, target: 8, value: noViolation.length },

        // Repaired -> Drift (mostly)
        { source: 3, target: 6, value: repaired.filter(d => d.classification.stability_class === 'Constraint Drift').length },
        { source: 3, target: 8, value: repaired.filter(d => d.classification.stability_class === 'Task Maintained').length },

        // Abandoned -> Collapse
        { source: 4, target: 7, value: abandoned.length },

        // Unresolved -> Drift or Shift
        { source: 5, target: 6, value: noResponse.filter(d => d.classification.stability_class === 'Constraint Drift').length },
        { source: 5, target: 8, value: noResponse.filter(d => d.classification.stability_class === 'Task Maintained').length },
    ]

    // CRITICAL: Filter out 0 value links to prevent Recharts Error
    return {
        nodes,
        links: rawLinks.filter(l => l.value > 0)
    }
}

export default function TaskAnalytics() {
    const [data, setData] = useState<ClassifiedConversation[]>([])
    const [selectedPoint, setSelectedPoint] = useState<ClassifiedConversation | null>(null)
    const [loading, setLoading] = useState(true)
    const [view, setView] = useState<'landscape' | 'flow'>('landscape')

    useEffect(() => {
        fetch('/data/task_stability.json')
            .then(res => res.json())
            .then(json => {
                setData(json)
                setLoading(false)
            })
            .catch(err => {
                console.error("Failed to load data", err)
                setLoading(false)
            })
    }, [])

    if (loading) return <div className="p-12 text-white text-center">Loading analysis data...</div>

    // Scatter Data
    const scatterData = data.map(d => ({
        ...d,
        x: d.total_turns + (Math.random() - 0.5) * 0.5,
        y: d.classification.violation_count + (Math.random() - 0.5) * 0.2,
        fill: CLASS_COLORS[d.classification.stability_class] || "#94a3b8"
    }))

    // Sankey Data
    const sankeyData = prepareSankeyData(data)

    // Timeline Helper
    const renderTimeline = (d: ClassifiedConversation) => {
        const turns = Array.from({ length: d.total_turns }, (_, i) => i)
        return (
            <div className="flex flex-col gap-1 mt-4 relative pl-4 border-l border-white border-opacity-10">
                {turns.map(t => {
                    const isV = d.classification.evidence.violation_turns.includes(t)
                    const isR = d.classification.evidence.repair_turns.includes(t)
                    const isC = d.classification.evidence.constraint_turns.includes(t)
                    if (!isV && !isR && !isC && t % 5 !== 0) return null // Skip boring turns to save space, show every 5th or active

                    let label = `Turn ${t}`
                    let color = "text-gray-600"
                    let icon = "circle"

                    if (isC) { label = "Constraint Set"; color = "text-blue-400"; icon = "lock" }
                    if (isV) { label = "Violation"; color = "text-red-400"; icon = "warning" }
                    if (isR) { label = "User Repair"; color = "text-yellow-400"; icon = "build" }

                    return (
                        <div key={t} className={`text-xs flex items-center gap-2 ${color}`}>
                            <span className="material-symbols-rounded text-[10px]">{icon}</span>
                            <span>{label}</span>
                        </div>
                    )
                })}
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-[var(--black)] text-white flex">
            {/* Main Content */}
            <div className="flex-1 p-6 flex flex-col h-screen overflow-hidden">
                <header className="mb-6 flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold flex items-center gap-2">
                            <span className="material-symbols-rounded text-[var(--yellow)]">monitoring</span>
                            Task Stability Landscape
                        </h1>
                        <p className="text-[var(--gray-dark)] text-sm">
                            N={data.length} Conversations
                        </p>
                    </div>

                    <div className="flex items-center bg-white bg-opacity-10 rounded-lg p-1 gap-1">
                        <button
                            onClick={() => setView('landscape')}
                            className={clsx("px-3 py-1.5 rounded-md text-sm transition-all", view === 'landscape' ? "bg-[var(--yellow)] text-[var(--black)] font-bold" : "text-gray-400 hover:text-white")}
                        >
                            Landscape
                        </button>
                        <button
                            onClick={() => setView('flow')}
                            className={clsx("px-3 py-1.5 rounded-md text-sm transition-all", view === 'flow' ? "bg-[var(--yellow)] text-[var(--black)] font-bold" : "text-gray-400 hover:text-white")}
                        >
                            Flow
                        </button>
                    </div>

                    <Link to="/" className="text-sm text-[var(--gray-dark)] hover:text-white">
                        Back to Home
                    </Link>
                </header>

                <div className="flex-1 bg-white bg-opacity-5 rounded-xl border border-white border-opacity-10 p-4 relative">

                    {view === 'landscape' && (
                        <ResponsiveContainer width="100%" height="100%">
                            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.1} />
                                <XAxis type="number" dataKey="x" name="Total Turns" unit=" turns" stroke="#666" label={{ value: 'Conversation Length (Turns)', position: 'insideBottom', offset: -10, fill: '#666' }} />
                                <YAxis type="number" dataKey="y" name="Violations" stroke="#666" label={{ value: 'Task Violations', angle: -90, position: 'insideLeft', fill: '#666' }} />
                                <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
                                <Legend verticalAlign="top" height={36} />
                                <Scatter name="Conversations" data={scatterData} fill="#8884d8" onClick={(node) => setSelectedPoint(node.payload)} cursor="pointer">
                                    {scatterData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.fill} />)}
                                </Scatter>
                            </ScatterChart>
                        </ResponsiveContainer>
                    )}

                    {view === 'flow' && (
                        <ResponsiveContainer width="100%" height="100%">
                            <Sankey
                                data={sankeyData}
                                node={{ fill: "#666", width: 10 }}
                                link={{ stroke: '#facc1530' }}
                                margin={{ left: 20, right: 20, top: 20, bottom: 20 }}
                            >
                                <Tooltip />
                            </Sankey>
                        </ResponsiveContainer>
                    )}

                </div>
            </div>

            {/* Side Panel */}
            <div className="w-96 border-l border-white border-opacity-10 bg-[var(--black)] p-6 overflow-y-auto">
                {selectedPoint ? (
                    <div className="space-y-6 animate-in slide-in-from-right duration-300">
                        {/* ... Existing Details ... */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs uppercase tracking-widest text-[var(--gray-dark)]">Conversation ID</span>
                                <span className="text-xs text-[var(--gray-dark)] truncate w-32">{selectedPoint.id}</span>
                            </div>
                            <div
                                className="inline-block px-3 py-1 rounded-full text-xs font-bold"
                                style={{
                                    backgroundColor: `${CLASS_COLORS[selectedPoint.classification.stability_class]}20`,
                                    color: CLASS_COLORS[selectedPoint.classification.stability_class],
                                    border: `1px solid ${CLASS_COLORS[selectedPoint.classification.stability_class]}40`
                                }}
                            >
                                {selectedPoint.classification.stability_class}
                            </div>
                        </div>

                        <div>
                            <h3 className="text-sm font-bold text-[var(--yellow)] mb-2">Task Goal</h3>
                            <p className="text-sm text-gray-300 p-3 bg-white bg-opacity-5 rounded-lg">
                                {selectedPoint.classification.task_goal}
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-3 bg-white bg-opacity-5 rounded-lg text-center">
                                <div className="text-2xl font-bold text-white">{selectedPoint.classification.violation_count}</div>
                                <div className="text-xs text-[var(--gray-dark)]">Violations</div>
                            </div>
                            <div className="p-3 bg-white bg-opacity-5 rounded-lg text-center">
                                <div className="text-2xl font-bold text-white">{selectedPoint.classification.evidence.repair_turns.length}</div>
                                <div className="text-xs text-[var(--gray-dark)]">User Repairs</div>
                            </div>
                        </div>

                        <div className="pt-4 border-t border-white border-opacity-10">
                            <h3 className="text-xs font-bold text-[var(--gray-dark)] mb-2">Conversation Timeline</h3>
                            {renderTimeline(selectedPoint)}
                        </div>

                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-[var(--gray-dark)] opacity-50">
                        <span className="material-symbols-rounded text-4xl mb-4">touch_app</span>
                        <p>Select a data point to view details</p>
                    </div>
                )}
            </div>
        </div>
    )
}

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const d = payload[0].payload as ClassifiedConversation
        return (
            <div className="bg-[var(--black)] border border-white border-opacity-20 p-3 rounded shadow-xl text-xs z-50">
                <p className="font-bold text-[var(--yellow)]">{d.classification.stability_class}</p>
                <p>ID: {d.id}</p>
                <p>Turns: {d.total_turns}</p>
                <p>Violations: {d.classification.violation_count}</p>
            </div>
        )
    }
    return null
}
