from datetime import date
from typing import List, Optional

SYSTEM_PROMPT_TEMPLATE = """You are a helpful, accurate, and professional banking support assistant for a fintech company.

Your role is to assist customers with:
- Loan queries (personal loans, home loans, auto loans)
- Credit card information and policies
- General banking FAQs
- Banking procedures and documentation

STRICT RULES:
1. Answer ONLY based on the provided context from retrieved documents.
2. If the context does not contain enough information to answer, say: "I don't have specific information about that in our documents. Please contact our support team at 1800-XXX-XXXX."
3. Never fabricate interest rates, fees, or policy details.
4. Be concise, clear, and professional.
5. When relevant, mention which document or section the information comes from.
6. Maintain context from previous messages in the conversation.
7. Format your responses clearly — use bullet points or numbered lists when listing multiple items.

Today's date: {date}
"""


class PromptBuilder:
    """Assembles system prompts and message lists for the LLM."""

    def build_system_prompt(self) -> str:
        """Build the system prompt with today's date injected."""
        return SYSTEM_PROMPT_TEMPLATE.format(date=date.today().strftime("%B %d, %Y"))

    def build_messages(
        self,
        chat_history: List[dict],
        user_query: str,
        retrieved_chunks: List[dict],
        rolling_summary: Optional[str] = None,
    ) -> tuple[str, list]:
        """
        Assemble the full message list for the LLM.

        Returns:
            (system_prompt, messages_list)

        The messages list follows Anthropic's format:
            [{"role": "user"|"assistant", "content": "..."}]

        Retrieved context is injected as a <context> block prepended
        to the user's latest message.
        """
        system_prompt = self.build_system_prompt()

        # Build context block from retrieved chunks
        context_block = self._build_context_block(retrieved_chunks)

        # Build the messages list
        messages = []

        # If there's a rolling summary of older turns, inject it as a system note
        if rolling_summary:
            messages.append({
                "role": "user",
                "content": f"[Previous conversation summary for context]\n{rolling_summary}"
            })
            messages.append({
                "role": "assistant",
                "content": "Understood. I have the context from our previous conversation."
            })

        # Add recent chat history (already pruned)
        for turn in chat_history:
            messages.append({"role": turn["role"], "content": turn["content"]})

        # Add the current user message with injected context
        if context_block:
            user_content = f"{context_block}\n\nUser Question: {user_query}"
        else:
            user_content = (
                f"Note: No relevant documents were found in the knowledge base for this query.\n\n"
                f"User Question: {user_query}"
            )

        messages.append({"role": "user", "content": user_content})
        return system_prompt, messages

    def _build_context_block(self, retrieved_chunks: List[dict]) -> str:
        """Format retrieved chunks into a structured context block."""
        if not retrieved_chunks:
            return ""

        context_parts = ["<context>", "The following information was retrieved from our banking documents:\n"]
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("metadata", {}).get("source", "Unknown")
            text = chunk.get("text", "")
            context_parts.append(f"[Source {i}: {source}]\n{text}\n")

        context_parts.append("</context>")
        return "\n".join(context_parts)


prompt_builder = PromptBuilder()
