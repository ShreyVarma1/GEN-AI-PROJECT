import React from "react";

export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-slide-up">
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-electric-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
        B
      </div>

      {/* Bubble */}
      <div className="chat-bubble-assistant flex items-center gap-1 py-4 px-5">
        <span
          className="w-2 h-2 rounded-full bg-slate-400 inline-block animate-bounce-dot"
          style={{ animationDelay: "0ms" }}
        />
        <span
          className="w-2 h-2 rounded-full bg-slate-400 inline-block animate-bounce-dot"
          style={{ animationDelay: "200ms" }}
        />
        <span
          className="w-2 h-2 rounded-full bg-slate-400 inline-block animate-bounce-dot"
          style={{ animationDelay: "400ms" }}
        />
      </div>
    </div>
  );
}
