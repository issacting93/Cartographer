/**
 * TaskWizardPanel.tsx
 * 
 * A Task-First Interaction interface for the CUI 2026 paper:
 * "Tasks, Not Turns: Reframing Conversational Interfaces Around Persistent Task Objects"
 * 
 * Implements the three interaction patterns:
 * 1. Pin to Task - Convert text/concepts to Constraint Nodes
 * 2. Task Shelf - Visual list of persistent tasks
 * 3. Context Lens - Explicit scope selection for queries
 */

import React, { useState, useEffect } from 'react';
import clsx from 'clsx';
import {
    Pin,
    FolderOpen,
    Eye,
    Sparkles,
    Plus,
    Check,
    Pause,
    Archive,
    ChevronRight,
    ListTodo,
    Tag,
    Target,
    Heart,
    FileText
} from 'lucide-react';

// Types matching backend models
interface ConstraintNode {
    id: string;
    type: 'Goal' | 'Constraint' | 'Preference' | 'Artifact' | 'Context';
    label: string;
    description?: string;
    active: boolean;
    pinned: boolean;
    created_at: string;
}

interface TaskObject {
    id: string;
    user_id: string;
    name: string;
    description?: string;
    status: 'active' | 'suspended' | 'completed' | 'archived';
    nodes: ConstraintNode[];
    created_at: string;
    updated_at: string;
    metrics: {
        conversation_turns: number;
        restatement_count: number;
        constraint_violations: number;
        interruption_count: number;
    };
}

interface TaskWizardPanelProps {
    userId?: string;
    onQuerySubmit?: (prompt: string, activeNodes: ConstraintNode[]) => void;
    className?: string;
}

// Node type icons - with fallback
const getNodeIcon = (type: string): React.ElementType => {
    const icons: Record<string, React.ElementType> = {
        Goal: Target,
        Constraint: Tag,
        Preference: Heart,
        Artifact: FileText,
        Context: Eye,
    };
    return icons[type] || Tag;
};

// Node type colors
const NODE_COLORS: Record<string, string> = {
    Goal: 'bg-emerald-100 text-emerald-700 border-emerald-200',
    Constraint: 'bg-amber-100 text-amber-700 border-amber-200',
    Preference: 'bg-pink-100 text-pink-700 border-pink-200',
    Artifact: 'bg-blue-100 text-blue-700 border-blue-200',
    Context: 'bg-purple-100 text-purple-700 border-purple-200',
};

