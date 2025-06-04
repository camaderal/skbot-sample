"""
Core Abstract tools for the MACS project.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable


class Tool(ABC):
    """
    Abstract base class representing a generic tool that an agent can use.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of the tool."""
        pass

    @property
    @abstractmethod
    def function(self) -> Callable:
        """Return the function that implements the tool."""
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the tool."""
        pass


class AbstractTool(Tool):
    """Abstract base class for tools."""

    def __init__(self, name: str, description: str, function: Callable):
        self._name = name
        self._description = description
        self._function = function

    @property
    def name(self) -> str:
        """
        Get the name of the tool.

        Returns:
            str: The name of the tool.

        """
        return self._name

    @property
    def description(self) -> str:
        """
        Get the description of the tool.

        Returns:
            str: The description of the tool.

        """
        return self._description

    @property
    def function(self) -> Callable:
        """
        Execute the tool's function.

        Returns:
            Callable: The function associated with the tool.

        """
        return self._function

    @property
    def function_signature(self) -> dict[str, Any]:
        """
        Get the function signature (parameters and annotations).

        Returns:
            dict[str, Any]: A dictionary containing the function's parameters and their annotations.

        """
        return self._function.__annotations__

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the tool to a dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the tool, including its name,
              description, and function signature.

        """
        return {
            "name": self._name,
            "description": self._description,
            "function": self.function_signature,
        }
