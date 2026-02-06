/**
 * ThreePanelLayout.tsx - BLOOM Design System
 * 
 * Main layout wrapper for the three-panel workspace:
 * - Left: Context Source (drag from)
 * - Center: Workspace (conversation or canvas)
 * - Right: Details + Create (select to, save new context)
 */

import { useState, createContext, useContext, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { ContextItem, Selection } from '../types/index';

// Re-export types for components that import from this file
export type { ContextItem, Selection } from '../types/index';

interface WorkspaceContextType {
    // Left Panel
    sourceContext: ContextItem[];
    sessionContext: ContextItem[];
    addSessionContext: (item: Omit<ContextItem, 'id' | 'source' | 'createdAt'>) => void;
    removeSessionContext: (id: string) => void;

    // Center Panel
    mode: 'chat' | 'canvas';
    setMode: (mode: 'chat' | 'canvas') => void;
    attachedContext: ContextItem[];
    attachContext: (item: ContextItem) => void;
    detachContext: (id: string) => void;
    clearAttached: () => void;

    // Right Panel
    selection: Selection | null;
    setSelection: (selection: Selection | null) => void;

    // Pin-to-Task: Selection → Promotion → Reification
    pinTextToContext: (text: string, type: ContextItem['type']) => void;
}

const WorkspaceContext = createContext<WorkspaceContextType | null>(null);

export function useWorkspace() {
    const context = useContext(WorkspaceContext);
    if (!context) throw new Error('useWorkspace must be used within ThreePanelLayout');
    return context;
}

// Default context items
const DEFAULT_CONTEXT: ContextItem[] = [
    { id: 'goal-1', type: 'Goal', label: 'Find senior engineering role', icon: 'flag', source: 'predefined' },
    { id: 'constraint-1', type: 'Constraint', label: 'Max 45 hrs/week, no on-call', icon: 'lock', source: 'predefined' },
    { id: 'constraint-2', type: 'Constraint', label: 'Remote-first only', icon: 'home', source: 'predefined' },
    { id: 'preference-1', type: 'Preference', label: 'Tech/AI sector', icon: 'smart_toy', source: 'predefined' },
];

interface ThreePanelLayoutProps {
    leftPanel: ReactNode;
    centerPanel: ReactNode;
    rightPanel: ReactNode;
    title?: string;
}

export function ThreePanelLayout({ leftPanel, centerPanel, rightPanel, title = "Context Workspace" }: ThreePanelLayoutProps) {
    // State
    const [sourceContext] = useState<ContextItem[]>(DEFAULT_CONTEXT);
    const [sessionContext, setSessionContext] = useState<ContextItem[]>([]);
    const [mode, setMode] = useState<'chat' | 'canvas'>('chat');
    const [attachedContext, setAttachedContext] = useState<ContextItem[]>([]);
    const [selection, setSelection] = useState<Selection | null>(null);

    // Actions
    const addSessionContext = (item: Omit<ContextItem, 'id' | 'source' | 'createdAt'>) => {
        const newItem: ContextItem = {
            ...item,
            id: `session-${Date.now()}`,
            source: 'session',
            createdAt: new Date(),
        };
        setSessionContext(prev => [...prev, newItem]);
    };

    const removeSessionContext = (id: string) => {
        setSessionContext(prev => prev.filter(item => item.id !== id));
    };

    const attachContext = (item: ContextItem) => {
        if (!attachedContext.find(c => c.id === item.id)) {
            setAttachedContext(prev => [...prev, item]);
        }
    };

    const detachContext = (id: string) => {
        setAttachedContext(prev => prev.filter(item => item.id !== id));
    };

    const clearAttached = () => {
        setAttachedContext([]);
    };

    // Pin-to-Task: Selection → Promotion → Reification
    const pinTextToContext = (text: string, type: ContextItem['type']) => {
        const iconMap: Record<ContextItem['type'], string> = {
            Goal: 'flag',
            Constraint: 'lock',
            Preference: 'favorite',
            Session: 'pin',
        };

        addSessionContext({
            type,
            label: text.length > 80 ? text.slice(0, 77) + '...' : text,
            description: text.length > 80 ? text : undefined,
            icon: iconMap[type],
        });
    };

    const contextValue: WorkspaceContextType = {
        sourceContext,
        sessionContext,
        addSessionContext,
        removeSessionContext,
        mode,
        setMode,
        attachedContext,
        attachContext,
        detachContext,
        clearAttached,
        selection,
        setSelection,
        pinTextToContext,
    };

    return (
        <WorkspaceContext.Provider value={contextValue}>
            <div className="h-screen flex flex-col bg-[var(--bg-subtle)]">
                {/* Header */}
                <header className="bg-[var(--black)] px-4 py-3 flex items-center justify-between flex-shrink-0">
                    <div className="flex items-center gap-3">
                        <Link to="/" className="text-[var(--gray-dark)] hover:text-white transition-colors">
                            <span className="material-symbols-rounded">arrow_back</span>
                        </Link>
                        <div className="flex items-center gap-2">
                            <span className="material-symbols-rounded text-[var(--yellow)]">dashboard</span>
                            <h1 className="text-white font-bold">{title}</h1>
                        </div>
                    </div>

                    {/* Mode Switcher */}
                    <div className="flex items-center gap-1 bg-white bg-opacity-10 rounded-full p-1">
                        <button
                            onClick={() => setMode('chat')}
                            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${mode === 'chat'
                                ? 'bg-[var(--yellow)] text-[var(--black)]'
                                : 'text-[var(--gray-dark)] hover:text-white'
                                }`}
                        >
                            <span className="material-symbols-rounded text-lg">chat</span>
                            Chat
                        </button>
                        <button
                            onClick={() => setMode('canvas')}
                            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${mode === 'canvas'
                                ? 'bg-[var(--yellow)] text-[var(--black)]'
                                : 'text-[var(--gray-dark)] hover:text-white'
                                }`}
                        >
                            <span className="material-symbols-rounded text-lg">hexagon</span>
                            Canvas
                        </button>
                    </div>

                    {/* Status */}
                    <div className="flex items-center gap-3 text-xs">
                        {attachedContext.length > 0 && (
                            <span className="bg-[var(--yellow)] bg-opacity-20 text-[var(--yellow)] px-3 py-1 rounded-full flex items-center gap-1">
                                <span className="material-symbols-rounded text-sm">attach_file</span>
                                {attachedContext.length} attached
                            </span>
                        )}
                        <span className="text-[var(--gray-dark)]">
                            {sessionContext.length} session items
                        </span>
                    </div>
                </header>

                {/* Three Panel Layout */}
                <main className="flex-1 flex overflow-hidden">
                    {/* Left Panel: Context Source */}
                    <div className="w-72 bg-white border-r border-[var(--gray)] flex-shrink-0 overflow-hidden flex flex-col">
                        {leftPanel}
                    </div>

                    {/* Center Panel: Workspace */}
                    <div className="flex-1 flex flex-col overflow-hidden">
                        {centerPanel}
                    </div>

                    {/* Right Panel: Details + Create */}
                    <div className="w-80 bg-white border-l border-[var(--gray)] flex-shrink-0 overflow-hidden flex flex-col">
                        {rightPanel}
                    </div>
                </main>
            </div>
        </WorkspaceContext.Provider>
    );
}
