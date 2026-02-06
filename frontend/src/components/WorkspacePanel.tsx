/**
 * WorkspacePanel.tsx - BLOOM Design System
 * 
 * Center panel: Chat or Canvas mode with drop zones
 * and text selection for saving to context.
 */

import { useState, useRef } from 'react';
import { useWorkspace, ContextItem } from './ThreePanelLayout';
import { HexWorkspace, WorkspaceNode } from './HexWorkspace';

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    attachedContext?: ContextItem[];
    timestamp: Date;
}

export function WorkspacePanel() {
    const {
        mode,
        attachedContext,
        clearAttached,
        attachContext,
        setSelection
    } = useWorkspace();

    // Chat state
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: 'welcome',
            role: 'assistant',
            content: "Welcome! I'm your AI assistant. You can drag context items from the left panel to attach them to your messages. Select any text to save it as new context.",
            timestamp: new Date(),
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    // Canvas state
    const [hexSlots, setHexSlots] = useState<(WorkspaceNode | null)[]>([null, null, null, null, null, null]);
    const [hexSelection, setHexSelection] = useState<number[]>([]);

    // Drop handlers
    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        try {
            const data = e.dataTransfer.getData('application/json');
            const item: ContextItem = JSON.parse(data);
            attachContext(item);
        } catch (err) {
            console.error('Drop failed:', err);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    };

    // Text selection
    const handleTextSelect = () => {
        const selection = window.getSelection();
        if (selection && selection.toString().trim()) {
            setSelection({
                type: 'text',
                content: selection.toString().trim(),
            });
        }
    };

    // Send message
    const handleSend = () => {
        if (!inputValue.trim()) return;

        const userMessage: ChatMessage = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: inputValue,
            attachedContext: attachedContext.length > 0 ? [...attachedContext] : undefined,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        clearAttached();
        setIsTyping(true);

        // Simulated response
        setTimeout(() => {
            const response: ChatMessage = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: `I've noted your message${userMessage.attachedContext ? ` with ${userMessage.attachedContext.length} context item(s) attached` : ''}. How can I help further?`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, response]);
            setIsTyping(false);
        }, 1000);
    };

    // Render Chat Mode
    const renderChatMode = () => (
        <div
            className="flex-1 flex flex-col"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
        >
            {/* Messages */}
            <div
                className="flex-1 overflow-y-auto p-6 space-y-4"
                onMouseUp={handleTextSelect}
            >
                {messages.map(msg => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[80%] ${msg.role === 'system' ? 'w-full' : ''}`}>
                            {msg.role === 'system' ? (
                                <div className="text-center text-xs text-[var(--text-dim)] py-2">
                                    {msg.content}
                                </div>
                            ) : (
                                <div className={`rounded-2xl px-4 py-3 ${msg.role === 'user'
                                        ? 'bg-[var(--black)] text-white rounded-br-md'
                                        : 'bg-white border border-[var(--gray)] rounded-bl-md'
                                    }`}>
                                    {/* Attached context badges */}
                                    {msg.attachedContext && msg.attachedContext.length > 0 && (
                                        <div className="flex flex-wrap gap-1 mb-2">
                                            {msg.attachedContext.map(ctx => (
                                                <span
                                                    key={ctx.id}
                                                    className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-[var(--yellow)] bg-opacity-20 text-[var(--yellow)]"
                                                >
                                                    <span className="material-symbols-rounded text-xs">{ctx.icon}</span>
                                                    {ctx.label}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                    <p className="text-sm">{msg.content}</p>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isTyping && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-[var(--gray)] rounded-2xl rounded-bl-md px-4 py-3">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-[var(--gray-dark)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                <span className="w-2 h-2 bg-[var(--gray-dark)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                <span className="w-2 h-2 bg-[var(--gray-dark)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Attached Context Preview */}
            {attachedContext.length > 0 && (
                <div className="px-6 py-2 bg-[var(--yellow)] bg-opacity-10 border-t border-[var(--yellow)] flex items-center gap-2">
                    <span className="material-symbols-rounded text-[var(--yellow)] text-sm">attach_file</span>
                    <span className="text-xs text-[var(--yellow)] font-medium">
                        {attachedContext.length} context attached
                    </span>
                    <div className="flex-1 flex gap-1 overflow-x-auto">
                        {attachedContext.map(ctx => (
                            <span
                                key={ctx.id}
                                className="text-xs px-2 py-0.5 bg-[var(--yellow)] bg-opacity-20 rounded-full whitespace-nowrap"
                            >
                                {ctx.label}
                            </span>
                        ))}
                    </div>
                    <button onClick={clearAttached} className="text-[var(--yellow)] hover:text-[var(--orange)]">
                        <span className="material-symbols-rounded text-sm">close</span>
                    </button>
                </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-[var(--gray)] bg-white">
                <div className="flex gap-3">
                    <input
                        ref={inputRef}
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder={attachedContext.length > 0
                            ? `Message with ${attachedContext.length} context attached...`
                            : "Type your message..."
                        }
                        className="flex-1 px-4 py-3 bg-[var(--bg-subtle)] rounded-full border border-[var(--gray)] focus:outline-none focus:border-[var(--yellow)] text-sm"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!inputValue.trim()}
                        className="w-12 h-12 bg-[var(--yellow)] text-[var(--black)] rounded-full flex items-center justify-center hover:scale-105 disabled:opacity-50 transition-all"
                    >
                        <span className="material-symbols-rounded">send</span>
                    </button>
                </div>
            </div>
        </div>
    );

    // Render Canvas Mode
    const renderCanvasMode = () => (
        <div className="flex-1 flex flex-col items-center justify-center p-8">
            <p className="text-xs text-[var(--text-dim)] uppercase tracking-wide mb-6">
                Drag context items to slots • Trace a path to compose
            </p>
            <div className="bg-white rounded-3xl shadow-lg p-8 border border-[var(--gray)]">
                <HexWorkspace
                    slots={hexSlots}
                    selectedIndices={hexSelection}
                    onSlotsChange={setHexSlots}
                    onSelectionChange={setHexSelection}
                />
            </div>
            {hexSelection.length > 0 && (
                <div className="mt-6 text-center">
                    <p className="text-sm text-[var(--text)]">
                        Path: {hexSelection.map(i => hexSlots[i]?.label || '○').join(' → ')}
                    </p>
                </div>
            )}
        </div>
    );

    return (
        <div className="flex-1 flex flex-col bg-[var(--bg-subtle)]">
            {mode === 'chat' ? renderChatMode() : renderCanvasMode()}
        </div>
    );
}
