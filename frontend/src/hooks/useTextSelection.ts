/**
 * useTextSelection.ts - Text Selection Hook
 * 
 * Detects text selection within a container and provides selection state.
 * Used for the "Pin to Task" feature - promoting text to constraint nodes.
 */

import { useState, useEffect, useCallback, RefObject } from 'react';

export interface TextSelectionState {
    selectedText: string;
    isSelecting: boolean;
    selectionRect: DOMRect | null;
    sourceElement: HTMLElement | null;
}

export interface UseTextSelectionOptions {
    containerRef: RefObject<HTMLElement>;
    minLength?: number; // Minimum characters to trigger selection
    enabled?: boolean;
}

export function useTextSelection({
    containerRef,
    minLength = 3,
    enabled = true,
}: UseTextSelectionOptions): TextSelectionState & { clearSelection: () => void } {
    const [state, setState] = useState<TextSelectionState>({
        selectedText: '',
        isSelecting: false,
        selectionRect: null,
        sourceElement: null,
    });

    const clearSelection = useCallback(() => {
        window.getSelection()?.removeAllRanges();
        setState({
            selectedText: '',
            isSelecting: false,
            selectionRect: null,
            sourceElement: null,
        });
    }, []);

    useEffect(() => {
        if (!enabled) return;

        const handleSelectionChange = () => {
            const selection = window.getSelection();

            if (!selection || selection.isCollapsed) {
                setState(prev => ({
                    ...prev,
                    selectedText: '',
                    isSelecting: false,
                    selectionRect: null,
                }));
                return;
            }

            const text = selection.toString().trim();

            // Check if selection is within our container
            const anchorNode = selection.anchorNode;
            const container = containerRef.current;

            if (!container || !anchorNode) return;

            const isWithinContainer = container.contains(anchorNode);

            if (!isWithinContainer || text.length < minLength) {
                return;
            }

            // Get selection rectangle for positioning the pin button
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();

            setState({
                selectedText: text,
                isSelecting: true,
                selectionRect: rect,
                sourceElement: anchorNode.parentElement,
            });
        };

        // Listen for selection changes
        document.addEventListener('selectionchange', handleSelectionChange);

        // Also listen for mouseup to catch the end of selection
        const handleMouseUp = () => {
            setTimeout(handleSelectionChange, 10);
        };
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('selectionchange', handleSelectionChange);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [containerRef, minLength, enabled]);

    return { ...state, clearSelection };
}

export default useTextSelection;
