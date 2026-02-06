/**
 * Chat API Client
 * 
 * Communicates with the LLM-backed chat endpoint.
 */

import type { ContextItem, ChatMessage } from '../types/index';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatRequest {
    message: string;
    constraints: ConstraintPayload[];
    history: MessagePayload[];
    condition?: 'baseline' | 'treatment';
}

export interface ChatResponse {
    content: string;
    constraint_violations: string[];
    model_used: string;
}

interface ConstraintPayload {
    id: string;
    type: string;
    label: string;
    description?: string;
}

interface MessagePayload {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

/**
 * Send a message to the LLM-backed chat endpoint.
 */
export async function sendMessage(
    message: string,
    constraints: ContextItem[],
    history: ChatMessage[]
): Promise<ChatResponse> {
    const payload: ChatRequest = {
        message,
        constraints: constraints.map(c => ({
            id: c.id,
            type: c.type,
            label: c.label,
            description: c.description
        })),
        history: history
            .filter(m => m.role !== 'system')
            .map(m => ({
                role: m.role,
                content: m.content
            })),
        condition: 'treatment'
    };

    const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Chat API error: ${error}`);
    }

    return response.json();
}

/**
 * Test the LLM connection.
 */
export async function testConnection(): Promise<{ status: string; response?: string; message?: string }> {
    const response = await fetch(`${API_BASE}/api/chat/test`, {
        method: 'POST'
    });
    return response.json();
}

/**
 * Check if we should use live LLM or scripted responses.
 */
export function useLiveLLM(): boolean {
    return import.meta.env.VITE_USE_LIVE_LLM === 'true';
}
