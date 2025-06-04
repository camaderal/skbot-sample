"""Data models for attachments in the chatbot response."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class Citation(BaseModel):
    """An item retrieved from a knowledge source."""

    title: str
    url: str
    content: str = ""  # Content of the citation, can be empty
    metadata: dict[str, Any] = {}


class Media(BaseModel):
    """Represents an attachment of media."""

    content: str  # URL or base64 encoded string
    mime_type: str  # MIME type of the media (e.g., "image/png", "video/mp4")
    label: Optional[str] = None  # Optional label for the media, can be used as a caption or description


class ChartColor(str, Enum):
    """Enumeration of chart colors used in the response."""

    GOOD = "good"
    WARNING = "warning"
    ATTENTION = "attention"
    NEUTRAL = "neutral"
    CATEGORICAL_RED = "categoricalRed"
    CATEGORICAL_PURPLE = "categoricalPurple"
    CATEGORICAL_LAVENDER = "categoricalLavender"
    CATEGORICAL_BLUE = "categoricalBlue"
    CATEGORICAL_LIGHT_BLUE = "categoricalLightBlue"
    CATEGORICAL_TEAL = "categoricalTeal"
    CATEGORICAL_GREEN = "categoricalGreen"
    CATEGORICAL_LIME = "categoricalLime"
    CATEGORICAL_MARIGOLD = "categoricalMarigold"
    SEQUENTIAL_1 = "sequential1"
    SEQUENTIAL_2 = "sequential2"
    SEQUENTIAL_3 = "sequential3"
    SEQUENTIAL_4 = "sequential4"
    SEQUENTIAL_5 = "sequential5"
    SEQUENTIAL_6 = "sequential6"
    SEQUENTIAL_7 = "sequential7"
    SEQUENTIAL_8 = "sequential8"
    DIVERGING_BLUE = "divergingBlue"
    DIVERGING_LIGHT_BLUE = "divergingLightBlue"
    DIVERGING_CYAN = "divergingCyan"
    DIVERGING_TEAL = "divergingTeal"
    DIVERGING_YELLOW = "divergingYellow"
    DIVERGING_PEACH = "divergingPeach"
    DIVERGING_LIGHT_RED = "divergingLightRed"
    DIVERGING_RED = "divergingRed"
    DIVERGING_MAROON = "divergingMaroon"
    DIVERGING_GRAY = "divergingGray"

    def __str__(self) -> str:
        """Return the string representation of the chart color."""
        return self.value


class Chart(BaseModel):
    """Represents a chart structure for the response."""

    id: str  # Unique identifier for the chart
    title: str  # Title of the chart


class VerticalBarChartDataValue(BaseModel):
    """Represents a single data value in a vertical bar chart."""

    color: Optional[ChartColor] = None  # Color of the bar (optional)
    x: str | float  # X-axis value (can be a string or a number)
    y: float  # Y-axis value


class VerticalBarChart(Chart):
    """Represents a vertical bar chart structure for the response."""

    data: list[VerticalBarChartDataValue]


class LineChartDataValue(BaseModel):
    """Represents a single data value in a line chart."""

    x: str | float  # X-axis value (can be a string or a number)
    y: float  # Y-axis value


class LineChartData(BaseModel):
    """Represents a single line chart data set."""

    values: list["LineChartDataValue"]  # List of data values for the line chart
    color: Optional[ChartColor] = None  # Color of the line chart
    legend: Optional[str] = None  # Legend for the line chart


class LineChart(Chart):
    """Represents a line chart structure for the response."""

    data: list[LineChartData]  # List of line chart data values


class PieChartData(BaseModel):
    """Represents a single data value in a pie chart."""

    value: float  # Value of the pie slice
    color: Optional[ChartColor] = None  # Color of the pie slice (optional)
    legend: Optional[str] = None  # Legend for the pie slice (optional)


class PieChart(Chart):
    """Represents a pie chart structure for the response."""

    data: list[PieChartData]  # List of pie chart data values
