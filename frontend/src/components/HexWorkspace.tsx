/**
 * HexWorkspace.tsx - BLOOM Design System
 * 
 * 6-node hexagonal workspace for drag-and-drop context composition.
 * Core interaction pattern from CUI 2026 paper: "Tasks, Not Turns"
 */

import { useState } from 'react';
import clsx from 'clsx';

export interface WorkspaceNode {
    id: string;
    label: string;
    icon: string;
    type?: string;
}

export interface HexWorkspaceProps {
    slots: (WorkspaceNode | null)[];
    selectedIndices: number[];
    onSlotsChange: (newSlots: (WorkspaceNode | null)[]) => void;
    onSelectionChange: (selectedIndices: number[]) => void;
}

// 6-Node Geometry
const HEX_POSITIONS = [
    { x: 130, y: 34 },    // Top (0)
    { x: 46, y: 86 },     // Upper left (1)
    { x: 214, y: 86 },    // Upper right (2)
    { x: 46, y: 174 },    // Lower left (3)
    { x: 214, y: 174 },   // Lower right (4)
    { x: 130, y: 226 },   // Bottom (5)
];

// Default Adjacency Graph
const HEX_CONNECTIONS = [
    [0, 1], [0, 2],
    [1, 2],
    [1, 3], [2, 4],
    [3, 4],
    [3, 5], [4, 5],
];

