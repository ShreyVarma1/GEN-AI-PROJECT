import { useState, useCallback, useRef, useEffect } from "react";
import { chatAPI, SourceChunk } from "../lib/api";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  messages: Message[]; // full message history stored per session
}

const SESSIONS_STORAGE_KEY = "bankbot_sessions_v2";
const ACTIVE_SESSION_KEY = "bankbot_active_session";

function generateId(): string {
  return Math.random().toString(36).substring(2, 11);
}

function saveSessions(sessions: ChatSession[]) {
  try {
    // Store sessions without messages for the index, messages stored separately
    const index = sessions.map((s) => ({
      id: s.id,
      title: s.title,
      createdAt: s.createdAt,
    }));
    localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(index));
    // Store messages per session
    sessions.forEach((s) => {
      localStorage.setItem(`bankbot_msgs_${s.id}`, JSON.stringify(s.messages));
    });
  } catch {
    // Storage full — ignore
  }
}

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSIONS_STORAGE_KEY);
    if (!raw) return [];
    const index = JSON.parse(raw) as Array<{ id: string; title: string; createdAt: string }>;
    return index.map((s) => {
      const msgsRaw = localStorage.getItem(`bankbot_msgs_${s.id}`);
      const messages: Message[] = msgsRaw
        ? (JSON.parse(msgsRaw) as Message[]).map((m) => ({
            ...m,
            timestamp: new Date(m.timestamp),
          }))
        : [];
      return { id: s.id, title: s.title, createdAt: new Date(s.createdAt), messages };
    });
  } catch {
    return [];
  }
}

function deleteSessionStorage(sessionId: string) {
  localStorage.removeItem(`bankbot_msgs_${sessionId}`);
}

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>(() => loadSessions());
  const [activeSessionId, setActiveSessionId] = useState<string | null>(
    () => localStorage.getItem(ACTIVE_SESSION_KEY)
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Derived: current session and its messages
  const currentSession = sessions.find((s) => s.id === activeSessionId) ?? null;
  const messages = currentSession?.messages ?? [];

  // Persist active session id
  useEffect(() => {
    if (activeSessionId) {
      localStorage.setItem(ACTIVE_SESSION_KEY, activeSessionId);
    } else {
      localStorage.removeItem(ACTIVE_SESSION_KEY);
    }
  }, [activeSessionId]);

  // Persist sessions whenever they change
  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  // ── helpers ──────────────────────────────────────────────────────────────

  const updateSessionMessages = useCallback(
    (sessionId: string, updater: (msgs: Message[]) => Message[]) => {
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, messages: updater(s.messages) } : s
        )
      );
    },
    []
  );

  // ── public API ────────────────────────────────────────────────────────────

  const newChat = useCallback(() => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setActiveSessionId(null);
    setError(null);
    setIsLoading(false);
  }, []);

  const selectSession = useCallback((id: string) => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setActiveSessionId(id);
    setError(null);
    setIsLoading(false);
  }, []);

  const renameSession = useCallback((id: string, newTitle: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, title: newTitle.trim() || s.title } : s))
    );
  }, []);

  const deleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => prev.filter((s) => s.id !== id));
      deleteSessionStorage(id);
      // Clear backend session
      chatAPI.clearSession(id).catch(() => {});
      if (activeSessionId === id) {
        setActiveSessionId(null);
        setError(null);
      }
    },
    [activeSessionId]
  );

  const sendMessage = useCallback(
    async (text: string, useStream = false) => {
      if (!text.trim() || isLoading) return;

      setError(null);

      // Create a new session if none is active
      let currentId = activeSessionId;
      if (!currentId) {
        currentId = generateId();
        const title = text.length > 42 ? text.substring(0, 42) + "…" : text;
        const newSession: ChatSession = {
          id: currentId,
          title,
          createdAt: new Date(),
          messages: [],
        };
        setSessions((prev) => [newSession, ...prev.slice(0, 49)]);
        setActiveSessionId(currentId);
      }

      const sid = currentId;

      // Append user message
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: text.trim(),
        timestamp: new Date(),
      };
      updateSessionMessages(sid, (msgs) => [...msgs, userMsg]);
      setIsLoading(true);

      if (useStream) {
        const streamingId = generateId();
        const streamingMsg: Message = {
          id: streamingId,
          role: "assistant",
          content: "",
          timestamp: new Date(),
          isStreaming: true,
        };
        updateSessionMessages(sid, (msgs) => [...msgs, streamingMsg]);

        try {
          abortControllerRef.current = new AbortController();
          const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

          const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sid, message: text.trim(), stream: true }),
            signal: abortControllerRef.current.signal,
          });

          if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP ${response.status}`);
          }

          const reader = response.body?.getReader();
          const decoder = new TextDecoder();
          let fullContent = "";
          let sources: SourceChunk[] = [];

          if (reader) {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              const chunk = decoder.decode(value, { stream: true });
              for (const line of chunk.split("\n")) {
                if (!line.startsWith("data: ")) continue;
                try {
                  const data = JSON.parse(line.slice(6));
                  if (data.type === "delta") {
                    fullContent += data.text;
                    updateSessionMessages(sid, (msgs) =>
                      msgs.map((m) => (m.id === streamingId ? { ...m, content: fullContent } : m))
                    );
                  } else if (data.type === "sources") {
                    sources = data.sources || [];
                  } else if (data.type === "done") {
                    updateSessionMessages(sid, (msgs) =>
                      msgs.map((m) =>
                        m.id === streamingId ? { ...m, isStreaming: false, sources } : m
                      )
                    );
                  } else if (data.type === "error") {
                    throw new Error(data.message);
                  }
                } catch {
                  // skip malformed lines
                }
              }
            }
          }
        } catch (err: unknown) {
          if (err instanceof Error && err.name === "AbortError") {
            setIsLoading(false);
            return;
          }
          const msg = err instanceof Error ? err.message : "Failed to get response";
          setError(msg);
          updateSessionMessages(sid, (msgs) =>
            msgs.map((m) =>
              m.id === streamingId
                ? { ...m, content: "Sorry, I encountered an error. Please try again.", isStreaming: false }
                : m
            )
          );
        } finally {
          setIsLoading(false);
        }
      } else {
        // Non-streaming
        try {
          const response = await chatAPI.sendMessage({
            session_id: sid,
            message: text.trim(),
            stream: false,
          });
          const data = response.data;
          const assistantMsg: Message = {
            id: generateId(),
            role: "assistant",
            content: data.answer,
            sources: data.sources,
            timestamp: new Date(),
          };
          updateSessionMessages(sid, (msgs) => [...msgs, assistantMsg]);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : "Failed to get response";
          setError(msg);
          updateSessionMessages(sid, (msgs) => [
            ...msgs,
            {
              id: generateId(),
              role: "assistant",
              content: "Sorry, I encountered an error. Please try again.",
              timestamp: new Date(),
            },
          ]);
        } finally {
          setIsLoading(false);
        }
      }
    },
    [isLoading, activeSessionId, updateSessionMessages]
  );

  return {
    messages,
    isLoading,
    error,
    sessionId: activeSessionId,
    sessions,
    sendMessage,
    newChat,
    selectSession,
    renameSession,
    deleteSession,
  };
}
