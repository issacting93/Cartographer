/**
 * TaskWizardDemo.tsx
 * 
 * Demo page for the Task-First Interaction Model.
 * This is the evaluation prototype for the CUI 2026 paper.
 * 
 * Route: /task-wizard
 */

import { useState } from 'react';
import { TaskWizardPanel } from '@/components/context-engine/TaskWizardPanel';
import { MessageCircle, Send, Bot, User } from 'lucide-react';
import clsx from 'clsx';

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function TaskWizardDemo() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content: "Hello! I'm your Task-First AI assistant. Use the Task Wizard on the left to create tasks, pin constraints, and control what context I see when you ask questions.",
            timestamp: new Date(),
        }
    ]);
    const [inputText, setInputText] = useState('');
    const [isTyping, setIsTyping] = useState(false);

    const handleQuerySubmit = (augmentedPrompt: string, activeNodes: any[]) => {
        // Log the augmented prompt for debugging
        console.log('[TaskWizard] Augmented prompt:', augmentedPrompt);

        // Show user's original intent
        const userMessage: ChatMessage = {
            role: 'user',
            content: augmentedPrompt,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsTyping(true);

        // Simulate AI response with context awareness
        setTimeout(() => {
            const contextSummary = activeNodes.length > 0
                ? `I see ${activeNodes.length} active constraints:\n${activeNodes.map(n => `• [${n.type}] ${n.label}`).join('\n')}\n\n`
                : '';

            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: `${contextSummary}I'll help you with that while respecting your constraints. Here's what I found...`,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, assistantMessage]);
            setIsTyping(false);
        }, 1500);
    };

    const handleSendMessage = () => {
        if (!inputText.trim()) return;

        const userMessage: ChatMessage = {
            role: 'user',
            content: inputText,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsTyping(true);

        // Simulate response (in real implementation, this would call the LLM)
        setTimeout(() => {
            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: "I received your message. For the best results, try using the **Pin to Task** to save constraints, or use **Context Lens** to explicitly select what context I should consider.",
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, assistantMessage]);
            setIsTyping(false);
        }, 1000);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-100 to-indigo-50">
            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div>
                        <h1 className="text-xl font-bold text-gray-800">Task-First Interaction Demo</h1>
                        <p className="text-sm text-gray-500">CUI 2026: "Tasks, Not Turns"</p>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-xs bg-amber-100 text-amber-700 px-3 py-1 rounded-full font-medium">
                            Evaluation Prototype
                        </span>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto p-6">
                <div className="grid grid-cols-12 gap-6 h-[calc(100vh-140px)]">

                    {/* Left: Task Wizard Panel */}
                    <div className="col-span-5">
                        <TaskWizardPanel
                            userId="demo"
                            onQuerySubmit={handleQuerySubmit}
                            className="h-full"
                        />
                    </div>

                    {/* Right: Chat Interface */}
                    <div className="col-span-7 flex flex-col bg-white rounded-xl border border-gray-200 shadow-lg overflow-hidden">
                        {/* Chat Header */}
                        <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-4 py-3">
                            <div className="flex items-center gap-2">
                                <MessageCircle className="w-5 h-5 text-white" />
                                <h2 className="text-white font-bold">Conversation</h2>
                            </div>
                            <p className="text-slate-300 text-xs mt-1">
                                Chat with context-aware responses
                            </p>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {messages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={clsx(
                                        "flex gap-3",
                                        msg.role === 'user' ? "flex-row-reverse" : ""
                                    )}
                                >
                                    <div className={clsx(
                                        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
                                        msg.role === 'user'
                                            ? "bg-indigo-100 text-indigo-600"
                                            : "bg-slate-100 text-slate-600"
                                    )}>
                                        {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                                    </div>
                                    <div className={clsx(
                                        "max-w-[70%] p-3 rounded-xl text-sm",
                                        msg.role === 'user'
                                            ? "bg-indigo-600 text-white"
                                            : "bg-gray-100 text-gray-800"
                                    )}>
                                        <p className="whitespace-pre-wrap">{msg.content}</p>
                                        <div className={clsx(
                                            "text-xs mt-2",
                                            msg.role === 'user' ? "text-indigo-200" : "text-gray-400"
                                        )}>
                                            {msg.timestamp.toLocaleTimeString()}
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {isTyping && (
                                <div className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-slate-600" />
                                    </div>
                                    <div className="bg-gray-100 p-3 rounded-xl">
                                        <div className="flex gap-1">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <div className="border-t border-gray-200 p-4">
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                    placeholder="Type a message... (or use Context Lens for scoped queries)"
                                    className="flex-1 px-4 py-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                />
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!inputText.trim()}
                                    className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-all"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                            <p className="text-xs text-gray-400 mt-2 text-center">
                                Tip: Use the <strong>Context Lens</strong> tab to select which constraints the AI should consider.
                            </p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
