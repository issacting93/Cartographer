/**
 * PinButton.tsx - Floating Pin-to-Task Button
 * 
 * Appears when text is selected, allowing users to promote text to constraint nodes.
 * Implements the "Selection → Promotion → Reification" pattern from the paper.
 */

import { useState, useEffect } from 'react';
import type { ContextType } from '../types/index';

interface PinButtonProps {
    selectedText: string;
    selectionRect: DOMRect | null;
    onPin: (text: string, type: ContextType) => void;
    onClose: () => void;
}

const TYPE_OPTIONS: { type: ContextType; label: string; icon: string; color: string }[] = [
    { type: 'Goal', label: 'Goal', icon: 'flag', color: 'var(--green)' },
    { type: 'Constraint', label: 'Constraint', icon: 'lock', color: 'var(--red)' },
    { type: 'Preference', label: 'Preference', icon: 'favorite', color: 'var(--yellow)' },
];

export function PinButton({ selectedText, selectionRect, onPin, onClose }: PinButtonProps) {
    const [showTypeSelector, setShowTypeSelector] = useState(false);
    const [position, setPosition] = useState({ top: 0, left: 0 });

    // Calculate position based on selection
    useEffect(() => {
        if (selectionRect) {
            setPosition({
                top: selectionRect.bottom + window.scrollY + 8,
                left: selectionRect.left + window.scrollX + (selectionRect.width / 2) - 20,
            });
        }
    }, [selectionRect]);

    if (!selectionRect || !selectedText) return null;

    const handlePinClick = () => {
        setShowTypeSelector(true);
    };

    const handleTypeSelect = (type: ContextType) => {
        onPin(selectedText, type);
        setShowTypeSelector(false);
        onClose();
    };

    return (
        <div
            className="pin-button-container"
            style={{
                position: 'absolute',
                top: position.top,
                left: position.left,
                zIndex: 1000,
            }}
        >
            {!showTypeSelector ? (
                // Initial Pin button
                <button
                    onClick={handlePinClick}
                    className="pin-button"
                    title="Pin to Context"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '8px 12px',
                        background: 'var(--yellow)',
                        color: 'var(--black)',
                        border: 'none',
                        borderRadius: '20px',
                        cursor: 'pointer',
                        fontWeight: 600,
                        fontSize: '13px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        transition: 'all 0.2s ease',
                    }}
                >
                    <span className="material-symbols-rounded" style={{ fontSize: '18px' }}>push_pin</span>
                    Pin
                </button>
            ) : (
                // Type selector
                <div
                    className="pin-type-selector"
                    style={{
                        display: 'flex',
                        gap: '4px',
                        padding: '8px',
                        background: 'white',
                        borderRadius: '12px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                        border: '1px solid var(--gray)',
                    }}
                >
                    {TYPE_OPTIONS.map(({ type, label, icon, color }) => (
                        <button
                            key={type}
                            onClick={() => handleTypeSelect(type)}
                            title={`Pin as ${label}`}
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: '4px',
                                padding: '8px 12px',
                                background: 'transparent',
                                border: '2px solid transparent',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.background = 'var(--bg-subtle)';
                                e.currentTarget.style.borderColor = color;
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.background = 'transparent';
                                e.currentTarget.style.borderColor = 'transparent';
                            }}
                        >
                            <span
                                className="material-symbols-rounded"
                                style={{ fontSize: '20px', color }}
                            >
                                {icon}
                            </span>
                            <span style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-dim)' }}>
                                {label}
                            </span>
                        </button>
                    ))}
                    <button
                        onClick={onClose}
                        title="Cancel"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: '8px',
                            background: 'transparent',
                            border: 'none',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            color: 'var(--text-dim)',
                        }}
                    >
                        <span className="material-symbols-rounded" style={{ fontSize: '18px' }}>close</span>
                    </button>
                </div>
            )}
        </div>
    );
}

export default PinButton;
