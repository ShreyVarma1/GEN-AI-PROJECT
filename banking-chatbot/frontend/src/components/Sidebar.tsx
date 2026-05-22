import React, { useState, useRef, useEffect } from "react";
import { ChatSession } from "../hooks/useChat";

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onNewChat: () => void;
  onSelectSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, newTitle: string) => void;
  onDeleteSession: (sessionId: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

// ── Inline rename input ───────────────────────────────────────────────────────
function RenameInput({
  initialValue,
  onSave,
  onCancel,
}: {
  initialValue: string;
  onSave: (v: string) => void;
  onCancel: () => void;
}) {
  const [value, setValue] = useState(initialValue);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  const commit = () => {
    const trimmed = value.trim();
    if (trimmed) onSave(trimmed);
    else onCancel();
  };

  return (
    <input
      ref={inputRef}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => {
        if (e.key === "Enter") commit();
        if (e.key === "Escape") onCancel();
      }}
      className="flex-1 bg-navy-700 text-white text-sm px-2 py-0.5 rounded outline-none border border-electric-500 min-w-0"
      maxLength={80}
      aria-label="Rename chat"
    />
  );
}

// ── Delete confirmation popover ───────────────────────────────────────────────
function DeleteConfirm({
  onConfirm,
  onCancel,
}: {
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="absolute right-0 top-full mt-1 z-50 bg-navy-800 border border-navy-600 rounded-xl shadow-xl p-3 w-52 animate-fade-in">
      <p className="text-white text-xs font-medium mb-2">Delete this chat?</p>
      <p className="text-navy-400 text-xs mb-3">This cannot be undone.</p>
      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          className="flex-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium py-1.5 rounded-lg transition-colors"
        >
          Delete
        </button>
        <button
          onClick={onCancel}
          className="flex-1 bg-navy-700 hover:bg-navy-600 text-white text-xs font-medium py-1.5 rounded-lg transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

// ── Single session row ────────────────────────────────────────────────────────
function SessionRow({
  session,
  isActive,
  onSelect,
  onRename,
  onDelete,
}: {
  session: ChatSession;
  isActive: boolean;
  onSelect: () => void;
  onRename: (title: string) => void;
  onDelete: () => void;
}) {
  const [isRenaming, setIsRenaming] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu on outside click
  useEffect(() => {
    if (!showMenu && !showDeleteConfirm) return;
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowMenu(false);
        setShowDeleteConfirm(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [showMenu, showDeleteConfirm]);

  return (
    <li className="relative group">
      <div
        className={`flex items-center gap-1.5 px-2 py-2 rounded-lg cursor-pointer transition-colors duration-100 ${
          isActive
            ? "bg-navy-700 text-white"
            : "text-slate-300 hover:bg-navy-800 hover:text-white"
        }`}
        onClick={() => !isRenaming && onSelect()}
      >
        {/* Chat icon */}
        <svg
          className="w-3.5 h-3.5 flex-shrink-0 opacity-50"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>

        {/* Title or rename input */}
        {isRenaming ? (
          <RenameInput
            initialValue={session.title}
            onSave={(v) => {
              onRename(v);
              setIsRenaming(false);
            }}
            onCancel={() => setIsRenaming(false)}
          />
        ) : (
          <span className="flex-1 text-sm truncate">{session.title}</span>
        )}

        {/* Three-dot menu button — visible on hover or when active */}
        {!isRenaming && (
          <div ref={menuRef} className="relative flex-shrink-0">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu((v) => !v);
                setShowDeleteConfirm(false);
              }}
              className={`p-1 rounded-md transition-all duration-100 ${
                showMenu
                  ? "opacity-100 bg-navy-600 text-white"
                  : "opacity-0 group-hover:opacity-100 text-slate-400 hover:text-white hover:bg-navy-600"
              }`}
              aria-label="Chat options"
            >
              <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="5" cy="12" r="2" />
                <circle cx="12" cy="12" r="2" />
                <circle cx="19" cy="12" r="2" />
              </svg>
            </button>

            {/* Dropdown menu */}
            {showMenu && !showDeleteConfirm && (
              <div className="absolute right-0 top-full mt-1 z-50 bg-navy-800 border border-navy-600 rounded-xl shadow-xl py-1 w-36 animate-fade-in">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowMenu(false);
                    setIsRenaming(true);
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-300 hover:bg-navy-700 hover:text-white transition-colors"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Rename
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowMenu(false);
                    setShowDeleteConfirm(true);
                  }}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-navy-700 hover:text-red-300 transition-colors"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete
                </button>
              </div>
            )}

            {/* Delete confirmation */}
            {showDeleteConfirm && (
              <DeleteConfirm
                onConfirm={() => {
                  setShowDeleteConfirm(false);
                  onDelete();
                }}
                onCancel={() => setShowDeleteConfirm(false)}
              />
            )}
          </div>
        )}
      </div>
    </li>
  );
}

