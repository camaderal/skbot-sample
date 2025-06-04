"""Chart Tools Module."""

import uuid

from data_models.attachments import (
    LineChart,
    LineChartData,
    PieChart,
    PieChartData,
    VerticalBarChart,
    VerticalBarChartDataValue,
)
from tools import AbstractTool


class LineChartTool(AbstractTool):
    """Tool for creating line charts."""

    def __init__(
        self,
        name: str = "LineChart",
        description: str = "Generate a stacked line chart.  The chart would be included automatically in the response. "
        "The data should be a list of LineChartData objects. A LineChartData object representa a single line "
        "in the chart and should contain a list of LineChartDataValue objects.  A LineChartDataValue object"
        "represents a single point which has an x value (string or number) and a y value (number)."
        "Sample input: "
        """
        {
            title = "Sample Line Chart",
            data = [
                {
                    values = [
                        {"x": "point 1", "y": 5},
                        {"x": "point 2", "y": 3},
                        {"x": "point 3", "y": 3},
                        {"x": "point 4", "y": 7}
                    ],
                    color = "red",
                    legend = "Line 1"
                }
            ]
        }
        """,
    ):
        super().__init__(name=name, description=description, function=self.create_line_chart)

    @staticmethod
    def create_line_chart(title: str, data: list[LineChartData]) -> LineChart:
        """
        Create a line chart with the given title and data.

        Args:
            title (str): The title of the line chart.
            data (list[LineChartData]): The data for the line chart.

        Returns:
            LineChart: An instance of LineChart containing the generated chart.

        """
        return LineChart(id=str(uuid.uuid4()), title=title, data=data)


class PieChartTool(AbstractTool):
    """Tool for creating pie charts."""

    def __init__(
        self,
        name: str = "PieChart",
        description: str = "Generate a pie chart.  The chart would be included automatically in the response.",
    ):
        super().__init__(name=name, description=description, function=self.create_pie_chart)

    @staticmethod
    def create_pie_chart(title: str, data: list[PieChartData]) -> PieChart:
        """
        Create a pie chart with the given title and data.

        Args:
            title (str): The title of the pie chart.
            data (list[PieChartData]): The data for the pie chart.

        Returns:
            PieChart: An instance of PieChart containing the generated chart.

        """
        return PieChart(id=str(uuid.uuid4()), title=title, data=data)


class VerticalBarChartTool(AbstractTool):
    """Tool for creating vertical bar charts."""

    def __init__(
        self,
        name: str = "VerticalBarChart",
        description: str = "Generate a vertical bar chart. The chart would be included automatically in the response.",
    ):
        super().__init__(name=name, description=description, function=self.create_vertical_bar_chart)

    @staticmethod
    def create_vertical_bar_chart(title: str, data: list[VerticalBarChartDataValue]) -> VerticalBarChart:
        """
        Create a vertical bar chart with the given title and data.

        Args:
            title (str): The title of the vertical bar chart.
            data (list[VerticalBarChartDataValue]): The data for the vertical bar chart.

        Returns:
            VerticalBarChart: An instance of VerticalBarChart containing the generated chart.

        """
        return VerticalBarChart(id=str(uuid.uuid4()), title=title, data=data)