export function TaskWizardPanel({ userId = 'demo', onQuerySubmit, className }: TaskWizardPanelProps) {
    // --- State ---
    const [tasks, setTasks] = useState<TaskObject[]>([]);
    const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
    const [activeTask, setActiveTask] = useState<TaskObject | null>(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState<'shelf' | 'pin' | 'lens'>('shelf');

    // Pin to Task state
    const [pinText, setPinText] = useState('');
    const [pinType, setPinType] = useState<ConstraintNode['type']>('Constraint');

    // Context Lens state
    const [selectedNodeIds, setSelectedNodeIds] = useState<Set<string>>(new Set());
    const [queryPrompt, setQueryPrompt] = useState('');

    // New Task state
    const [showNewTask, setShowNewTask] = useState(false);
    const [newTaskName, setNewTaskName] = useState('');

    // --- API Calls ---
    const API_BASE = 'http://localhost:8000/api/context';

    const fetchTasks = async () => {
        try {
            const res = await fetch(`${API_BASE}/task/list?user_id=${userId}`);
            const data = await res.json();
            setTasks(data.tasks || []);
            setActiveTaskId(data.active_task_id);
        } catch (e) {
            console.error('Failed to fetch tasks:', e);
        }
    };

    const fetchActiveTask = async () => {
        if (!activeTaskId) return;
        try {
            const res = await fetch(`${API_BASE}/task/${activeTaskId}?user_id=${userId}`);
            const data = await res.json();
            setActiveTask(data);
        } catch (e) {
            console.error('Failed to fetch active task:', e);
        }
    };

    const createTask = async () => {
        if (!newTaskName.trim()) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/task/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    name: newTaskName,
                }),
            });
            const data = await res.json();
            if (data.ok) {
                await fetchTasks();
                setActiveTaskId(data.task_id);
                setNewTaskName('');
                setShowNewTask(false);
            }
        } catch (e) {
            console.error('Failed to create task:', e);
        } finally {
            setLoading(false);
        }
    };

    const switchTask = async (taskId: string) => {
        try {
            await fetch(`${API_BASE}/task/switch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, task_id: taskId }),
            });
            setActiveTaskId(taskId);
        } catch (e) {
            console.error('Failed to switch task:', e);
        }
    };

    const pinToTask = async () => {
        if (!pinText.trim() || !activeTaskId) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/event/pin`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    task_id: activeTaskId,
                    text: pinText,
                    type: pinType,
                }),
            });
            const data = await res.json();
            if (data.ok) {
                await fetchActiveTask();
                setPinText('');
            }
        } catch (e) {
            console.error('Failed to pin:', e);
        } finally {
            setLoading(false);
        }
    };

    const toggleNodeScope = (nodeId: string) => {
        const newSet = new Set(selectedNodeIds);
        if (newSet.has(nodeId)) {
            newSet.delete(nodeId);
        } else {
            newSet.add(nodeId);
        }
        setSelectedNodeIds(newSet);
    };

    const submitQuery = async () => {
        if (!queryPrompt.trim() || !activeTaskId) return;
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/query/context`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    task_id: activeTaskId,
                    scope: Array.from(selectedNodeIds),
                    prompt: queryPrompt,
                }),
            });
            const data = await res.json();
            if (onQuerySubmit) {
                onQuerySubmit(data.augmented_prompt, data.active_nodes);
            }
            setQueryPrompt('');
        } catch (e) {
            console.error('Failed to submit query:', e);
        } finally {
            setLoading(false);
        }
    };

    // --- Effects ---
    useEffect(() => {
        fetchTasks();
    }, [userId]);

    useEffect(() => {
        if (activeTaskId) {
            fetchActiveTask();
        }
    }, [activeTaskId]);

    // --- Render ---
    return (
        <div className={clsx(
            "flex flex-col bg-white border border-gray-200 rounded-xl overflow-hidden shadow-lg",
            className
        )}>
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3">
                <div className="flex items-center gap-2">
                    <ListTodo className="w-5 h-5 text-white" />
                    <h2 className="text-white font-bold">Task-First Context</h2>
                </div>
                <p className="text-indigo-100 text-xs mt-1">
                    Tasks, Not Turns — CUI 2026
                </p>
            </div>

            {/* Pattern Tabs */}
            <div className="flex border-b border-gray-200 bg-gray-50">
                <button
                    onClick={() => setActiveTab('shelf')}
                    className={clsx(
                        "flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 transition-all",
                        activeTab === 'shelf'
                            ? "bg-white text-indigo-600 border-b-2 border-indigo-600"
                            : "text-gray-500 hover:text-gray-700"
                    )}
                >
                    <FolderOpen className="w-4 h-4" />
                    Task Shelf
                </button>
                <button
                    onClick={() => setActiveTab('pin')}
                    className={clsx(
                        "flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 transition-all",
                        activeTab === 'pin'
                            ? "bg-white text-indigo-600 border-b-2 border-indigo-600"
                            : "text-gray-500 hover:text-gray-700"
                    )}
                >
                    <Pin className="w-4 h-4" />
                    Pin to Task
                </button>
                <button
                    onClick={() => setActiveTab('lens')}
                    className={clsx(
                        "flex-1 py-3 px-4 text-sm font-medium flex items-center justify-center gap-2 transition-all",
                        activeTab === 'lens'
                            ? "bg-white text-indigo-600 border-b-2 border-indigo-600"
                            : "text-gray-500 hover:text-gray-700"
                    )}
                >
                    <Eye className="w-4 h-4" />
                    Context Lens
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 min-h-[400px]">

                {/* Pattern 2: Task Shelf */}
                {activeTab === 'shelf' && (
                    <div className="space-y-4">
                        {/* New Task Button */}
                        {!showNewTask ? (
                            <button
                                onClick={() => setShowNewTask(true)}
                                className="w-full py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-indigo-400 hover:text-indigo-600 transition-all flex items-center justify-center gap-2"
                            >
                                <Plus className="w-4 h-4" />
                                Create New Task
                            </button>
                        ) : (
                            <div className="p-4 bg-indigo-50 rounded-lg space-y-3">
                                <input
                                    type="text"
                                    placeholder="Task name (e.g., Berlin Business Trip)"
                                    value={newTaskName}
                                    onChange={(e) => setNewTaskName(e.target.value)}
                                    className="w-full px-3 py-2 border border-indigo-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    onKeyDown={(e) => e.key === 'Enter' && createTask()}
                                />
                                <div className="flex gap-2">
                                    <button
                                        onClick={createTask}
                                        disabled={loading || !newTaskName.trim()}
                                        className="flex-1 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
                                    >
                                        Create Task
                                    </button>
                                    <button
                                        onClick={() => { setShowNewTask(false); setNewTaskName(''); }}
                                        className="px-4 py-2 text-gray-500 hover:text-gray-700"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Task List */}
                        <div className="space-y-2">
                            {tasks.map((task) => (
                                <button
                                    key={task.id}
                                    onClick={() => switchTask(task.id)}
                                    className={clsx(
                                        "w-full p-4 rounded-lg border transition-all text-left",
                                        task.id === activeTaskId
                                            ? "bg-indigo-50 border-indigo-300 ring-2 ring-indigo-200"
                                            : "bg-white border-gray-200 hover:border-indigo-300"
                                    )}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            {task.status === 'active' && <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />}
                                            {task.status === 'suspended' && <Pause className="w-4 h-4 text-amber-500" />}
                                            {task.status === 'completed' && <Check className="w-4 h-4 text-green-500" />}
                                            {task.status === 'archived' && <Archive className="w-4 h-4 text-gray-400" />}
                                            <span className="font-medium text-gray-800">{task.name}</span>
                                        </div>
                                        <ChevronRight className="w-4 h-4 text-gray-400" />
                                    </div>
                                    <div className="mt-2 flex gap-4 text-xs text-gray-500">
                                        <span>{task.nodes.length} constraints</span>
                                        <span>•</span>
                                        <span>{task.metrics.restatement_count} restatements</span>
                                    </div>
                                </button>
                            ))}

                            {tasks.length === 0 && (
                                <div className="text-center py-8 text-gray-400">
                                    <ListTodo className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                    <p>No tasks yet. Create your first task above.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Pattern 1: Pin to Task */}
                {activeTab === 'pin' && (
                    <div className="space-y-4">
                        {!activeTask ? (
                            <div className="text-center py-8 text-gray-400">
                                <Pin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>Select a task first to pin constraints.</p>
                            </div>
                        ) : (
                            <>
                                {/* Current Task Info */}
                                <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                                    <div className="text-xs text-indigo-600 font-medium uppercase tracking-wide">Pinning to</div>
                                    <div className="font-bold text-indigo-800">{activeTask.name}</div>
                                </div>

                                {/* Pin Input */}
                                <div className="space-y-3">
                                    <div>
                                        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Constraint Type</label>
                                        <div className="grid grid-cols-5 gap-2 mt-2">
                                            {(['Goal', 'Constraint', 'Preference', 'Artifact', 'Context'] as const).map((type) => {
                                                const Icon = getNodeIcon(type);
                                                return (
                                                    <button
                                                        key={type}
                                                        onClick={() => setPinType(type)}
                                                        className={clsx(
                                                            "p-2 rounded-lg border text-xs font-medium flex flex-col items-center gap-1 transition-all",
                                                            pinType === type
                                                                ? NODE_COLORS[type]
                                                                : "bg-white border-gray-200 text-gray-500 hover:border-gray-300"
                                                        )}
                                                    >
                                                        <Icon className="w-4 h-4" />
                                                        {type}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Constraint Text</label>
                                        <textarea
                                            value={pinText}
                                            onChange={(e) => setPinText(e.target.value)}
                                            placeholder="e.g., Budget must be under €150/night"
                                            className="w-full mt-2 p-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                                            rows={3}
                                        />
                                    </div>

                                    <button
                                        onClick={pinToTask}
                                        disabled={loading || !pinText.trim()}
                                        className="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium flex items-center justify-center gap-2 hover:bg-indigo-700 disabled:opacity-50"
                                    >
                                        <Pin className="w-4 h-4" />
                                        Pin to Task
                                    </button>
                                </div>

                                {/* Existing Nodes */}
                                {activeTask.nodes.length > 0 && (
                                    <div className="mt-6">
                                        <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                                            Current Constraints ({activeTask.nodes.length})
                                        </div>
                                        <div className="space-y-2">
                                            {activeTask.nodes.map((node) => {
                                                const Icon = getNodeIcon(node.type);
                                                return (
                                                    <div
                                                        key={node.id}
                                                        className={clsx(
                                                            "p-3 rounded-lg border flex items-start gap-3",
                                                            NODE_COLORS[node.type]
                                                        )}
                                                    >
                                                        <Icon className="w-4 h-4 mt-0.5" />
                                                        <div className="flex-1">
                                                            <div className="text-sm font-medium">{node.label}</div>
                                                            <div className="text-xs opacity-75 mt-1">{node.type}</div>
                                                        </div>
                                                        {node.pinned && (
                                                            <Pin className="w-3 h-3 opacity-50" />
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                )}

                {/* Pattern 3: Context Lens */}
                {activeTab === 'lens' && (
                    <div className="space-y-4">
                        {!activeTask ? (
                            <div className="text-center py-8 text-gray-400">
                                <Eye className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>Select a task first to use Context Lens.</p>
                            </div>
                        ) : (
                            <>
                                {/* Scope Selection */}
                                <div>
                                    <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                                        Select Context Scope
                                        <span className="text-indigo-600 ml-2">
                                            ({selectedNodeIds.size} selected)
                                        </span>
                                    </div>

                                    {activeTask.nodes.length === 0 ? (
                                        <div className="text-center py-6 text-gray-400 text-sm">
                                            No constraints in this task yet. Pin some first!
                                        </div>
                                    ) : (
                                        <div className="grid grid-cols-2 gap-2">
                                            {activeTask.nodes.map((node) => {
                                                const Icon = getNodeIcon(node.type);
                                                const isSelected = selectedNodeIds.has(node.id);
                                                return (
                                                    <button
                                                        key={node.id}
                                                        onClick={() => toggleNodeScope(node.id)}
                                                        className={clsx(
                                                            "p-3 rounded-lg border text-left transition-all",
                                                            isSelected
                                                                ? "bg-indigo-100 border-indigo-300 ring-2 ring-indigo-200"
                                                                : "bg-white border-gray-200 hover:border-indigo-300"
                                                        )}
                                                    >
                                                        <div className="flex items-center gap-2">
                                                            <div className={clsx(
                                                                "w-5 h-5 rounded flex items-center justify-center",
                                                                isSelected ? "bg-indigo-600 text-white" : "bg-gray-100"
                                                            )}>
                                                                {isSelected ? <Check className="w-3 h-3" /> : <Icon className="w-3 h-3 text-gray-400" />}
                                                            </div>
                                                            <span className="text-xs font-medium text-gray-600 truncate">{node.label}</span>
                                                        </div>
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    )}
                                </div>

                                {/* Query Input */}
                                <div className="mt-4">
                                    <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Your Query</label>
                                    <textarea
                                        value={queryPrompt}
                                        onChange={(e) => setQueryPrompt(e.target.value)}
                                        placeholder="What do you want to do? The selected context will be included automatically."
                                        className="w-full mt-2 p-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                                        rows={3}
                                    />
                                </div>

                                <button
                                    onClick={submitQuery}
                                    disabled={loading || !queryPrompt.trim()}
                                    className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-medium flex items-center justify-center gap-2 hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50"
                                >
                                    <Sparkles className="w-4 h-4" />
                                    Submit with Context
                                </button>

                                {/* Preview */}
                                {selectedNodeIds.size > 0 && (
                                    <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs">
                                        <div className="font-medium text-gray-500 uppercase tracking-wide mb-2">Context Preview</div>
                                        {activeTask.nodes
                                            .filter((n) => selectedNodeIds.has(n.id))
                                            .map((n) => (
                                                <div key={n.id} className="text-gray-600">
                                                    [{n.type}] {n.label}
                                                </div>
                                            ))}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Footer - Metrics */}
            {activeTask && (
                <div className="border-t border-gray-200 px-4 py-3 bg-gray-50">
                    <div className="flex justify-between text-xs text-gray-500">
                        <span>Restatements: <strong>{activeTask.metrics.restatement_count}</strong></span>
                        <span>Violations: <strong>{activeTask.metrics.constraint_violations}</strong></span>
                        <span>Interruptions: <strong>{activeTask.metrics.interruption_count}</strong></span>
                    </div>
                </div>
            )}
        </div>
    );
}