// ── Group sessions by date ────────────────────────────────────────────────────
function groupByDate(sessions: ChatSession[]) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today.getTime() - 86400000);
  const sevenDaysAgo = new Date(today.getTime() - 7 * 86400000);
  const thirtyDaysAgo = new Date(today.getTime() - 30 * 86400000);

  const groups: { label: string; items: ChatSession[] }[] = [
    { label: "Today", items: [] },
    { label: "Yesterday", items: [] },
    { label: "Previous 7 Days", items: [] },
    { label: "Previous 30 Days", items: [] },
    { label: "Older", items: [] },
  ];

  for (const s of sessions) {
    const d = new Date(s.createdAt);
    if (d >= today) groups[0].items.push(s);
    else if (d >= yesterday) groups[1].items.push(s);
    else if (d >= sevenDaysAgo) groups[2].items.push(s);
    else if (d >= thirtyDaysAgo) groups[3].items.push(s);
    else groups[4].items.push(s);
  }

  return groups.filter((g) => g.items.length > 0);
}

// ── Main Sidebar ──────────────────────────────────────────────────────────────
export default function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onRenameSession,
  onDeleteSession,
  isOpen,
  onClose,
}: SidebarProps) {
  const groups = groupByDate(sessions);

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full z-30 w-64 bg-[#0f1724] flex flex-col transition-transform duration-300
          lg:relative lg:translate-x-0 lg:z-auto
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
        aria-label="Chat history sidebar"
      >
        {/* Logo */}
        <div className="px-4 pt-5 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-electric-600 flex items-center justify-center shadow">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h1 className="font-serif text-white font-semibold text-sm leading-tight">BankBot</h1>
              <p className="text-slate-500 text-xs">AI Banking Support</p>
            </div>
          </div>
        </div>

        {/* New Chat */}
        <div className="px-3 pb-2">
          <button
            onClick={onNewChat}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl bg-electric-600 hover:bg-electric-700 text-white text-sm font-medium transition-colors shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Session list */}
        <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-4">
          {groups.length === 0 ? (
            <div className="text-center py-10 px-4">
              <div className="w-10 h-10 rounded-full bg-navy-800 flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-slate-500 text-xs">No conversations yet</p>
              <p className="text-slate-600 text-xs mt-1">Start a new chat above</p>
            </div>
          ) : (
            groups.map((group) => (
              <div key={group.label}>
                <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider px-2 mb-1">
                  {group.label}
                </p>
                <ul className="space-y-0.5">
                  {group.items.map((session) => (
                    <SessionRow
                      key={session.id}
                      session={session}
                      isActive={session.id === currentSessionId}
                      onSelect={() => onSelectSession(session.id)}
                      onRename={(title) => onRenameSession(session.id, title)}
                      onDelete={() => onDeleteSession(session.id)}
                    />
                  ))}
                </ul>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-navy-800">
          <p className="text-slate-600 text-xs text-center">Powered by Gemini + RAG</p>
        </div>
      </aside>
    </>
  );
}
