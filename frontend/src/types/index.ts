/**
 * types/index.ts - Unified Type Definitions
 * 
 * All shared types for the CUI-Project frontend.
 * THIS IS THE SINGLE SOURCE OF TRUTH FOR TYPES.
 */

// ============= Context Types =============

export type ContextType = 'Goal' | 'Constraint' | 'Preference' | 'Session';

export interface ContextItem {
    id: string;
    type: ContextType;
    label: string;
    description?: string;
    icon: string;
    source: 'predefined' | 'session' | 'scenario';
    createdAt?: Date;
    violated?: boolean;
}

export interface Selection {
    type: 'text' | 'message' | 'context';
    content: string;
    sourceId?: string;
    item?: ContextItem;
}

// ============= Chat Types =============

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    turnNumber?: number;
    attachedContext?: ContextItem[];
    violatesConstraint?: boolean;
}

// ============= Study Types =============

export interface StudyMetrics {
    condition: 'baseline' | 'treatment';
    userId: string;
    taskId?: string;
    startTime: Date;
    endTime?: Date;

    // Primary metrics
    constraintRestatements: number;
    constraintViolationsDetected: number;
    repairTurns: number;

    // Turn tracking
    totalTurns: number;
    turnAtViolation?: number;
    turnAtCorrection?: number;

    // Treatment condition actions
    pinActions: number;
    contextLensQueries: number;
    taskSwitches: number;

    // New metrics for workspace
    contextAttachments: number;
    sessionContextCreated: number;
}

// ============= Workspace Types =============

export interface WorkspaceNode {
    id: string;
    label: string;
    icon: string;
    type: ContextType | 'Action' | 'Need' | 'Feeling' | 'Context';
}

export interface WorkspaceState {
    mode: 'chat' | 'canvas';
    sourceContext: ContextItem[];
    sessionContext: ContextItem[];
    attachedContext: ContextItem[];
    selection: Selection | null;
}

// ============= Legacy Compatibility =============
// These are kept for backwards compatibility with existing components

export interface ConstraintNode {
    id: string;
    type: 'Goal' | 'Constraint' | 'Preference' | 'Artifact' | 'Context';
    label: string;
    description?: string;
    active: boolean;
    pinned: boolean;
    created_at: string;
}

export interface TaskObject {
    id: string;
    user_id: string;
    name: string;
    description?: string;
    status: 'active' | 'suspended' | 'completed' | 'archived';
    nodes: ConstraintNode[];
    created_at: string;
    updated_at: string;
    metrics: {
        conversation_turns: number;
        restatement_count: number;
        constraint_violations: number;
        interruption_count: number;
    };
}