export function HexWorkspace({
    slots,
    selectedIndices,
    onSlotsChange,
    onSelectionChange
}: HexWorkspaceProps) {
    const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
    const [isInteracting, setIsInteracting] = useState(false);
    const [startNodeIndex, setStartNodeIndex] = useState<number | null>(null);
    const [pointerPos, setPointerPos] = useState<{ x: number, y: number } | null>(null);

    // --- Helpers ---
    const getEventPos = (e: React.PointerEvent) => {
        const rect = e.currentTarget.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    };

    const getHitIndex = (x: number, y: number, radius = 40) => {
        return HEX_POSITIONS.findIndex(p => {
            const dx = x - p.x;
            const dy = y - p.y;
            return Math.sqrt(dx * dx + dy * dy) < radius;
        });
    };

    // --- Drag & Drop (Node Placement) ---
    const handleDragOver = (e: React.DragEvent, index: number) => {
        e.preventDefault();
        setDragOverIndex(index);
    };

    const handleDragLeave = () => {
        setDragOverIndex(null);
    };

    const handleDrop = (e: React.DragEvent, index: number) => {
        e.preventDefault();
        setDragOverIndex(null);
        try {
            const raw = e.dataTransfer.getData('application/json');
            const data = JSON.parse(raw);
            if (data.id && data.label) {
                const newSlots = [...slots];
                newSlots[index] = {
                    id: data.id,
                    label: data.label,
                    icon: data.icon || 'circle',
                    type: data.type || 'Context'
                };
                onSlotsChange(newSlots);
            }
        } catch (err) {
            console.error("Drop failed", err);
        }
    };

    const removeNode = (e: React.MouseEvent, index: number) => {
        e.stopPropagation();
        const newSlots = [...slots];
        newSlots[index] = null;
        onSlotsChange(newSlots);
        if (selectedIndices.includes(index)) {
            onSelectionChange(selectedIndices.filter(i => i !== index));
        }
    };

    // --- Unified Pointer Interaction (Trace Selection) ---
    const handlePointerDown = (e: React.PointerEvent) => {
        const pos = getEventPos(e);
        const hitIndex = getHitIndex(pos.x, pos.y);

        if (hitIndex !== -1 && slots[hitIndex]) {
            if (e.pointerType === 'touch') {
                e.preventDefault();
            }

            setIsInteracting(true);
            setStartNodeIndex(hitIndex);
            setPointerPos(pos);

            const container = e.currentTarget as HTMLElement;
            try {
                container.setPointerCapture(e.pointerId);
            } catch (err) { }

            onSelectionChange([hitIndex]);
        }
    };

    const handlePointerMove = (e: React.PointerEvent) => {
        if (!isInteracting || startNodeIndex === null) return;

        const pos = getEventPos(e);
        setPointerPos(pos);

        const hitIndex = getHitIndex(pos.x, pos.y, 30);
        if (hitIndex !== -1 && slots[hitIndex]) {
            const lastIdx = selectedIndices[selectedIndices.length - 1];
            if (hitIndex !== lastIdx && !selectedIndices.includes(hitIndex)) {
                onSelectionChange([...selectedIndices, hitIndex]);
            }
        }
    };

    const handlePointerUp = (e: React.PointerEvent) => {
        if (!isInteracting) return;

        setIsInteracting(false);
        setStartNodeIndex(null);
        setPointerPos(null);

        try {
            const container = e.currentTarget as HTMLElement;
            if (container.hasPointerCapture(e.pointerId)) {
                container.releasePointerCapture(e.pointerId);
            }
        } catch (err) { }
    };

    return (
        <div
            className="relative w-[300px] h-[320px] mx-auto select-none touch-none"
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
        >
            {/* SVG Lines Layer */}
            <svg className="absolute top-0 left-0 w-full h-full pointer-events-none z-0">
                {/* Background Grid */}
                {HEX_CONNECTIONS.map(([source, target], i) => (
                    <line
                        key={`bg-${i}`}
                        x1={HEX_POSITIONS[source].x}
                        y1={HEX_POSITIONS[source].y}
                        x2={HEX_POSITIONS[target].x}
                        y2={HEX_POSITIONS[target].y}
                        stroke="var(--gray)"
                        strokeWidth={2}
                        strokeLinecap="round"
                    />
                ))}

                {/* Active Selection Path (Yellow) */}
                {selectedIndices.length > 1 && (
                    <polyline
                        points={selectedIndices.map(i => {
                            const p = HEX_POSITIONS[i];
                            return p ? `${p.x},${p.y}` : '0,0';
                        }).join(' ')}
                        fill="none"
                        stroke="var(--yellow)"
                        strokeWidth={4}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                )}

                {/* Dragging Line Indicator */}
                {isInteracting && pointerPos && startNodeIndex !== null && HEX_POSITIONS[startNodeIndex] && (
                    <line
                        x1={HEX_POSITIONS[startNodeIndex].x}
                        y1={HEX_POSITIONS[startNodeIndex].y}
                        x2={pointerPos.x}
                        y2={pointerPos.y}
                        stroke="var(--yellow)"
                        strokeWidth={4}
                        strokeLinecap="round"
                        opacity={0.7}
                    />
                )}
            </svg>

            {/* Nodes Layer */}
            {HEX_POSITIONS.map((pos, i) => {
                const node = slots[i];
                const isSelected = selectedIndices.includes(i);
                const isDragOver = dragOverIndex === i;
                const isLast = selectedIndices[selectedIndices.length - 1] === i;

                return (
                    <div
                        key={i}
                        className={clsx(
                            "absolute w-20 h-20 rounded-full flex flex-col items-center justify-center gap-1 -ml-10 -mt-10 z-10 group transition-all duration-150",
                            !node && "bg-white border-2 border-dashed border-[var(--gray)] text-[var(--text-dim)]",
                            !node && isDragOver && "border-[var(--yellow)] bg-yellow-50 scale-110",
                            node && !isSelected && "bg-[var(--black)] text-white cursor-pointer",
                            node && isSelected && !isLast && "bg-[var(--black)] text-white ring-2 ring-[var(--yellow)] ring-offset-2 scale-110",
                            node && isLast && "bg-[var(--yellow)] text-[var(--black)] scale-110 shadow-lg"
                        )}
                        style={{ left: pos.x, top: pos.y }}
                        onDragOver={(e) => handleDragOver(e, i)}
                        onDragLeave={handleDragLeave}
                        onDrop={(e) => handleDrop(e, i)}
                    >
                        {node ? (
                            <>
                                <span className="material-symbols-rounded text-2xl">{node.icon}</span>
                                <span className="text-[10px] font-semibold uppercase tracking-wide truncate max-w-[60px]">
                                    {node.label}
                                </span>
                                <button
                                    onClick={(e) => removeNode(e, i)}
                                    className="absolute -top-1 -right-1 w-5 h-5 bg-white border border-[var(--gray)] rounded-full flex items-center justify-center text-[var(--text-dim)] hover:text-[var(--orange)] hover:border-[var(--orange)] opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <span className="material-symbols-rounded text-sm">close</span>
                                </button>
                            </>
                        ) : (
                            <span className="material-symbols-rounded text-2xl">add</span>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
