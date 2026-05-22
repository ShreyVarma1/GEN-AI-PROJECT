import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "../hooks/useChat";
import SourceChips from "./SourceChips";
import TypingIndicator from "./TypingIndicator";

interface MessageBubbleProps {
  message: Message;
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  if (message.isStreaming && message.content === "") {
    return <TypingIndicator />;
  }

  if (isUser) {
    return (
      <div className="flex items-end justify-end gap-2 animate-slide-up">
        <div className="flex flex-col items-end gap-1">
          <div className="chat-bubble-user">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          </div>
          <span className="text-xs text-slate-400 px-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
        {/* User avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
          U
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex items-start gap-3 animate-slide-up">
      {/* Bot avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-electric-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
        B
      </div>

      <div className="flex flex-col gap-1 max-w-[80%]">
        <div className="chat-bubble-assistant">
          {message.isStreaming ? (
            <div>
              <div className="markdown-content text-sm">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              </div>
              {/* Blinking cursor while streaming */}
              <span className="inline-block w-0.5 h-4 bg-slate-400 animate-pulse ml-0.5 align-middle" />
            </div>
          ) : (
            <div className="markdown-content text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* Source chips */}
          {!message.isStreaming && message.sources && message.sources.length > 0 && (
            <SourceChips sources={message.sources} />
          )}
        </div>

        <span className="text-xs text-slate-400 px-1">
          {formatTime(message.timestamp)}
          {message.isStreaming && (
            <span className="ml-1 text-electric-600">● streaming</span>
          )}
        </span>
      </div>
    </div>
  );
}
