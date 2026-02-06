/**
 * TreatmentChat.tsx - CUI 2026 Condition B
 * 
 * Chat + Context Inventory Interface.
 * Constraints are always visible in sidebar.
 * User can click constraints to reference them in repair.
 * 
 * BLOOM Design System
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChatInterface } from '../components/ChatInterface';
import { ConstraintSidebar, ConstraintItem } from '../components/ConstraintSidebar';
import { INITIAL_CONSTRAINTS, SCENARIO_NAME, getScriptedResponse } from '../scenario';
import type { ChatMessage, StudyMetrics } from '../types';

export default function TreatmentChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [turnNumber, setTurnNumber] = useState(0);
  const [violationOccurred, setViolationOccurred] = useState(false);
  const [violatedIds, setViolatedIds] = useState<string[]>([]);
  const [repairStartTime, setRepairStartTime] = useState<number | null>(null);
  const [repairTime, setRepairTime] = useState<number | null>(null);
  const [pendingReference, setPendingReference] = useState<string | null>(null);

  const [metrics, setMetrics] = useState<StudyMetrics>({
    condition: 'treatment',
    userId: `treatment-${Date.now()}`,
    startTime: new Date(),
    constraintRestatements: 0,
    constraintViolationsDetected: 0,
    repairTurns: 0,
    totalTurns: 0,
    pinActions: 0,
    contextLensQueries: 0,
    taskSwitches: 0
  });

  // Convert scenario constraints to sidebar format
  const sidebarConstraints: ConstraintItem[] = INITIAL_CONSTRAINTS.map(c => ({
    id: c.id,
    type: c.type as 'Goal' | 'Constraint' | 'Preference',
    label: c.label,
    description: c.description
  }));

  // Add initial messages
  useEffect(() => {
    const initialMessages: ChatMessage[] = [
      {
        id: 'system-1',
        role: 'system',
        content: `Starting: ${SCENARIO_NAME}`,
        timestamp: new Date()
      },
      {
        id: 'system-2',
        role: 'system',
        content: 'Your constraints are visible in the Context Inventory →',
        timestamp: new Date()
      }
    ];

    const welcomeMessage: ChatMessage = {
      id: 'assistant-0',
      role: 'assistant',
      content: `Welcome! I'm your AI career coach.

I can see your requirements in the **Context Inventory** on the right:

${INITIAL_CONSTRAINTS.map(c => `• **${c.type}**: ${c.label}`).join('\n')}

These stay visible throughout our conversation. If I ever suggest something that violates your constraints, you can click them to reference.

What would you like to focus on first?`,
      timestamp: new Date(),
      turnNumber: 0
    };

    setMessages([...initialMessages, welcomeMessage]);
  }, []);

  // Timer effect
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (repairStartTime && !repairTime) {
      interval = setInterval(() => {
        setMetrics(m => ({ ...m }));
      }, 100);
    }
    return () => clearInterval(interval);
  }, [repairStartTime, repairTime]);

  const handleConstraintClick = (constraint: ConstraintItem) => {
    // Insert reference to constraint
    setPendingReference(`[Referencing: ${constraint.type} - ${constraint.label}]`);
    setMetrics(m => ({ ...m, pinActions: m.pinActions + 1 }));
  };

  const handleSendMessage = (content: string) => {
    const newTurn = turnNumber + 1;
    setTurnNumber(newTurn);

    // Include pending reference if any
    const fullContent = pendingReference
      ? `${content}\n\n${pendingReference}`
      : content;
    setPendingReference(null);

    // If violation occurred and this is first response, measure repair time
    if (violationOccurred && repairStartTime && !repairTime) {
      const elapsed = (Date.now() - repairStartTime) / 1000;
      setRepairTime(elapsed);
      setMetrics(m => ({ ...m, repairTurns: m.repairTurns + 1 }));
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${newTurn}`,
      role: 'user',
      content: fullContent,
      timestamp: new Date(),
      turnNumber: newTurn
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Get scripted response
    setTimeout(() => {
      const scriptedResponse = getScriptedResponse(newTurn);

      if (scriptedResponse) {
        const assistantMessage: ChatMessage = {
          id: `assistant-${newTurn}`,
          role: 'assistant',
          content: scriptedResponse.response,
          timestamp: new Date(),
          turnNumber: newTurn,
          violatesConstraint: !!scriptedResponse.violatesConstraint
        };

        // Turn 8: Start repair timer and highlight violated constraints
        if (scriptedResponse.violatesConstraint) {
          setViolationOccurred(true);
          setRepairStartTime(Date.now());
          // OpenScale violates: work-life balance (constraint-1) and remote (constraint-2)
          setViolatedIds(['constraint-1', 'constraint-2']);
          setMetrics(m => ({
            ...m,
            constraintViolationsDetected: m.constraintViolationsDetected + 1,
            turnAtViolation: newTurn
          }));
        }

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const genericResponse: ChatMessage = {
          id: `assistant-${newTurn}`,
          role: 'assistant',
          content: "I'll keep your constraints in mind. What else would you like to explore?",
          timestamp: new Date(),
          turnNumber: newTurn
        };
        setMessages(prev => [...prev, genericResponse]);
      }

      setMetrics(m => ({ ...m, totalTurns: newTurn }));
      setIsTyping(false);
    }, 1500);
  };

  const currentRepairTime = repairStartTime && !repairTime
    ? ((Date.now() - repairStartTime) / 1000).toFixed(1)
    : repairTime?.toFixed(1);

  return (
    <div className="h-screen flex flex-col bg-[var(--bg-subtle)]">
      {/* Header */}
      <header className="bg-[var(--black)] px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <Link to="/" className="text-[var(--gray-dark)] hover:text-white transition-colors">
            <span className="material-symbols-rounded">arrow_back</span>
          </Link>
          <div>
            <h1 className="text-white font-bold">Condition B: Context Inventory</h1>
            <p className="text-[var(--gray-dark)] text-xs">Chat + persistent constraint sidebar</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs bg-white bg-opacity-10 text-white px-3 py-1 rounded-full">
            Turn {turnNumber}
          </span>
          <span className="text-xs bg-[var(--green)] bg-opacity-20 text-[var(--green)] px-3 py-1 rounded-full flex items-center gap-1">
            <span className="material-symbols-rounded text-sm">visibility</span>
            Context Visible
          </span>
          {violationOccurred && (
            <span className={`text-xs px-3 py-1 rounded-full flex items-center gap-2 ${repairTime
              ? 'bg-[var(--green)] bg-opacity-20 text-[var(--green)]'
              : 'bg-[var(--orange)] text-white animate-pulse'
              }`}>
              <span className="material-symbols-rounded text-sm">timer</span>
              {currentRepairTime}s
            </span>
          )}
        </div>
      </header>

      {/* Main Content - Two Column Layout */}
      <main className="flex-1 flex gap-6 p-6 overflow-hidden">
        {/* Left: Chat */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Violation Alert */}
          {violationOccurred && !repairTime && (
            <div className="mb-4 p-4 bg-[var(--orange)] bg-opacity-10 border border-[var(--orange)] rounded-2xl">
              <div className="flex items-start gap-3">
                <span className="material-symbols-rounded text-[var(--orange)]">warning</span>
                <div className="flex-1">
                  <h3 className="font-bold text-[var(--text)]">Constraint Violation Detected</h3>
                  <p className="text-sm text-[var(--text-dim)] mt-1">
                    Click a constraint in the sidebar to reference it, then send your correction.
                  </p>
                </div>
              </div>
            </div>
          )}

          {repairTime && (
            <div className="mb-4 p-4 bg-[var(--green)] bg-opacity-10 border border-[var(--green)] rounded-2xl">
              <div className="flex items-center gap-3">
                <span className="material-symbols-rounded text-[var(--green)]">check_circle</span>
                <div>
                  <span className="font-bold text-[var(--text)]">Repair completed in {repairTime.toFixed(1)}s</span>
                  <span className="text-sm text-[var(--text-dim)] ml-2">
                    ({metrics.pinActions} click references used)
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Pending Reference */}
          {pendingReference && (
            <div className="mb-4 p-3 bg-[var(--yellow)] bg-opacity-20 border border-[var(--yellow)] rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="material-symbols-rounded text-[var(--yellow)]">link</span>
                <span className="text-sm font-medium">{pendingReference}</span>
              </div>
              <button
                onClick={() => setPendingReference(null)}
                className="text-[var(--text-dim)] hover:text-[var(--text)]"
              >
                <span className="material-symbols-rounded text-sm">close</span>
              </button>
            </div>
          )}

          {/* Chat Interface */}
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isTyping={isTyping}
            className="flex-1"
          />
        </div>

        {/* Right: Constraint Sidebar */}
        <div className="w-80 flex-shrink-0">
          <ConstraintSidebar
            constraints={sidebarConstraints}
            onConstraintClick={handleConstraintClick}
            violatedIds={violatedIds}
            className="h-full"
          />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-[var(--gray)] px-6 py-3 flex justify-between text-xs text-[var(--text-dim)]">
        <span>Treatment: Constraints always visible in Context Inventory</span>
        <div className="flex gap-4">
          <span>Click References: <strong className="text-[var(--text)]">{metrics.pinActions}</strong></span>
          <span>Violations: <strong className="text-[var(--orange)]">{metrics.constraintViolationsDetected}</strong></span>
        </div>
      </footer>
    </div>
  );
}
