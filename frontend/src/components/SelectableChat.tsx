/**
 * SelectableChat.tsx - Chat with Pin-to-Task capability
 * 
 * Wraps any chat content and adds text selection → constraint promotion.
 * Implements the "Pin to Task" pattern from the CII design.
 */

import { useRef, ReactNode } from 'react';
import { useTextSelection } from '../hooks/useTextSelection';
import { PinButton } from './PinButton';
import type { ContextType } from '../types/index';

interface SelectableChatProps {
    children: ReactNode;
    onPin: (text: string, type: ContextType) => void;
    enabled?: boolean;
}

export function SelectableChat({ children, onPin, enabled = true }: SelectableChatProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    const {
        selectedText,
        selectionRect,
        clearSelection
    } = useTextSelection({
        containerRef,
        minLength: 5, // At least 5 chars to show pin button
        enabled,
    });

    const handlePin = (text: string, type: ContextType) => {
        onPin(text, type);
        clearSelection();
    };

    return (
        <div ref={containerRef} className="relative">
            {children}

            {selectedText && (
                <PinButton
                    selectedText={selectedText}
                    selectionRect={selectionRect}
                    onPin={handlePin}
                    onClose={clearSelection}
                />
            )}
        </div>
    );
}

export default SelectableChat;
