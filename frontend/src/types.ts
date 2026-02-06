export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  turnNumber?: number;
  violatesConstraint?: boolean;
}

export interface StudyMetrics {
  condition: 'baseline' | 'treatment';
  userId: string;
  taskId?: string;
  startTime: Date;
  endTime?: Date;

  // Primary metrics
  constraintRestatements: number;
  constraintViolationsDetected: number;
  repairTurns: number; // turns to correct after violation

  // Turn tracking
  totalTurns: number;
  turnAtViolation?: number;
  turnAtCorrection?: number;

  // User actions (treatment only)
  pinActions: number;
  contextLensQueries: number;
  taskSwitches: number;
}

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
