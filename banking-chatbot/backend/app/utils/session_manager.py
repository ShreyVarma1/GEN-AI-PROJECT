import uuid
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """
    In-memory session store keyed by session_id UUID.
    Each session holds a list of {role, content} message dicts.
    """

    def __init__(self):
        self._sessions: dict[str, list] = {}
        self._summaries: dict[str, str] = {}  # rolling summaries for old turns

    def new_session(self) -> str:
        """Generate a new session UUID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        logger.info(f"New session created: {session_id}")
        return session_id

    def get_history(self, session_id: str) -> List[dict]:
        """Return the full message history for a session."""
        return self._sessions.get(session_id, [])

    def get_summary(self, session_id: str) -> Optional[str]:
        """Return the rolling summary for older turns, if any."""
        return self._summaries.get(session_id)

    def add_turn(self, session_id: str, role: str, content: str):
        """Append a message turn to the session history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "content": content})

    def clear_session(self, session_id: str):
        """Clear all history for a session."""
        self._sessions.pop(session_id, None)
        self._summaries.pop(session_id, None)
        logger.info(f"Session cleared: {session_id}")

    def prune_history(self, session_id: str, max_turns: int):
        """
        Keep only the last max_turns message pairs.
        Older turns beyond 6 pairs are summarized into a rolling summary.
        """
        history = self._sessions.get(session_id, [])
        if len(history) <= max_turns * 2:
            return

        # Summarize turns older than the keep window
        cutoff = len(history) - (max_turns * 2)
        old_turns = history[:cutoff]
        recent_turns = history[cutoff:]

        # Build a simple text summary of old turns
        summary_parts = []
        for msg in old_turns:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            summary_parts.append(f"{role_label}: {msg['content'][:200]}")

        existing_summary = self._summaries.get(session_id, "")
        new_summary = existing_summary
        if summary_parts:
            new_summary = (existing_summary + "\n" if existing_summary else "") + \
                          "Earlier conversation summary:\n" + "\n".join(summary_parts)

        self._summaries[session_id] = new_summary
        self._sessions[session_id] = recent_turns
        logger.debug(f"Pruned session {session_id}: kept {len(recent_turns)} messages, summarized {len(old_turns)}")

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def list_sessions(self) -> List[str]:
        return list(self._sessions.keys())


session_manager = SessionManager()
