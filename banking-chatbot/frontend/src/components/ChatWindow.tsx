import React, { useEffect, useRef } from "react";
import { Message } from "../hooks/useChat";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import InputBar from "./InputBar";

const STARTER_QUESTIONS = [
  "What documents do I need for a personal loan?",
  "What is the interest rate on a Gold credit card?",
  "How long does home loan approval take?",
  "What are the NEFT transfer limits?",
];

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onUploadClick: () => void;
  onMenuClick: () => void;
}

export default function ChatWindow({
  messages,
  isLoading,
  error,
  onSend,
  onUploadClick,
  onMenuClick,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full bg-slate-50">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 bg-white border-b border-slate-200 shadow-sm">
        {/* Mobile menu button */}
        <button
          onClick={onMenuClick}
          className="lg:hidden p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          aria-label="Open sidebar"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-electric-600 flex items-center justify-center shadow-sm">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h2 className="font-semibold text-slate-800 text-sm leading-tight">Banking Support</h2>
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
              <span className="text-xs text-slate-500">Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Messages area */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-4"
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {isEmpty ? (
          /* Empty state */
          <div className="flex flex-col items-center justify-center h-full text-center px-4 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-electric-600 flex items-center justify-center shadow-lg mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="font-serif text-xl text-slate-700 mb-1">How can I help you today?</h3>
            <p className="text-slate-500 text-sm mb-8 max-w-sm">
              Ask me anything about loans, credit cards, banking policies, or account services.
            </p>

            {/* Starter question chips */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-lg">
              {STARTER_QUESTIONS.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => onSend(question)}
                  className="text-left px-4 py-3 rounded-xl bg-white border border-slate-200 hover:border-electric-400 hover:bg-electric-50 text-sm text-slate-700 hover:text-electric-700 transition-all duration-150 shadow-sm"
                >
                  <span className="text-electric-500 mr-1.5">→</span>
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Message list */
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}

            {/* Show typing indicator only for non-streaming loading */}
            {isLoading && !messages.some((m) => m.isStreaming) && (
              <TypingIndicator />
            )}
          </>
        )}

        {/* Error banner */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600 animate-fade-in">
            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <InputBar
        onSend={onSend}
        onUploadClick={onUploadClick}
        isLoading={isLoading}
      />
    </div>
  );
}
