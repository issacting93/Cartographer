/**
 * ContextSourcePanel.tsx - BLOOM Design System
 * 
 * Left panel: Draggable context items organized by type.
 * Includes pre-defined context AND session-created context.
 */

import { useWorkspace, ContextItem } from './ThreePanelLayout';

const TYPE_CONFIG: Record<string, { icon: string; color: string; bgColor: string }> = {
    Goal: { icon: 'flag', color: 'text-[var(--green)]', bgColor: 'bg-[var(--green)]' },
    Constraint: { icon: 'lock', color: 'text-[var(--yellow)]', bgColor: 'bg-[var(--yellow)]' },
    Preference: { icon: 'favorite', color: 'text-[var(--orange)]', bgColor: 'bg-[var(--orange)]' },
    Session: { icon: 'bookmark', color: 'text-[var(--text)]', bgColor: 'bg-[var(--black)]' },
};

export function ContextSourcePanel() {
    const { sourceContext, sessionContext, attachContext, setSelection, attachedContext } = useWorkspace();

    const handleDragStart = (e: React.DragEvent, item: ContextItem) => {
        e.dataTransfer.setData('application/json', JSON.stringify(item));
        e.dataTransfer.effectAllowed = 'copy';
    };

    const handleClick = (item: ContextItem) => {
        setSelection({ type: 'context', content: item.label, item });
    };

    const handleDoubleClick = (item: ContextItem) => {
        attachContext(item);
    };

    const isAttached = (id: string) => attachedContext.some(c => c.id === id);

    const renderItem = (item: ContextItem) => {
        const config = TYPE_CONFIG[item.type] || TYPE_CONFIG.Session;
        const attached = isAttached(item.id);

        return (
            <div
                key={item.id}
                draggable
                onDragStart={(e) => handleDragStart(e, item)}
                onClick={() => handleClick(item)}
                onDoubleClick={() => handleDoubleClick(item)}
                className={`
          group p-3 rounded-xl border-2 cursor-grab active:cursor-grabbing
          transition-all hover:scale-[1.02] hover:shadow-md
          ${attached
                        ? 'border-[var(--yellow)] bg-[var(--yellow)] bg-opacity-10'
                        : 'border-[var(--gray)] bg-white hover:border-[var(--gray-dark)]'
                    }
        `}
            >
                <div className="flex items-start gap-2">
                    <span className={`material-symbols-rounded ${config.color}`}>
                        {item.icon || config.icon}
                    </span>
                    <div className="flex-1 min-w-0">
                        <div className="text-[10px] font-bold uppercase tracking-wide text-[var(--text-dim)]">
                            {item.type}
                        </div>
                        <div className="text-sm font-medium text-[var(--text)] truncate">
                            {item.label}
                        </div>
                    </div>
                    {attached && (
                        <span className="material-symbols-rounded text-[var(--yellow)] text-sm">
                            check_circle
                        </span>
                    )}
                </div>
            </div>
        );
    };

    // Group source context by type
    const goals = sourceContext.filter(c => c.type === 'Goal');
    const constraints = sourceContext.filter(c => c.type === 'Constraint');
    const preferences = sourceContext.filter(c => c.type === 'Preference');

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-[var(--gray)]">
                <h2 className="font-bold text-[var(--text)] flex items-center gap-2">
                    <span className="material-symbols-rounded text-[var(--yellow)]">widgets</span>
                    Context Source
                </h2>
                <p className="text-xs text-[var(--text-dim)] mt-1">
                    Drag items to attach • Double-click to quick-attach
                </p>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {/* Goals */}
                {goals.length > 0 && (
                    <section>
                        <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--green)] mb-3 flex items-center gap-2">
                            <span className="material-symbols-rounded text-sm">flag</span>
                            Goals
                        </h3>
                        <div className="space-y-2">
                            {goals.map(renderItem)}
                        </div>
                    </section>
                )}

                {/* Constraints */}
                {constraints.length > 0 && (
                    <section>
                        <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--yellow)] mb-3 flex items-center gap-2">
                            <span className="material-symbols-rounded text-sm">lock</span>
                            Constraints
                        </h3>
                        <div className="space-y-2">
                            {constraints.map(renderItem)}
                        </div>
                    </section>
                )}

                {/* Preferences */}
                {preferences.length > 0 && (
                    <section>
                        <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--orange)] mb-3 flex items-center gap-2">
                            <span className="material-symbols-rounded text-sm">favorite</span>
                            Preferences
                        </h3>
                        <div className="space-y-2">
                            {preferences.map(renderItem)}
                        </div>
                    </section>
                )}

                {/* Session Context */}
                <section>
                    <h3 className="text-[11px] font-bold uppercase tracking-widest text-[var(--text-dim)] mb-3 flex items-center gap-2">
                        <span className="material-symbols-rounded text-sm">bookmark</span>
                        Session Context
                    </h3>
                    {sessionContext.length > 0 ? (
                        <div className="space-y-2">
                            {sessionContext.map(renderItem)}
                        </div>
                    ) : (
                        <div className="p-4 border-2 border-dashed border-[var(--gray)] rounded-xl text-center">
                            <span className="material-symbols-rounded text-2xl text-[var(--gray-dark)] opacity-50">
                                add_circle
                            </span>
                            <p className="text-xs text-[var(--text-dim)] mt-2">
                                Select text in the conversation and save it here
                            </p>
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}
