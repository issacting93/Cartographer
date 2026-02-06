/**
 * constants/styling.ts - BLOOM Design System Constants
 * 
 * Centralized icon and color mappings for context types.
 * Import from here instead of redefining in each component.
 */

import type { ContextType } from '../types/index';

// ============= Icons (Material Symbols) =============

export const TYPE_ICONS: Record<string, string> = {
    Goal: 'flag',
    Constraint: 'lock',
    Preference: 'favorite',
    Session: 'bookmark',
    Action: 'play_arrow',
    Need: 'priority_high',
    Feeling: 'mood',
    Context: 'visibility',
    Artifact: 'description',
};

// ============= Colors (BLOOM Palette) =============

export const TYPE_COLORS: Record<ContextType, {
    bg: string;
    bgLight: string;
    text: string;
    border: string;
}> = {
    Goal: {
        bg: 'bg-[var(--green)]',
        bgLight: 'bg-[var(--green)] bg-opacity-20',
        text: 'text-[var(--green)]',
        border: 'border-[var(--green)]',
    },
    Constraint: {
        bg: 'bg-[var(--yellow)]',
        bgLight: 'bg-[var(--yellow)] bg-opacity-20',
        text: 'text-[var(--yellow)]',
        border: 'border-[var(--yellow)]',
    },
    Preference: {
        bg: 'bg-[var(--orange)]',
        bgLight: 'bg-[var(--orange)] bg-opacity-20',
        text: 'text-[var(--orange)]',
        border: 'border-[var(--orange)]',
    },
    Session: {
        bg: 'bg-[var(--black)]',
        bgLight: 'bg-[var(--black)] bg-opacity-10',
        text: 'text-[var(--text)]',
        border: 'border-[var(--gray-dark)]',
    },
};

// Pill styles for context palette
export const PILL_STYLES: Record<string, string> = {
    Goal: 'bg-[var(--green)] text-white',
    Constraint: 'bg-[var(--yellow)] text-[var(--black)]',
    Preference: 'bg-[var(--orange)] text-white',
    Need: 'bg-[var(--orange)] text-white',
    Feeling: 'bg-[var(--yellow)] text-[var(--black)]',
    Action: 'bg-white text-[var(--black)] border border-[var(--gray)]',
    Context: 'bg-[var(--black)] text-white',
    Session: 'bg-[var(--black)] bg-opacity-80 text-white',
};

// Combined border + bg classes for cards
export const TYPE_CARD_STYLES: Record<string, string> = {
    Goal: 'bg-[var(--green)] bg-opacity-20 border-[var(--green)]',
    Constraint: 'bg-[var(--yellow)] bg-opacity-20 border-[var(--yellow)]',
    Preference: 'bg-[var(--orange)] bg-opacity-20 border-[var(--orange)]',
    Session: 'bg-[var(--gray)] bg-opacity-20 border-[var(--gray-dark)]',
};

// ============= Helper Functions =============

export function getTypeIcon(type: string): string {
    return TYPE_ICONS[type] || 'help';
}

export function getTypeColor(type: ContextType) {
    return TYPE_COLORS[type] || TYPE_COLORS.Session;
}
