import { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import type { ChatMessage } from '../types';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isTyping: boolean;
  showConstraintReminder?: boolean;
  constraints?: { label: string }[];
  className?: string;
}

export function ChatInterface({
  messages,
  onSendMessage,
  isTyping,
  showConstraintReminder = false,
  constraints = [],
  className
}: ChatInterfaceProps) {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = () => {
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText('');
  };

  return (
    <div className={clsx("flex flex-col bg-[var(--bg)] rounded-2xl border border-[var(--gray)] shadow-lg overflow-hidden", className)}>
      {/* Chat Header */}
      <div className="bg-[var(--black)] px-5 py-4">
        <div className="flex items-center gap-3">
          <span className="material-symbols-rounded text-[var(--yellow)]">smart_toy</span>
          <h2 className="text-white font-bold text-lg">AI Career Coach</h2>
        </div>
        <p className="text-[var(--gray-dark)] text-xs mt-1">
          Your personal career planning assistant
        </p>
      </div>

      {/* Constraint Reminder (Baseline only) */}
      {showConstraintReminder && constraints.length > 0 && (
        <div className="px-5 py-3 bg-[var(--yellow)] bg-opacity-10 border-b border-[var(--yellow)]">
          <div className="flex items-start gap-2 text-xs text-[var(--black)]">
            <span className="material-symbols-rounded text-sm">info</span>
            <div>
              <span className="font-semibold">Remember your constraints:</span>
              <span className="ml-1">{constraints.map(c => c.label).join(' • ')}</span>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 min-h-[400px] bg-[var(--bg-subtle)]">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={clsx(
              "flex gap-3",
              msg.role === 'user' ? "flex-row-reverse" : "",
              msg.role === 'system' ? "justify-center" : ""
            )}
          >
            {msg.role === 'system' ? (
              <div className="pill pill-outline text-xs">
                {msg.content}
              </div>
            ) : (
              <>
                <div className={clsx(
                  "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0",
                  msg.role === 'user'
                    ? "bg-[var(--yellow)]"
                    : "bg-[var(--black)]"
                )}>
                  <span className={clsx(
                    "material-symbols-rounded text-xl",
                    msg.role === 'user' ? "text-[var(--black)]" : "text-white"
                  )}>
                    {msg.role === 'user' ? 'person' : 'smart_toy'}
                  </span>
                </div>
                <div className={clsx(
                  "max-w-[75%] p-4 rounded-2xl text-sm",
                  msg.role === 'user'
                    ? "bg-[var(--black)] text-white"
                    : "bg-white text-[var(--text)] border border-[var(--gray)]",
                  msg.violatesConstraint && "ring-2 ring-[var(--orange)] bg-red-50"
                )}>
                  {msg.violatesConstraint && (
                    <div className="flex items-center gap-2 text-[var(--orange)] text-xs mb-2 font-semibold">
                      <span className="material-symbols-rounded text-sm">warning</span>
                      This response may violate your constraints
                    </div>
                  )}
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  <div className={clsx(
                    "text-xs mt-3",
                    msg.role === 'user' ? "text-[var(--gray-dark)]" : "text-[var(--text-dim)]"
                  )}>
                    {msg.timestamp.toLocaleTimeString()}
                    {msg.turnNumber && ` • Turn ${msg.turnNumber}`}
                  </div>
                </div>
              </>
            )}
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-3">
            <div className="w-10 h-10 rounded-full bg-[var(--black)] flex items-center justify-center">
              <span className="material-symbols-rounded text-white text-xl">smart_toy</span>
            </div>
            <div className="bg-white p-4 rounded-2xl border border-[var(--gray)]">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-[var(--gray-dark)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-[var(--gray-dark)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-[var(--gray-dark)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-[var(--gray)] p-4 bg-white">
        <div className="flex gap-3">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSubmit()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border border-[var(--gray)] rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-[var(--yellow)]"
          />
          <button
            onClick={handleSubmit}
            disabled={!inputText.trim()}
            className="btn btn-primary"
          >
            <span className="material-symbols-rounded">send</span>
          </button>
        </div>
      </div>
    </div>
  );
}
