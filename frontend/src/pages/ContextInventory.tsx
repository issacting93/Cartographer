/**
 * ContextInventory.tsx - BLOOM Design System
 * 
 * Full-page Context Inventory implementing the three-zone architecture:
 * 1. Context Palette (left) - Draggable pills
 * 2. Hex Workspace (center) - 6-node composition grid
 * 3. Output Bar (bottom) - Sentence preview + speak
 */

import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { HexWorkspace, WorkspaceNode } from '../components/HexWorkspace';
import { ContextPalette, DEFAULT_CONTEXT_ITEMS } from '../components/ContextPalette';

export default function ContextInventory() {
    // Hex workspace state
    const [slots, setSlots] = useState<(WorkspaceNode | null)[]>([null, null, null, null, null, null]);
    const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

    // Build sentence from selection
    const sentence = useMemo(() => {
        if (selectedIndices.length === 0) return '';

        const words = selectedIndices
            .map(i => slots[i])
            .filter(Boolean)
            .map(node => node!.label);

        if (words.length === 0) return '';
        if (words.length === 1) return words[0];

        return words.join(' → ');
    }, [slots, selectedIndices]);

    const handleSpeak = () => {
        if (!sentence) return;
        const utterance = new SpeechSynthesisUtterance(sentence);
        utterance.rate = 0.9;
        speechSynthesis.speak(utterance);
    };

    const handleClear = () => {
        setSelectedIndices([]);
    };

    const handleClearAll = () => {
        setSlots([null, null, null, null, null, null]);
        setSelectedIndices([]);
    };

    const filledCount = slots.filter(Boolean).length;

    return (
        <div className="h-screen flex flex-col bg-[var(--bg-subtle)] overflow-hidden">
            {/* Header */}
            <header className="bg-[var(--black)] px-6 py-3 flex items-center justify-between flex-shrink-0">
                <div className="flex items-center gap-3">
                    <Link to="/" className="text-[var(--gray-dark)] hover:text-white transition-colors">
                        <span className="material-symbols-rounded">arrow_back</span>
                    </Link>
                    <div className="flex items-center gap-2">
                        <span className="material-symbols-rounded text-[var(--yellow)]">hexagon</span>
                        <h1 className="text-white font-bold">Context Inventory</h1>
                    </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-[var(--gray-dark)]">
                    <span className="w-2 h-2 rounded-full bg-[var(--green)] animate-pulse"></span>
                    BLOOM v1.1
                </div>
            </header>

            {/* Main Content - Side by Side Layout */}
            <div className="flex-1 flex overflow-hidden">

                {/* Left Panel: Context Palette */}
                <div className="w-80 bg-white border-r border-[var(--gray)] flex-shrink-0 overflow-y-auto">
                    <ContextPalette
                        items={DEFAULT_CONTEXT_ITEMS}
                    />
                </div>

                {/* Right Panel: Workspace + Output */}
                <div className="flex-1 flex flex-col">

                    {/* Hex Workspace */}
                    <div className="flex-1 flex flex-col items-center justify-center p-8">
                        <p className="text-xs text-[var(--text-dim)] uppercase tracking-wide mb-6">
                            Drag pills to slots • Trace a path to compose
                        </p>

                        <div className="bg-white rounded-3xl shadow-lg p-8 border border-[var(--gray)]">
                            <HexWorkspace
                                slots={slots}
                                selectedIndices={selectedIndices}
                                onSlotsChange={setSlots}
                                onSelectionChange={setSelectedIndices}
                            />
                        </div>

                        <div className="mt-6 flex gap-3">
                            <button
                                onClick={handleClear}
                                disabled={selectedIndices.length === 0}
                                className="px-4 py-2 bg-white border border-[var(--gray)] rounded-full text-sm text-[var(--text-dim)] hover:border-[var(--black)] hover:text-[var(--black)] disabled:opacity-30 transition-all flex items-center gap-2"
                            >
                                <span className="material-symbols-rounded text-lg">refresh</span>
                                Reset Path
                            </button>
                            <button
                                onClick={handleClearAll}
                                disabled={filledCount === 0}
                                className="px-4 py-2 bg-white border border-[var(--gray)] rounded-full text-sm text-[var(--text-dim)] hover:border-[var(--orange)] hover:text-[var(--orange)] disabled:opacity-30 transition-all flex items-center gap-2"
                            >
                                <span className="material-symbols-rounded text-lg">delete</span>
                                Clear All
                            </button>
                        </div>
                    </div>

                    {/* Output Bar */}
                    <div className="bg-white border-t border-[var(--gray)] px-8 py-5 flex-shrink-0">
                        <div className="flex items-center gap-4">
                            <div className="flex-1 min-h-[56px] px-6 py-4 bg-[var(--bg-subtle)] rounded-2xl flex items-center border border-[var(--gray)]">
                                {sentence ? (
                                    <span className="text-[var(--text)] font-medium text-lg">{sentence}</span>
                                ) : (
                                    <span className="text-[var(--text-dim)]">Trace a path through the workspace to compose...</span>
                                )}
                            </div>
                            <button
                                onClick={handleSpeak}
                                disabled={!sentence}
                                className="w-14 h-14 rounded-full bg-[var(--yellow)] text-[var(--black)] flex items-center justify-center hover:scale-105 hover:shadow-lg disabled:opacity-30 disabled:hover:scale-100 transition-all"
                            >
                                <span className="material-symbols-rounded text-2xl">play_arrow</span>
                            </button>
                        </div>

                        {/* Stats */}
                        <div className="flex justify-between mt-4 text-xs text-[var(--text-dim)]">
                            <span>Slots: <strong className="text-[var(--text)]">{filledCount}/6</strong></span>
                            <span>Path: <strong className="text-[var(--yellow)]">{selectedIndices.length} nodes</strong></span>
                            <span className="opacity-50">CUI 2026 Prototype</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
