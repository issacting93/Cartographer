/**
 * DetailsPanel.tsx - BLOOM Design System
 * 
 * Right panel: Shows details of selected items and allows
 * creating new session context from selections.
 */

import { useState } from 'react';
import { useWorkspace } from './ThreePanelLayout';

export function DetailsPanel() {
    const {
        selection,
        setSelection,
        sessionContext,
        addSessionContext,
        removeSessionContext,
        attachedContext,
        detachContext,
    } = useWorkspace();

    const [newContextType, setNewContextType] = useState<'Goal' | 'Constraint' | 'Preference'>('Constraint');
    const [isCreating, setIsCreating] = useState(false);

    const handleSaveAsContext = () => {
        if (!selection) return;

        addSessionContext({
            type: newContextType,
            label: selection.content.slice(0, 100),
            icon: newContextType === 'Goal' ? 'flag' : newContextType === 'Constraint' ? 'lock' : 'favorite',
            description: selection.content,
        });

        setSelection(null);
        setIsCreating(false);
    };

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-[var(--gray)]">
                <h2 className="font-bold text-[var(--text)] flex items-center gap-2">
                    <span className="material-symbols-rounded text-[var(--yellow)]">info</span>
                    Details
                </h2>
                <p className="text-xs text-[var(--text-dim)] mt-1">
                    View selection details • Create new context
                </p>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">

                {/* Current Selection */}
                {selection ? (
                    <section>
                        <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--text-dim)] mb-3">
                            Selected
                        </h3>
                        <div className="p-4 bg-[var(--bg-subtle)] rounded-xl border border-[var(--gray)]">
                            {selection.type === 'context' && selection.item ? (
                                <div className="space-y-3">
                                    <div className="flex items-center gap-2">
                                        <span className="material-symbols-rounded text-[var(--yellow)]">
                                            {selection.item.icon}
                                        </span>
                                        <span className="text-xs font-bold uppercase text-[var(--text-dim)]">
                                            {selection.item.type}
                                        </span>
                                    </div>
                                    <div className="font-medium text-[var(--text)]">
                                        {selection.item.label}
                                    </div>
                                    {selection.item.description && (
                                        <p className="text-sm text-[var(--text-dim)]">
                                            {selection.item.description}
                                        </p>
                                    )}
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    <div className="flex items-center gap-2">
                                        <span className="material-symbols-rounded text-[var(--text-dim)]">
                                            {selection.type === 'text' ? 'text_fields' : 'chat_bubble'}
                                        </span>
                                        <span className="text-xs font-bold uppercase text-[var(--text-dim)]">
                                            {selection.type} selection
                                        </span>
                                    </div>
                                    <p className="text-sm text-[var(--text)] bg-white p-3 rounded-lg border border-[var(--gray)]">
                                        "{selection.content}"
                                    </p>

                                    {/* Save as Context */}
                                    {!isCreating ? (
                                        <button
                                            onClick={() => setIsCreating(true)}
                                            className="w-full py-2 px-4 bg-[var(--yellow)] text-[var(--black)] rounded-full font-medium text-sm flex items-center justify-center gap-2 hover:scale-[1.02] transition-all"
                                        >
                                            <span className="material-symbols-rounded text-lg">add</span>
                                            Save as Context
                                        </button>
                                    ) : (
                                        <div className="space-y-3 p-3 bg-white rounded-lg border border-[var(--gray)]">
                                            <div className="text-xs font-bold text-[var(--text-dim)]">Context Type</div>
                                            <div className="flex gap-2">
                                                {(['Goal', 'Constraint', 'Preference'] as const).map(type => (
                                                    <button
                                                        key={type}
                                                        onClick={() => setNewContextType(type)}
                                                        className={`flex-1 py-2 rounded-lg text-xs font-medium transition-all ${newContextType === type
                                                            ? type === 'Goal'
                                                                ? 'bg-[var(--green)] text-white'
                                                                : type === 'Constraint'
                                                                    ? 'bg-[var(--yellow)] text-[var(--black)]'
                                                                    : 'bg-[var(--orange)] text-white'
                                                            : 'bg-[var(--bg-subtle)] text-[var(--text-dim)]'
                                                            }`}
                                                    >
                                                        {type}
                                                    </button>
                                                ))}
                                            </div>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => setIsCreating(false)}
                                                    className="flex-1 py-2 rounded-lg text-sm text-[var(--text-dim)] hover:bg-[var(--bg-subtle)]"
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    onClick={handleSaveAsContext}
                                                    className="flex-1 py-2 bg-[var(--black)] text-white rounded-lg text-sm font-medium"
                                                >
                                                    Save
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Clear Selection */}
                        <button
                            onClick={() => setSelection(null)}
                            className="mt-3 w-full py-2 text-sm text-[var(--text-dim)] hover:text-[var(--text)] transition-colors"
                        >
                            Clear Selection
                        </button>
                    </section>
                ) : (
                    <div className="p-6 text-center text-[var(--text-dim)]">
                        <span className="material-symbols-rounded text-4xl opacity-30 block mb-3">
                            touch_app
                        </span>
                        <p className="text-sm">Select text or items to see details</p>
                    </div>
                )}

                {/* Attached Context */}
                {attachedContext.length > 0 && (
                    <section>
                        <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--yellow)] mb-3 flex items-center gap-2">
                            <span className="material-symbols-rounded text-sm">attach_file</span>
                            Attached to Next Message
                        </h3>
                        <div className="space-y-2">
                            {attachedContext.map(item => (
                                <div
                                    key={item.id}
                                    className="flex items-center justify-between p-3 bg-[var(--yellow)] bg-opacity-10 rounded-lg border border-[var(--yellow)]"
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="material-symbols-rounded text-[var(--yellow)]">
                                            {item.icon}
                                        </span>
                                        <span className="text-sm font-medium">{item.label}</span>
                                    </div>
                                    <button
                                        onClick={() => detachContext(item.id)}
                                        className="text-[var(--text-dim)] hover:text-[var(--orange)]"
                                    >
                                        <span className="material-symbols-rounded text-sm">close</span>
                                    </button>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* Session Context List */}
                {sessionContext.length > 0 && (
                    <section>
                        <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--text-dim)] mb-3 flex items-center gap-2">
                            <span className="material-symbols-rounded text-sm">bookmark</span>
                            Session Context ({sessionContext.length})
                        </h3>
                        <div className="space-y-2">
                            {sessionContext.map(item => (
                                <div
                                    key={item.id}
                                    className="flex items-center justify-between p-3 bg-white rounded-lg border border-[var(--gray)]"
                                >
                                    <div className="flex items-center gap-2 min-w-0">
                                        <span className="material-symbols-rounded text-[var(--text-dim)]">
                                            {item.icon}
                                        </span>
                                        <span className="text-sm truncate">{item.label}</span>
                                    </div>
                                    <button
                                        onClick={() => removeSessionContext(item.id)}
                                        className="text-[var(--text-dim)] hover:text-[var(--orange)] flex-shrink-0"
                                    >
                                        <span className="material-symbols-rounded text-sm">delete</span>
                                    </button>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </div>
        </div>
    );
}
