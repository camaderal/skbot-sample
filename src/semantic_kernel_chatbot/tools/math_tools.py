"""Math Tools Module."""

from tools import AbstractTool


class AddTool(AbstractTool):
    """Tool for adding two numbers."""

    def __init__(self, name: str = "Add", description: str = "Add two numbers, such as 6+3") -> None:
        super().__init__(name=name, description=description, function=staticmethod(lambda x, y: x + y))


class SubtractTool(AbstractTool):
    """Tool for subtracting two numbers."""

    def __init__(self, name: str = "Subtract", description: str = "Subtract two numbers, such as 6-3") -> None:
        super().__init__(name=name, description=description, function=staticmethod(lambda x, y: x - y))


class MultiplyTool(AbstractTool):
    """Tool for multiplying two numbers."""

    def __init__(self, name: str = "Multiply", description: str = "Multiply two numbers, such as 6*3") -> None:
        super().__init__(name=name, description=description, function=staticmethod(lambda x, y: x * y))


class DivideTool(AbstractTool):
    """Tool for dividing two numbers."""

    def __init__(self, name: str = "Divide", description: str = "Divide two numbers, such as 6/3") -> None:
        super().__init__(name=name, description=description, function=staticmethod(lambda x, y: x / y))
