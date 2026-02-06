/**
 * ConstraintSidebar.tsx - BLOOM Design System
 * 
 * Simple persistent constraint list for the Treatment condition.
 * Key differentiator: constraints are always visible and clickable
 * for quick reference during repair.
 */

import clsx from 'clsx';

export interface ConstraintItem {
    id: string;
    type: 'Goal' | 'Constraint' | 'Preference';
    label: string;
    description?: string;
    violated?: boolean;
}

interface ConstraintSidebarProps {
    constraints: ConstraintItem[];
    onConstraintClick?: (constraint: ConstraintItem) => void;
    violatedIds?: string[];
    className?: string;
}

const TYPE_ICONS: Record<string, string> = {
    Goal: 'flag',
    Constraint: 'lock',
    Preference: 'favorite',
};

const TYPE_COLORS: Record<string, string> = {
    Goal: 'bg-[var(--green)] bg-opacity-20 border-[var(--green)]',
    Constraint: 'bg-[var(--yellow)] bg-opacity-20 border-[var(--yellow)]',
    Preference: 'bg-[var(--orange)] bg-opacity-20 border-[var(--orange)]',
};

export function ConstraintSidebar({
    constraints,
    onConstraintClick,
    violatedIds = [],
    className
}: ConstraintSidebarProps) {
    return (
        <div className={clsx("flex flex-col bg-white rounded-2xl border border-[var(--gray)] overflow-hidden", className)}>
            {/* Header */}
            <div className="bg-[var(--black)] px-5 py-4">
                <div className="flex items-center gap-3">
                    <span className="material-symbols-rounded text-[var(--yellow)]">inventory_2</span>
                    <h2 className="text-white font-bold">Context Inventory</h2>
                </div>
                <p className="text-[var(--gray-dark)] text-xs mt-1">
                    Your constraints are always visible here
                </p>
            </div>

            {/* Constraint List */}
            <div className="flex-1 p-4 space-y-3 overflow-y-auto">
                <p className="text-xs text-[var(--text-dim)] mb-4">
                    Click a constraint to reference it in your message
                </p>

                {constraints.map((constraint) => {
                    const isViolated = violatedIds.includes(constraint.id);

                    return (
                        <button
                            key={constraint.id}
                            onClick={() => onConstraintClick?.(constraint)}
                            className={clsx(
                                "w-full p-4 rounded-xl border-2 text-left transition-all",
                                "hover:scale-[1.02] hover:shadow-md",
                                TYPE_COLORS[constraint.type],
                                isViolated && "ring-2 ring-[var(--orange)] ring-offset-2 animate-pulse"
                            )}
                        >
                            <div className="flex items-start gap-3">
                                <span className={clsx(
                                    "material-symbols-rounded text-xl",
                                    isViolated ? "text-[var(--orange)]" : "text-[var(--text)]"
                                )}>
                                    {isViolated ? 'warning' : TYPE_ICONS[constraint.type]}
                                </span>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                        <span className="text-[10px] font-bold uppercase tracking-wide text-[var(--text-dim)]">
                                            {constraint.type}
                                        </span>
                                        {isViolated && (
                                            <span className="text-[10px] font-bold uppercase tracking-wide text-[var(--orange)] bg-[var(--orange)] bg-opacity-20 px-2 py-0.5 rounded-full">
                                                VIOLATED
                                            </span>
                                        )}
                                    </div>
                                    <div className="font-medium text-[var(--text)] mt-1">
                                        {constraint.label}
                                    </div>
                                    {constraint.description && (
                                        <div className="text-xs text-[var(--text-dim)] mt-1">
                                            {constraint.description}
                                        </div>
                                    )}
                                </div>
                                <span className="material-symbols-rounded text-[var(--gray-dark)] opacity-50">
                                    arrow_forward
                                </span>
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* Footer */}
            <div className="border-t border-[var(--gray)] px-4 py-3 bg-[var(--bg-subtle)]">
                <div className="flex items-center gap-2 text-xs text-[var(--text-dim)]">
                    <span className="material-symbols-rounded text-sm text-[var(--green)]">check_circle</span>
                    <span>{constraints.length} constraints active</span>
                </div>
            </div>
        </div>
    );
}
