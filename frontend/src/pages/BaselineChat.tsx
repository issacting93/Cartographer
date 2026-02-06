/**
 * BaselineChat.tsx - CUI 2026 Condition A
 * 
 * Chat-only interface. Constraints are mentioned once at start
 * and then scroll away. User must type repairs from memory.
 * 
 * BLOOM Design System
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChatInterface } from '../components/ChatInterface';
import { INITIAL_CONSTRAINTS, SCENARIO_NAME, getScriptedResponse } from '../scenario';
import type { ChatMessage, StudyMetrics } from '../types';

export default function BaselineChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [turnNumber, setTurnNumber] = useState(0);
  const [violationOccurred, setViolationOccurred] = useState(false);
  const [repairStartTime, setRepairStartTime] = useState<number | null>(null);
  const [repairTime, setRepairTime] = useState<number | null>(null);

  const [metrics, setMetrics] = useState<StudyMetrics>({
    condition: 'baseline',
    userId: `baseline-${Date.now()}`,
    startTime: new Date(),
    constraintRestatements: 0,
    constraintViolationsDetected: 0,
    repairTurns: 0,
    totalTurns: 0,
    pinActions: 0,
    contextLensQueries: 0,
    taskSwitches: 0
  });

  // Add initial messages
  useEffect(() => {
    const initialMessages: ChatMessage[] = [
      {
        id: 'system-1',
        role: 'system',
        content: `Starting: ${SCENARIO_NAME}`,
        timestamp: new Date()
      }
    ];

    const constraintIntro: ChatMessage = {
      id: 'assistant-0',
      role: 'assistant',
      content: `Welcome! I understand you're looking for career coaching. Before we begin, I see you have the following requirements:

**Your Constraints:**
${INITIAL_CONSTRAINTS.map(c => `• **${c.type}**: ${c.label}`).join('\n')}

I'll keep these in mind throughout our conversation. Let's get started - what aspects of your career transition would you like to focus on first?`,
      timestamp: new Date(),
      turnNumber: 0
    };

    setMessages([...initialMessages, constraintIntro]);
  }, []);

  // Timer effect for repair measurement
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (repairStartTime && !repairTime) {
      interval = setInterval(() => {
        // Force re-render to update timer display
        setMetrics(m => ({ ...m }));
      }, 100);
    }
    return () => clearInterval(interval);
  }, [repairStartTime, repairTime]);

  const handleSendMessage = (content: string) => {
    const newTurn = turnNumber + 1;
    setTurnNumber(newTurn);

    // If violation occurred and this is the first response, measure repair time
    if (violationOccurred && repairStartTime && !repairTime) {
      const elapsed = (Date.now() - repairStartTime) / 1000;
      setRepairTime(elapsed);
      setMetrics(m => ({ ...m, repairTurns: m.repairTurns + 1 }));
    }

    // Check for constraint restatements
    const lowerContent = content.toLowerCase();
    const isRestatement =
      lowerContent.includes('remote') ||
      lowerContent.includes('work-life') ||
      lowerContent.includes('balance') ||
      lowerContent.includes('45 hour') ||
      lowerContent.includes('no on-call') ||
      lowerContent.includes('i said') ||
      lowerContent.includes('i mentioned') ||
      lowerContent.includes('remember');

    if (isRestatement) {
      setMetrics(m => ({ ...m, constraintRestatements: m.constraintRestatements + 1 }));
    }

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${newTurn}`,
      role: 'user',
      content,
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

        // Turn 8: Start repair timer
        if (scriptedResponse.violatesConstraint) {
          setViolationOccurred(true);
          setRepairStartTime(Date.now());
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
          content: "Thank you for sharing. What else would you like to explore?",
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
            <h1 className="text-white font-bold">Condition A: Baseline</h1>
            <p className="text-[var(--gray-dark)] text-xs">Chat-only interface (no external state)</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs bg-white bg-opacity-10 text-white px-3 py-1 rounded-full">
            Turn {turnNumber}
          </span>
          {metrics.constraintRestatements > 0 && (
            <span className="text-xs bg-[var(--orange)] bg-opacity-20 text-[var(--orange)] px-3 py-1 rounded-full">
              Restatements: {metrics.constraintRestatements}
            </span>
          )}
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

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-3xl mx-auto w-full p-6 overflow-hidden">
        {/* Violation Alert */}
        {violationOccurred && !repairTime && (
          <div className="mb-4 p-4 bg-[var(--orange)] bg-opacity-10 border border-[var(--orange)] rounded-2xl animate-in slide-in-from-top">
            <div className="flex items-start gap-3">
              <span className="material-symbols-rounded text-[var(--orange)]">warning</span>
              <div>
                <h3 className="font-bold text-[var(--text)]">Constraint Violation Detected</h3>
                <p className="text-sm text-[var(--text-dim)] mt-1">
                  The AI's suggestion violates your stated constraints.
                  How will you correct it? Timer is running...
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
                  ({metrics.constraintRestatements} restatements used)
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Chat Interface */}
        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isTyping={isTyping}
          className="flex-1"
        />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-[var(--gray)] px-6 py-3 flex justify-between text-xs text-[var(--text-dim)]">
        <span>Baseline: Constraints exist only in conversation history</span>
        <span>If the AI forgets constraints, you must re-state them manually</span>
      </footer>
    </div>
  );
}
