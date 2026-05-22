import React, { useState, useRef, useEffect, KeyboardEvent } from "react";

interface InputBarProps {
  onSend: (message: string) => void;
  onUploadClick: () => void;
  isLoading: boolean;
}

export default function InputBar({ onSend, onUploadClick, isLoading }: InputBarProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      const maxHeight = 4 * 24 + 24; // ~4 rows
      textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + "px";
    }
  }, [value]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const charCount = value.length;
  const isOverLimit = charCount > 2000;
  const isEmpty = !value.trim();

  return (
    <div className="border-t border-slate-200 bg-white px-4 py-3">
      <div className={`flex items-end gap-2 rounded-xl border-2 transition-colors duration-150 bg-white px-3 py-2 ${
        isOverLimit
          ? "border-red-400"
          : "border-slate-200 focus-within:border-electric-500"
      }`}>
        {/* Upload button */}
        <button
          onClick={onUploadClick}
          className="flex-shrink-0 p-1.5 text-slate-400 hover:text-electric-600 hover:bg-slate-100 rounded-lg transition-colors duration-150 mb-0.5"
          title="Upload document"
          aria-label="Upload document"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about loans, credit cards, banking policies..."
          rows={1}
          maxLength={2100}
          disabled={isLoading}
          className="flex-1 resize-none outline-none text-sm text-slate-800 placeholder-slate-400 bg-transparent leading-6 disabled:opacity-60"
          aria-label="Chat message input"
        />

        {/* Character counter (shown at 500+) */}
        {charCount >= 500 && (
          <span className={`flex-shrink-0 text-xs self-end mb-1 ${isOverLimit ? "text-red-500 font-medium" : "text-slate-400"}`}>
            {charCount}/2000
          </span>
        )}

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={isEmpty || isLoading || isOverLimit}
          className="flex-shrink-0 w-9 h-9 rounded-lg bg-electric-600 hover:bg-electric-700 text-white flex items-center justify-center transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed mb-0.5"
          aria-label="Send message"
        >
          {isLoading ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          )}
        </button>
      </div>

      <p className="text-xs text-slate-400 mt-1.5 text-center">
        Press <kbd className="px-1 py-0.5 bg-slate-100 rounded text-slate-500 font-mono text-xs">Enter</kbd> to send,{" "}
        <kbd className="px-1 py-0.5 bg-slate-100 rounded text-slate-500 font-mono text-xs">Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
