/**
 * annotation.ts - Types for Dataset Classification Tool
 *
 * Implements the multi-layer classification scheme from Dataset_Classification_Plan.md
 */

// Layer 1: Interaction-Level Metadata
export type Domain = 'career' | 'travel' | 'code' | 'education' | 'creative' | 'general' | 'other';
export type TaskComplexity = 'single-goal' | 'multi-goal' | 'exploratory';
export type Source = 'WildChat' | 'ChatbotArena' | 'OASST' | 'Custom';

export interface InteractionMetadata {
  id: string;
  source: Source;
  domain: Domain;
  taskComplexity: TaskComplexity;
  totalTurns: number;
  annotatorId?: string;
  annotatedAt?: Date;
}

// Layer 2: Turn-Level Constraint Tracking
export type ConstraintType = 'goal' | 'hard' | 'soft' | 'preference' | null;
export type ViolationType = 'direct' | 'drift' | 'implicit' | null;
export type RepairType = 'restatement' | 'reference' | 'redirect' | 'abandon' | null;
export type UserStance = 'directive' | 'collaborative' | 'passive' | 'reactive';

export interface TurnAnnotation {
  turnNumber: number;
  speaker: 'user' | 'assistant';
  content: string;

  // Constraint Events
  constraintStated: boolean;
  constraintType: ConstraintType;
  constraintText: string | null;
  constraintId?: string; // For tracking across turns

  // Violation Events
  constraintViolated: boolean;
  violatedConstraintId: string | null;
  violationType: ViolationType;

  // Repair Events
  repairAttempted: boolean;
  repairType: RepairType;
  repairSuccess: boolean | null;

  // Agency Markers
  userSpecificity: 1 | 2 | 3 | 4 | 5 | null; // Only for user turns
  userStance: UserStance | null; // Only for user turns
  passiveAcceptance: boolean; // "ok", "sure", "thanks" patterns
}

// Layer 3: Trajectory (Computed)
export interface TrajectoryMetrics {
  // Agency Collapse Metrics
  initialSpecificity: number; // Mean of turns 1-3
  finalSpecificity: number; // Mean of final 3 turns
  specificityDelta: number; // Change over time
  collapseDetected: boolean; // Δ < -1.0

  // Constraint Maintenance
  constraintsStated: number;
  constraintsViolated: number;
  constraintHalfLife: number | null; // Median turns to first violation
  restatementCount: number;
  restatementLoops: number; // Constraint restated 2+ times

  // Agency Collapse Index
  agencyCollapseIndex: number;

  // Repair Metrics
  totalRepairAttempts: number;
  successfulRepairs: number;
  repairEfficiency: number;
}

// Layer 4: Archetype
export type Archetype =
  | 'Provider Trap'
  | 'Hallucination Loop'
  | 'Identity Shift'
  | 'Canvas Hack'
  | 'Passive Default'
  | 'Mixed/Other';

// Full Annotated Interaction
export interface AnnotatedInteraction {
  metadata: InteractionMetadata;
  turns: TurnAnnotation[];
  trajectory: TrajectoryMetrics;
  archetype: Archetype;
  archetypeConfidence: 'high' | 'medium' | 'low';
  notes: string;
}

// For tracking constraints across turns
export interface TrackedConstraint {
  id: string;
  text: string;
  type: ConstraintType;
  statedAtTurn: number;
  violatedAtTurn: number | null;
  restatementTurns: number[];
}

// Raw interaction format (input)
export interface RawInteraction {
  id: string;
  source?: string;
  messages: Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
  }>;
}
