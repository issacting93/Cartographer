import { TurnAnnotation, TrajectoryMetrics, TrackedConstraint, Archetype } from '../types/annotation';

export function calculateTrajectory(
  turnAnnotations: TurnAnnotation[],
  constraints: TrackedConstraint[]
): TrajectoryMetrics {
  const userTurns = turnAnnotations.filter(t => t.speaker === 'user' && t.userSpecificity !== null);
  
  const initialSpecificity = userTurns.slice(0, 3).reduce((acc, t) => acc + (t.userSpecificity || 0), 0) / Math.max(1, Math.min(3, userTurns.length));
  const finalSpecificity = userTurns.slice(-3).reduce((acc, t) => acc + (t.userSpecificity || 0), 0) / Math.max(1, Math.min(3, userTurns.length));
  
  const totalRepairAttempts = turnAnnotations.filter(t => t.repairAttempted).length;
  const successfulRepairs = turnAnnotations.filter(t => t.repairAttempted && t.repairSuccess).length;

  const totalViolations = constraints.filter(c => c.violatedAtTurn !== null).length;
  
  // Basic half-life calculation (turns until first violation)
  const violationTurns = constraints
    .filter(c => c.violatedAtTurn !== null)
    .map(c => (c.violatedAtTurn as number) - c.statedAtTurn);
  const constraintHalfLife = violationTurns.length > 0
    ? violationTurns.reduce((acc, v) => acc + v, 0) / violationTurns.length
    : null;

  const restatementCount = constraints.reduce((acc, c) => acc + c.restatementTurns.length, 0);

  // Agency Collapse Index: Higher is worse
  // Factors: specificity drop, high violation rate, low repair success
  const specificityDelta = finalSpecificity - initialSpecificity;
  const violationRate = constraints.length > 0 ? totalViolations / constraints.length : 0;
  const repairFailureRate = totalRepairAttempts > 0 ? 1 - (successfulRepairs / totalRepairAttempts) : 0;
  
  const agencyCollapseIndex = (Math.max(0, -specificityDelta) * 1.0) + (violationRate * 3.0) + (repairFailureRate * 2.0);

  return {
    initialSpecificity,
    finalSpecificity,
    specificityDelta,
    collapseDetected: specificityDelta < -1.0,
    constraintsStated: constraints.length,
    constraintsViolated: totalViolations,
    constraintHalfLife,
    restatementCount,
    restatementLoops: constraints.filter(c => c.restatementTurns.length >= 2).length,
    agencyCollapseIndex,
    totalRepairAttempts,
    successfulRepairs,
    repairEfficiency: totalRepairAttempts > 0 ? successfulRepairs / totalRepairAttempts : 0,
  };
}

export function determineArchetype(
  turnAnnotations: TurnAnnotation[],
  trajectory: TrajectoryMetrics,
  constraints: TrackedConstraint[]
): { archetype: Archetype; confidence: 'high' | 'medium' | 'low' } {
  
  if (trajectory.agencyCollapseIndex > 5) {
    return { archetype: 'Provider Trap', confidence: 'high' };
  }
  
  if (trajectory.restatementLoops > 0 && trajectory.repairEfficiency < 0.3) {
    return { archetype: 'Hallucination Loop', confidence: 'medium' };
  }
  
  if (trajectory.specificityDelta < -1.5) {
    return { archetype: 'Passive Default', confidence: 'medium' };
  }

  if (trajectory.constraintsViolated > 0 && trajectory.totalRepairAttempts === 0) {
    return { archetype: 'Identity Shift', confidence: 'low' };
  }

  return { archetype: 'Mixed/Other', confidence: 'low' };
}
