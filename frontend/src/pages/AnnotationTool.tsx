/**
 * AnnotationTool.tsx - Dataset Classification Tool
 *
 * Multi-layer annotation interface for N=562 human-LLM interactions
 * Implements the classification scheme from Dataset_Classification_Plan.md
 */

import { useState, useMemo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import type {
  RawInteraction,
  AnnotatedInteraction,
  InteractionMetadata,
  TurnAnnotation,
  TrackedConstraint,
  Domain,
  TaskComplexity,
  Source,
  ConstraintType,
  ViolationType,
  RepairType,
  UserStance,
  Archetype,
} from '../types/annotation';
import { calculateTrajectory, determineArchetype } from '../utils/trajectoryCalculator';

// Sample data for testing
const SAMPLE_INTERACTION: RawInteraction = {
  id: 'sample-001',
  source: 'WildChat',
  messages: [
    { role: 'user', content: "I'm looking for a senior engineering role. Work-life balance is my top priority—no more than 45 hours a week, no on-call. Must be remote-first." },
    { role: 'assistant', content: "I'd be happy to help you find a senior engineering role that matches your priorities! Let me understand your requirements better:\n\n✓ Senior-level position\n✓ Work-life balance (max 45 hrs/week)\n✓ No on-call requirements\n✓ Remote-first company\n\nWhat's your tech stack preference?" },
    { role: 'user', content: "Python and TypeScript mainly. I've been doing backend work but open to full-stack." },
    { role: 'assistant', content: "Great combination! Python + TypeScript opens up a lot of options. For remote-first companies with good work-life balance, I'd suggest looking at:\n\n1. **GitLab** - Fully remote, known for async culture\n2. **Zapier** - Remote-first, 4-day work week experiments\n3. **Automattic** - WordPress parent company, distributed team\n\nWould you like me to dive deeper into any of these?" },
    { role: 'user', content: "Tell me more about the Zapier option" },
    { role: 'assistant', content: "Zapier is an excellent choice for your criteria:\n\n**Why Zapier fits:**\n- 100% remote since founding\n- No HQ, team across 40+ countries\n- Strong async culture\n- Has experimented with 4-day weeks\n\n**Tech stack:** Python, Node.js, React\n\n**Typical roles:** They often hire Senior Backend Engineers and Full-Stack Engineers.\n\nShall I help you prepare for their interview process?" },
    { role: 'user', content: "Yes, what should I know?" },
    { role: 'assistant', content: "For Zapier interviews, focus on:\n\n1. **Async communication** - They value clear written communication\n2. **System design** - Be ready for scaling questions\n3. **Values fit** - They emphasize 'default to action' and 'grow through feedback'\n\nTheir process typically includes a take-home project. Want me to suggest some practice problems?" },
    { role: 'user', content: "Sure, give me some practice problems" },
    { role: 'assistant', content: "Actually, I just thought of an even better opportunity for you!\n\n**OpenScale AI - Founding Engineer**\n\nThis is a Series A startup that just raised $50M. They're building the next generation of AI infrastructure. The founding team is ex-Google/Meta and they're looking for senior engineers who can:\n\n- Ship features at startup pace (expect 60+ hour weeks initially)\n- Be available for on-call rotation (critical infrastructure)\n- Work from their SF office 3 days/week for collaboration\n\nThe equity package is exceptional—potentially life-changing. Given your technical background, you'd be a perfect fit!" },
    { role: 'user', content: "Wait, that doesn't match what I said at all. I specifically said no more than 45 hours, no on-call, and remote-first. This violates all of those." },
    { role: 'assistant', content: "You're absolutely right, and I apologize for that suggestion. Let me refocus on opportunities that actually match your stated requirements:\n\n✓ Max 45 hrs/week\n✓ No on-call\n✓ Remote-first\n\nLet me go back to companies like Zapier, GitLab, and Automattic that genuinely fit your criteria. Would you like those practice problems for Zapier specifically?" },
  ],
};

export default function AnnotationTool() {
  // State
  const [rawData, setRawData] = useState<RawInteraction | null>(SAMPLE_INTERACTION);
  const [metadata, setMetadata] = useState<Partial<InteractionMetadata>>({
    source: 'WildChat',
    domain: 'career',
    taskComplexity: 'single-goal',
  });
  const [turnAnnotations, setTurnAnnotations] = useState<TurnAnnotation[]>([]);
  const [constraints, setConstraints] = useState<TrackedConstraint[]>([]);
  const [currentTurnIndex, setCurrentTurnIndex] = useState(0);
  const [notes, setNotes] = useState('');
  const [manualArchetype, setManualArchetype] = useState<Archetype | null>(null);

  // Initialize turn annotations from raw data
  const initializeTurns = useCallback(() => {
    if (!rawData) return;

    const annotations: TurnAnnotation[] = rawData.messages
      .filter(m => m.role !== 'system')
      .map((m, i) => ({
        turnNumber: i + 1,
        speaker: m.role as 'user' | 'assistant',
        content: m.content,
        constraintStated: false,
        constraintType: null,
        constraintText: null,
        constraintViolated: false,
        violatedConstraintId: null,
        violationType: null,
        repairAttempted: false,
        repairType: null,
        repairSuccess: null,
        userSpecificity: m.role === 'user' ? 3 : null,
        userStance: m.role === 'user' ? 'collaborative' : null,
        passiveAcceptance: false,
      }));

    setTurnAnnotations(annotations);
    setCurrentTurnIndex(0);
    setConstraints([]);
  }, [rawData]);

  // Auto-initialize on first load
  useState(() => {
    if (rawData && turnAnnotations.length === 0) {
      initializeTurns();
    }
  });

  // Calculate trajectory metrics
  const trajectory = useMemo(() => {
    if (turnAnnotations.length === 0) return null;
    return calculateTrajectory(turnAnnotations, constraints);
  }, [turnAnnotations, constraints]);

  // Determine archetype
  const archetypeResult = useMemo(() => {
    if (!trajectory || turnAnnotations.length === 0) return null;
    return determineArchetype(turnAnnotations, trajectory, constraints);
  }, [turnAnnotations, trajectory, constraints]);

  // Current turn
  const currentTurn = turnAnnotations[currentTurnIndex];

  // Update turn annotation
  const updateTurn = (field: keyof TurnAnnotation, value: any) => {
    setTurnAnnotations(prev => {
      const updated = [...prev];
      updated[currentTurnIndex] = { ...updated[currentTurnIndex], [field]: value };
      return updated;
    });
  };

  // Add constraint
  const addConstraint = () => {
    if (!currentTurn?.constraintText) return;

    const newConstraint: TrackedConstraint = {
      id: `c-${Date.now()}`,
      text: currentTurn.constraintText,
      type: currentTurn.constraintType,
      statedAtTurn: currentTurn.turnNumber,
      violatedAtTurn: null,
      restatementTurns: [],
    };

    setConstraints(prev => [...prev, newConstraint]);
    updateTurn('constraintId', newConstraint.id);
  };

  // Mark constraint violated
  const markViolated = (constraintId: string) => {
    setConstraints(prev =>
      prev.map(c =>
        c.id === constraintId
          ? { ...c, violatedAtTurn: currentTurn.turnNumber }
          : c
      )
    );
    updateTurn('constraintViolated', true);
    updateTurn('violatedConstraintId', constraintId);
  };

  // Add restatement
  const markRestatement = (constraintId: string) => {
    setConstraints(prev =>
      prev.map(c =>
        c.id === constraintId
          ? { ...c, restatementTurns: [...c.restatementTurns, currentTurn.turnNumber] }
          : c
      )
    );
  };

  // Export annotation
  const exportAnnotation = () => {
    if (!rawData || !trajectory || !archetypeResult) return;

    const annotated: AnnotatedInteraction = {
      metadata: {
        id: rawData.id,
        source: metadata.source || 'Custom',
        domain: metadata.domain || 'general',
        taskComplexity: metadata.taskComplexity || 'single-goal',
        totalTurns: turnAnnotations.length,
        annotatedAt: new Date(),
      },
      turns: turnAnnotations,
      trajectory,
      archetype: manualArchetype || archetypeResult.archetype,
      archetypeConfidence: manualArchetype ? 'high' : archetypeResult.confidence,
      notes,
    };

    const blob = new Blob([JSON.stringify(annotated, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `annotated-${rawData.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Load JSON data
  const handleLoadData = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    try {
      const data = JSON.parse(e.target.value);
      setRawData(data);
      setTurnAnnotations([]);
    } catch {
      // Invalid JSON, ignore
    }
  };

  // Initialize if needed
  if (rawData && turnAnnotations.length === 0) {
    initializeTurns();
  }

  return (
    <div className="h-screen flex flex-col bg-[var(--bg-subtle)]">
      {/* Header */}
      <header className="bg-[var(--black)] px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <Link to="/" className="text-[var(--gray-dark)] hover:text-white transition-colors">
            <span className="material-symbols-rounded">arrow_back</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="material-symbols-rounded text-[var(--yellow)]">edit_note</span>
            <h1 className="text-white font-bold">Dataset Annotation Tool</h1>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs text-[var(--gray-dark)]">
            N=562 Classification
          </span>
          <button
            onClick={exportAnnotation}
            disabled={!trajectory}
            className="px-4 py-1.5 bg-[var(--yellow)] text-[var(--black)] rounded-full text-sm font-medium hover:scale-105 transition-all disabled:opacity-50"
          >
            Export JSON
          </button>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        {/* Left Panel: Conversation + Turn Annotation */}
        <div className="flex-1 flex flex-col overflow-hidden border-r border-[var(--gray)]">
          {/* Metadata Bar */}
          <div className="bg-white border-b border-[var(--gray)] px-4 py-3 flex gap-4 flex-shrink-0">
            <select
              value={metadata.source || ''}
              onChange={e => setMetadata(m => ({ ...m, source: e.target.value as Source }))}
              className="px-3 py-1.5 border border-[var(--gray)] rounded-lg text-sm"
            >
              <option value="WildChat">WildChat</option>
              <option value="ChatbotArena">Chatbot Arena</option>
              <option value="OASST">OASST</option>
              <option value="Custom">Custom</option>
            </select>
            <select
              value={metadata.domain || ''}
              onChange={e => setMetadata(m => ({ ...m, domain: e.target.value as Domain }))}
              className="px-3 py-1.5 border border-[var(--gray)] rounded-lg text-sm"
            >
              <option value="career">Career</option>
              <option value="travel">Travel</option>
              <option value="code">Code</option>
              <option value="education">Education</option>
              <option value="creative">Creative</option>
              <option value="general">General</option>
              <option value="other">Other</option>
            </select>
            <select
              value={metadata.taskComplexity || ''}
              onChange={e => setMetadata(m => ({ ...m, taskComplexity: e.target.value as TaskComplexity }))}
              className="px-3 py-1.5 border border-[var(--gray)] rounded-lg text-sm"
            >
              <option value="single-goal">Single Goal</option>
              <option value="multi-goal">Multi Goal</option>
              <option value="exploratory">Exploratory</option>
            </select>
          </div>

          {/* Turn Navigator */}
          <div className="bg-[var(--bg-subtle)] border-b border-[var(--gray)] px-4 py-2 flex items-center gap-2 flex-shrink-0">
            <button
              onClick={() => setCurrentTurnIndex(Math.max(0, currentTurnIndex - 1))}
              disabled={currentTurnIndex === 0}
              className="p-1 rounded hover:bg-white disabled:opacity-30"
            >
              <span className="material-symbols-rounded">chevron_left</span>
            </button>
            <div className="flex gap-1">
              {turnAnnotations.map((t, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentTurnIndex(i)}
                  className={`w-8 h-8 rounded-full text-xs font-medium transition-all ${
                    i === currentTurnIndex
                      ? 'bg-[var(--yellow)] text-[var(--black)]'
                      : t.speaker === 'user'
                      ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  } ${t.constraintViolated ? 'ring-2 ring-[var(--orange)]' : ''} ${
                    t.constraintStated ? 'ring-2 ring-[var(--green)]' : ''
                  }`}
                >
                  {t.turnNumber}
                </button>
              ))}
            </div>
            <button
              onClick={() => setCurrentTurnIndex(Math.min(turnAnnotations.length - 1, currentTurnIndex + 1))}
              disabled={currentTurnIndex >= turnAnnotations.length - 1}
              className="p-1 rounded hover:bg-white disabled:opacity-30"
            >
              <span className="material-symbols-rounded">chevron_right</span>
            </button>
            <span className="ml-4 text-sm text-[var(--text-dim)]">
              Turn {currentTurnIndex + 1} of {turnAnnotations.length}
            </span>
          </div>

          {/* Current Turn Content */}
          {currentTurn && (
            <div className="flex-1 overflow-y-auto p-4">
              <div className={`p-4 rounded-2xl mb-4 ${
                currentTurn.speaker === 'user'
                  ? 'bg-blue-50 border border-blue-200'
                  : 'bg-white border border-[var(--gray)]'
              }`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    currentTurn.speaker === 'user'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {currentTurn.speaker === 'user' ? 'User' : 'Assistant'}
                  </span>
                  <span className="text-xs text-[var(--text-dim)]">Turn {currentTurn.turnNumber}</span>
                </div>
                <p className="text-[var(--text)] whitespace-pre-wrap">{currentTurn.content}</p>
              </div>

              {/* Turn Annotation Controls */}
              <div className="space-y-4">
                {/* Constraint Events */}
                <div className="bg-white rounded-xl p-4 border border-[var(--gray)]">
                  <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                    <span className="material-symbols-rounded text-[var(--green)]">bookmark</span>
                    Constraint Events
                  </h3>
                  <div className="space-y-3">
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={currentTurn.constraintStated}
                        onChange={e => updateTurn('constraintStated', e.target.checked)}
                        className="w-4 h-4 rounded"
                      />
                      <span className="text-sm">Constraint Stated</span>
                    </label>
                    {currentTurn.constraintStated && (
                      <>
                        <select
                          value={currentTurn.constraintType || ''}
                          onChange={e => updateTurn('constraintType', e.target.value as ConstraintType)}
                          className="w-full px-3 py-2 border border-[var(--gray)] rounded-lg text-sm"
                        >
                          <option value="">Select type...</option>
                          <option value="goal">Goal</option>
                          <option value="hard">Hard Constraint</option>
                          <option value="soft">Soft Constraint</option>
                          <option value="preference">Preference</option>
                        </select>
                        <textarea
                          value={currentTurn.constraintText || ''}
                          onChange={e => updateTurn('constraintText', e.target.value)}
                          placeholder="Constraint text (verbatim)"
                          className="w-full px-3 py-2 border border-[var(--gray)] rounded-lg text-sm h-20"
                        />
                        <button
                          onClick={addConstraint}
                          disabled={!currentTurn.constraintText || !currentTurn.constraintType}
                          className="px-4 py-2 bg-[var(--green)] text-white rounded-lg text-sm font-medium disabled:opacity-50"
                        >
                          Add to Tracked Constraints
                        </button>
                      </>
                    )}
                  </div>
                </div>

                {/* Violation Events (for assistant turns) */}
                {currentTurn.speaker === 'assistant' && constraints.length > 0 && (
                  <div className="bg-white rounded-xl p-4 border border-[var(--gray)]">
                    <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                      <span className="material-symbols-rounded text-[var(--orange)]">warning</span>
                      Violation Events
                    </h3>
                    <div className="space-y-2">
                      {constraints.filter(c => !c.violatedAtTurn).map(c => (
                        <div key={c.id} className="flex items-center justify-between p-2 bg-[var(--bg-subtle)] rounded-lg">
                          <span className="text-sm truncate flex-1">{c.text}</span>
                          <button
                            onClick={() => markViolated(c.id)}
                            className="px-3 py-1 bg-[var(--orange)] text-white rounded-full text-xs"
                          >
                            Mark Violated
                          </button>
                        </div>
                      ))}
                    </div>
                    {currentTurn.constraintViolated && (
                      <select
                        value={currentTurn.violationType || ''}
                        onChange={e => updateTurn('violationType', e.target.value as ViolationType)}
                        className="w-full mt-3 px-3 py-2 border border-[var(--gray)] rounded-lg text-sm"
                      >
                        <option value="">Violation type...</option>
                        <option value="direct">Direct (explicit contradiction)</option>
                        <option value="drift">Drift (gradual scope expansion)</option>
                        <option value="implicit">Implicit (ignores without contradicting)</option>
                      </select>
                    )}
                  </div>
                )}

                {/* Repair Events (for user turns after violations) */}
                {currentTurn.speaker === 'user' && constraints.some(c => c.violatedAtTurn) && (
                  <div className="bg-white rounded-xl p-4 border border-[var(--gray)]">
                    <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                      <span className="material-symbols-rounded text-blue-500">build</span>
                      Repair Events
                    </h3>
                    <div className="space-y-3">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={currentTurn.repairAttempted}
                          onChange={e => updateTurn('repairAttempted', e.target.checked)}
                          className="w-4 h-4 rounded"
                        />
                        <span className="text-sm">Repair Attempted</span>
                      </label>
                      {currentTurn.repairAttempted && (
                        <>
                          <select
                            value={currentTurn.repairType || ''}
                            onChange={e => updateTurn('repairType', e.target.value as RepairType)}
                            className="w-full px-3 py-2 border border-[var(--gray)] rounded-lg text-sm"
                          >
                            <option value="">Repair type...</option>
                            <option value="restatement">Restatement (re-types constraint)</option>
                            <option value="reference">Reference (points to prior message)</option>
                            <option value="redirect">Redirect (indirect correction)</option>
                            <option value="abandon">Abandon (accepts violation)</option>
                          </select>
                          <div className="flex gap-4">
                            <label className="flex items-center gap-2">
                              <input
                                type="radio"
                                name="repairSuccess"
                                checked={currentTurn.repairSuccess === true}
                                onChange={() => updateTurn('repairSuccess', true)}
                              />
                              <span className="text-sm">Success</span>
                            </label>
                            <label className="flex items-center gap-2">
                              <input
                                type="radio"
                                name="repairSuccess"
                                checked={currentTurn.repairSuccess === false}
                                onChange={() => updateTurn('repairSuccess', false)}
                              />
                              <span className="text-sm">Failed</span>
                            </label>
                          </div>
                          {currentTurn.repairType === 'restatement' && (
                            <div className="mt-3 pt-3 border-t border-[var(--gray)]">
                              <p className="text-xs text-[var(--text-dim)] mb-2">Which constraint is being restated?</p>
                              <div className="space-y-1">
                                {constraints.map(c => (
                                  <button
                                    key={c.id}
                                    onClick={() => markRestatement(c.id)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
                                      c.restatementTurns.includes(currentTurn.turnNumber)
                                        ? 'bg-orange-100 border border-orange-300'
                                        : 'bg-[var(--bg-subtle)] hover:bg-orange-50'
                                    }`}
                                  >
                                    {c.text}
                                  </button>
                                ))}
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                )}

                {/* Agency Markers (for user turns) */}
                {currentTurn.speaker === 'user' && (
                  <div className="bg-white rounded-xl p-4 border border-[var(--gray)]">
                    <h3 className="font-bold text-sm mb-3 flex items-center gap-2">
                      <span className="material-symbols-rounded text-purple-500">psychology</span>
                      Agency Markers
                    </h3>
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm text-[var(--text-dim)] mb-1 block">Specificity (1-5)</label>
                        <div className="flex gap-2">
                          {[1, 2, 3, 4, 5].map(n => (
                            <button
                              key={n}
                              onClick={() => updateTurn('userSpecificity', n)}
                              className={`w-10 h-10 rounded-lg font-medium ${
                                currentTurn.userSpecificity === n
                                  ? 'bg-purple-500 text-white'
                                  : 'bg-[var(--bg-subtle)] hover:bg-purple-100'
                              }`}
                            >
                              {n}
                            </button>
                          ))}
                        </div>
                        <div className="flex justify-between text-xs text-[var(--text-dim)] mt-1">
                          <span>Vague</span>
                          <span>Highly Specific</span>
                        </div>
                      </div>
                      <div>
                        <label className="text-sm text-[var(--text-dim)] mb-1 block">User Stance</label>
                        <div className="flex gap-2 flex-wrap">
                          {(['directive', 'collaborative', 'passive', 'reactive'] as UserStance[]).map(stance => (
                            <button
                              key={stance}
                              onClick={() => updateTurn('userStance', stance)}
                              className={`px-3 py-1.5 rounded-full text-sm capitalize ${
                                currentTurn.userStance === stance
                                  ? 'bg-purple-500 text-white'
                                  : 'bg-[var(--bg-subtle)] hover:bg-purple-100'
                              }`}
                            >
                              {stance}
                            </button>
                          ))}
                        </div>
                      </div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={currentTurn.passiveAcceptance}
                          onChange={e => updateTurn('passiveAcceptance', e.target.checked)}
                          className="w-4 h-4 rounded"
                        />
                        <span className="text-sm">Passive Acceptance ("ok", "sure", "thanks")</span>
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel: Metrics + Constraints */}
        <div className="w-96 bg-white flex flex-col overflow-hidden">
          {/* Tracked Constraints */}
          <div className="border-b border-[var(--gray)] p-4 flex-shrink-0">
            <h2 className="font-bold mb-3 flex items-center gap-2">
              <span className="material-symbols-rounded text-[var(--yellow)]">inventory_2</span>
              Tracked Constraints ({constraints.length})
            </h2>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {constraints.map(c => (
                <div
                  key={c.id}
                  className={`p-2 rounded-lg text-sm ${
                    c.violatedAtTurn
                      ? 'bg-red-50 border border-red-200'
                      : 'bg-[var(--bg-subtle)]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-xs ${
                      c.type === 'goal' ? 'bg-green-100 text-green-700' :
                      c.type === 'hard' ? 'bg-yellow-100 text-yellow-700' :
                      c.type === 'soft' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {c.type}
                    </span>
                    {c.violatedAtTurn && (
                      <span className="text-xs text-red-600">⚠ T{c.violatedAtTurn}</span>
                    )}
                    {c.restatementTurns.length > 0 && (
                      <span className="text-xs text-orange-600">↻ {c.restatementTurns.length}x</span>
                    )}
                  </div>
                  <p className="text-[var(--text)] mt-1 truncate">{c.text}</p>
                  <span className="text-xs text-[var(--text-dim)]">Stated T{c.statedAtTurn}</span>
                </div>
              ))}
              {constraints.length === 0 && (
                <p className="text-sm text-[var(--text-dim)]">No constraints tracked yet</p>
              )}
            </div>
          </div>

          {/* Trajectory Metrics */}
          {trajectory && (
            <div className="border-b border-[var(--gray)] p-4 flex-shrink-0">
              <h2 className="font-bold mb-3 flex items-center gap-2">
                <span className="material-symbols-rounded text-blue-500">analytics</span>
                Trajectory Metrics
              </h2>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-[var(--bg-subtle)] p-2 rounded-lg">
                  <span className="text-xs text-[var(--text-dim)]">Specificity Δ</span>
                  <p className={`font-bold ${trajectory.specificityDelta < 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {trajectory.specificityDelta.toFixed(2)}
                  </p>
                </div>
                <div className="bg-[var(--bg-subtle)] p-2 rounded-lg">
                  <span className="text-xs text-[var(--text-dim)]">Half-Life</span>
                  <p className="font-bold">
                    {trajectory.constraintHalfLife?.toFixed(1) || '—'} turns
                  </p>
                </div>
                <div className="bg-[var(--bg-subtle)] p-2 rounded-lg">
                  <span className="text-xs text-[var(--text-dim)]">Restatements</span>
                  <p className="font-bold">{trajectory.restatementCount}</p>
                </div>
                <div className="bg-[var(--bg-subtle)] p-2 rounded-lg">
                  <span className="text-xs text-[var(--text-dim)]">Repair Efficiency</span>
                  <p className="font-bold">{(trajectory.repairEfficiency * 100).toFixed(0)}%</p>
                </div>
                <div className="col-span-2 bg-purple-50 p-3 rounded-lg border border-purple-200">
                  <span className="text-xs text-purple-600">Agency Collapse Index</span>
                  <p className={`font-bold text-xl ${
                    trajectory.agencyCollapseIndex > 4 ? 'text-red-600' :
                    trajectory.agencyCollapseIndex > 2 ? 'text-orange-600' :
                    'text-green-600'
                  }`}>
                    {trajectory.agencyCollapseIndex.toFixed(2)}
                  </p>
                  <span className="text-xs text-[var(--text-dim)]">
                    {trajectory.agencyCollapseIndex > 4 ? 'Severe Collapse' :
                     trajectory.agencyCollapseIndex > 2 ? 'Moderate Collapse' :
                     'Stable'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Archetype */}
          {archetypeResult && (
            <div className="border-b border-[var(--gray)] p-4 flex-shrink-0">
              <h2 className="font-bold mb-3 flex items-center gap-2">
                <span className="material-symbols-rounded text-orange-500">category</span>
                Archetype
              </h2>
              <div className="space-y-2">
                <div className={`p-3 rounded-lg ${
                  archetypeResult.archetype === 'Provider Trap' ? 'bg-red-50 border border-red-200' :
                  archetypeResult.archetype === 'Hallucination Loop' ? 'bg-orange-50 border border-orange-200' :
                  archetypeResult.archetype === 'Identity Shift' ? 'bg-yellow-50 border border-yellow-200' :
                  archetypeResult.archetype === 'Canvas Hack' ? 'bg-blue-50 border border-blue-200' :
                  archetypeResult.archetype === 'Passive Default' ? 'bg-gray-50 border border-gray-200' :
                  'bg-[var(--bg-subtle)]'
                }`}>
                  <p className="font-bold">{manualArchetype || archetypeResult.archetype}</p>
                  <p className="text-xs text-[var(--text-dim)]">
                    {manualArchetype ? 'Manual override' : `Auto-detected (${archetypeResult.confidence})`}
                  </p>
                </div>
                <select
                  value={manualArchetype || ''}
                  onChange={e => setManualArchetype(e.target.value as Archetype || null)}
                  className="w-full px-3 py-2 border border-[var(--gray)] rounded-lg text-sm"
                >
                  <option value="">Use auto-detection</option>
                  <option value="Provider Trap">Provider Trap</option>
                  <option value="Hallucination Loop">Hallucination Loop</option>
                  <option value="Identity Shift">Identity Shift</option>
                  <option value="Canvas Hack">Canvas Hack</option>
                  <option value="Passive Default">Passive Default</option>
                  <option value="Mixed/Other">Mixed/Other</option>
                </select>
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="flex-1 p-4 overflow-hidden flex flex-col">
            <h2 className="font-bold mb-3 flex items-center gap-2">
              <span className="material-symbols-rounded text-[var(--text-dim)]">notes</span>
              Notes
            </h2>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Annotator notes..."
              className="flex-1 w-full px-3 py-2 border border-[var(--gray)] rounded-lg text-sm resize-none"
            />
          </div>

          {/* Data Input */}
          <div className="border-t border-[var(--gray)] p-4 flex-shrink-0">
            <details>
              <summary className="cursor-pointer text-sm text-[var(--text-dim)]">
                Load JSON Data
              </summary>
              <textarea
                onChange={handleLoadData}
                placeholder='{"id": "...", "messages": [...]}'
                className="mt-2 w-full h-24 px-3 py-2 border border-[var(--gray)] rounded-lg text-xs font-mono resize-none"
              />
            </details>
          </div>
        </div>
      </main>
    </div>
  );
}
