"""
Defines the Agent interface and AbstractAgent base class for agent implementations.
Provides a common interface and default behaviors for agents that process messages and use tools.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from botbuilder.core import TurnContext
from data_models.conversation_data import ConversationData, ConversationTurn
from tools import Tool

# Configure logging
logger = logging.getLogger(__name__)


class Agent(ABC):
    """
    Interface for an agent that can process messages and use tools.

    This provides a common interface for different agent implementations,
    allowing the rest of the application to work with any agent type.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Get the agent's unique identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the agent's display name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get the agent's description."""
        pass

    @property
    @abstractmethod
    def prompt(self) -> str:
        """Get the agent's system prompt/instructions."""
        pass

    @property
    @abstractmethod
    def tools(self) -> dict[str, Tool]:
        """Get the agent's available tools."""
        pass

    @property
    @abstractmethod
    def settings(self) -> dict[str, Any]:
        """Get the agent's configuration settings."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the agent and its resources."""
        pass

    @abstractmethod
    async def process(self, conversation_data: ConversationData, turn_context: TurnContext = None) -> ConversationTurn:
        """
        Process a message and return the response.

        Args:
            conversation_data (ConversationData): The conversation data containing the message and context.
            turn_context (TurnContext, optional): The turn context for the current conversation turn.

        Returns:
            ConversationTurn: The processed conversation turn with the response.

        """
        pass

    @abstractmethod
    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the agent's toolkit.

        Args:
            tool (Tool): The Tool object to add.

        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the agent object to a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the agent object.

        """
        pass


class AbstractAgent(Agent):
    """
    Abstract base class for Agent implementations.

    This class provides default implementations for some of the Agent interface methods.

    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        prompt: str,
        tools: dict[str, Tool],
        settings: dict[str, Any] = None,
    ):
        self._id = agent_id
        self._name = name
        self._description = description
        self._prompt = prompt
        self._tools = tools
        self._settings = settings if settings is not None else {}

    @property
    def id(self) -> str:
        """
        Get the agent's unique identifier.

        Returns:
            str: The unique identifier of the agent.

        """
        return self._id

    @property
    def name(self) -> str:
        """
        Get the agent's display name.

        Returns:
            str: The display name of the agent.

        """
        return self._name

    @property
    def description(self) -> str:
        """
        Get the agent's description.

        Returns:
            str: The description of the agent.

        """
        return self._description

    @property
    def prompt(self) -> str:
        """
        Get the agent's system prompt/instructions.

        Returns:
            str: The system prompt of the agent.

        """
        return self._prompt

    @property
    def tools(self) -> dict[str, Tool]:
        """
        Get the agent's available tools.

        Returns:
            dict[str, Tool]: A dictionary of tool names and their corresponding Tool objects.

        """
        return self._tools

    @property
    def settings(self) -> dict[str, Any]:
        """
        Get the agent's configuration settings.

        Returns:
            dict[str, Any]: A dictionary of settings for the agent.

        """
        return self._settings

    def initialize(self) -> None:
        """Default implementation for agent initialization."""
        logger.info(f"Initializing agent '{self.name}' with ID '{self.id}'")
        # Placeholder for actual initialization logic

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the agent's toolkit.

        Args:
            tool (Tool): The Tool object to add.

        Raises:
            ValueError: If the tool already exists in the agent's toolkit.

        """
        if tool.name not in self._tools:
            self._tools[tool.name] = tool
            logger.info(f"Added tool '{tool.name}' to agent '{self.name}'")
        else:
            logger.error(f"Tool '{tool.name}' already exists in agent '{self.name}'")
            raise ValueError(f"Tool '{tool.name}' already exists in agent '{self.name}'")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the agent object to a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the agent object.

        """
        return {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "prompt": self._prompt,
            "tools": {name: tool.to_dict() for name, tool in self._tools.items()},
            "settings": self._settings,
        }
