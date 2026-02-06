/**
 * ContextPalette.tsx - BLOOM Design System
 * 
 * Draggable context pills organized by category.
 * Implements the "Context Zone" from BLOOM style guide.
 */

import clsx from 'clsx';

export interface ContextItem {
    id: string;
    label: string;
    icon: string;
    type: 'Goal' | 'Constraint' | 'Preference' | 'Need' | 'Feeling' | 'Action' | 'Context';
}

interface ContextPaletteProps {
    items: ContextItem[];
    onItemSelect?: (item: ContextItem) => void;
    className?: string;
}

// BLOOM pill variants
const PILL_STYLES: Record<ContextItem['type'], string> = {
    Goal: 'bg-[var(--green)] text-white',
    Constraint: 'bg-[var(--yellow)] text-[var(--black)]',
    Preference: 'bg-[var(--orange)] text-white',
    Need: 'bg-[var(--orange)] text-white',
    Feeling: 'bg-[var(--yellow)] text-[var(--black)]',
    Action: 'bg-white text-[var(--black)] border border-[var(--gray)]',
    Context: 'bg-[var(--black)] text-white',
};

export function ContextPalette({ items, onItemSelect, className }: ContextPaletteProps) {
    const handleDragStart = (e: React.DragEvent, item: ContextItem) => {
        e.dataTransfer.setData('application/json', JSON.stringify({
            id: item.id,
            label: item.label,
            icon: item.icon,
            type: item.type
        }));
        e.dataTransfer.effectAllowed = 'copy';
    };

    // Group items by type
    const groupedItems = items.reduce((acc, item) => {
        const type = item.type;
        if (!acc[type]) acc[type] = [];
        acc[type].push(item);
        return acc;
    }, {} as Record<string, ContextItem[]>);

    const typeOrder: ContextItem['type'][] = ['Goal', 'Constraint', 'Preference', 'Need', 'Feeling', 'Action', 'Context'];
    const sortedTypes = typeOrder.filter(t => groupedItems[t]?.length > 0);

    return (
        <div className={clsx("p-6 overflow-y-auto", className)}>
            <h2 className="text-lg font-bold text-[var(--text)] mb-1">Context Palette</h2>
            <p className="text-xs text-[var(--text-dim)] mb-6">Drag items to the workspace</p>

            <div className="space-y-6">
                {sortedTypes.map(type => (
                    <div key={type}>
                        <h3 className="text-[11px] font-semibold text-[var(--text-dim)] uppercase tracking-widest mb-3">
                            {type}s
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {groupedItems[type].map(item => (
                                <div
                                    key={item.id}
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, item)}
                                    onClick={() => onItemSelect?.(item)}
                                    className={clsx(
                                        "px-3 py-2 rounded-full text-sm font-medium cursor-grab active:cursor-grabbing flex items-center gap-2 transition-all hover:scale-105 hover:shadow-md whitespace-nowrap",
                                        PILL_STYLES[item.type]
                                    )}
                                >
                                    <span className="material-symbols-rounded text-lg">{item.icon}</span>
                                    <span>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}

                {items.length === 0 && (
                    <div className="text-center py-8 text-[var(--text-dim)]">
                        <span className="material-symbols-rounded text-4xl opacity-30 block mb-3">dashboard_customize</span>
                        <p className="text-sm">No context items available</p>
                    </div>
                )}
            </div>
        </div>
    );
}

// Default context items for demo
export const DEFAULT_CONTEXT_ITEMS: ContextItem[] = [
    // Goals
    { id: 'goal-career', label: 'Find Role', icon: 'flag', type: 'Goal' },
    { id: 'goal-interview', label: 'Prepare Interview', icon: 'school', type: 'Goal' },

    // Constraints
    { id: 'constraint-remote', label: 'Remote Only', icon: 'home', type: 'Constraint' },
    { id: 'constraint-hours', label: 'Max 45 hrs/week', icon: 'schedule', type: 'Constraint' },
    { id: 'constraint-oncall', label: 'No On-Call', icon: 'phone_disabled', type: 'Constraint' },

    // Preferences
    { id: 'pref-ai', label: 'AI/Tech Sector', icon: 'smart_toy', type: 'Preference' },
    { id: 'pref-startup', label: 'Startup Culture', icon: 'rocket_launch', type: 'Preference' },

    // Actions
    { id: 'action-search', label: 'Search Jobs', icon: 'search', type: 'Action' },
    { id: 'action-apply', label: 'Apply Now', icon: 'send', type: 'Action' },
    { id: 'action-compare', label: 'Compare', icon: 'compare', type: 'Action' },

    // Context
    { id: 'context-senior', label: 'Senior Level', icon: 'trending_up', type: 'Context' },
    { id: 'context-location', label: 'US-based', icon: 'location_on', type: 'Context' },
];
