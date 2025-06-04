"""Conversation data models for managing conversation history and turns."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ConversationTurn(BaseModel):
    """
    Data model for a single turn in a conversation.
    Represents a message in the conversation history.
    """

    role: str  # "user", "assistant", "system"
    content: str  # The content of the turn
    created_at: datetime  # Timestamp of the turn creation
    metadata: dict[str, Any] = {}  # Additional metadata for the turn
    attachments: list[Any] = []  # List of attachments for the turn


class ConversationData:
    """
    Data model for conversation history.
    Contains a list of conversation turns and manages the conversation state.
    """

    def __init__(
        self,
        history: list[ConversationTurn],
        max_turns: int = 10,
        thread_id: str = None,
    ):
        self.thread_id = thread_id
        self.history = history
        self.max_turns = max_turns

    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a new turn to the conversation history.
        If the history exceeds max_turns, the oldest turn is removed.
        """
        self.history.append(turn)
        if len(self.history) >= self.max_turns:
            self.history.pop(0)

    def toMessages(self) -> list[dict[str, str]]:
        """
        Convert the conversation history to a list of messages.
        Each message is represented as a dictionary with 'role' and 'content'.
        """
        return [{"role": turn.role, "content": turn.content} for turn in self.history]
