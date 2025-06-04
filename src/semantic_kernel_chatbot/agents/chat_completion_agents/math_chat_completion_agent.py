"""
Math Chat Completion Agent Sample.
"""

from agents.chat_completion_agent import AbstractChatCompletionAgent
from data_models.attachments import Citation, Media
from tools import AbstractTool
from tools.chart_tools import LineChartTool, PieChartTool, VerticalBarChartTool
from tools.math_tools import AddTool, DivideTool, MultiplyTool, SubtractTool


def research(query: str) -> tuple[str, list[Citation]]:
    """
    Research a query on the web.

    Args:
        query (str): The query to research.

    Returns:
        tuple[str, list[Citation]]: A string with the result of the research and a list of citations.

    """
    # This function will be implemented later

    citations = [
        Citation(
            title="Harry Potter",
            url="https://harrypotter.fandom.com/wiki/Harry_Potter",
            metadata={"birthday": "1980-07-31", "house": "Gryffindor", "blood_status": "Half-blood"},
        ),
        Citation(
            title="Hermione Granger",
            url="https://harrypotter.fandom.com/wiki/Hermione_Granger",
            metadata={"birthday": "1979-09-19", "house": "Gryffindor", "blood_status": "Muggle-born"},
        ),
        Citation(
            title="Ron Weasley",
            url="https://harrypotter.fandom.com/wiki/Ron_Weasley",
            metadata={"birthday": "1980-03-01", "house": "Gryffindor", "blood_status": "Pure-blood"},
        ),
    ]

    return "Blood and Gold finished today", citations


def get_image(topic: str) -> str:
    """
    Get image related to a topic.

    Args:
        topic (str): The topic to get media for.

    Returns:
        str: A URL of an image related to the topic.

    """
    # This function will be implemented later
    return "https://eskipaper.com/images/harry-potter-3.jpg"


def get_video(topic: str) -> Media:
    """
    Get video related to a topic.

    Args:
        topic (str): The topic to get media for.

    Returns:
        Media: A media object containing a video related to the topic.

    """
    # This function will be implemented later
    return Media(
        content="https://www.youtube.com/watch?v=YsqcODOEO-M",
        mime_type="video/mp4",
        label="Harry Potter Trailer",
    )


class MathSemanticKernelAgent(AbstractChatCompletionAgent):
    """
    A Semantic Kernel Agent that can help you with math problems.
    """

    def __init__(self) -> None:
        super().__init__(
            agent_id="math_semantic_kernel_agent",
            name="Math Semantic Kernel Agent",
            description="A Semantic Kernel Agent that can help you with math problems",
            prompt=(
                "You can solve math problems with the following tools: Add, Subtract, Multiply, Divide. "
                "Please use a tool to solve math problems before you solve the math problem by yourself."
                "Do not generate markdown with data:image/... URIs. Do not include image placeholders."
                "If a chart or image is to be shown, describe it in text or reference a hosted URL only."
            ),
            tools={
                "Add": AddTool(),
                "Subtract": SubtractTool(),
                "Multiply": MultiplyTool(),
                "Divide": DivideTool(),
                "Research": AbstractTool(
                    name="Research",
                    description="Search the web for information to answer the question.",
                    function=research,
                ),
                "GetImage": AbstractTool(
                    name="GetImage",
                    description="Get image related to the topic.",
                    function=get_image,
                ),
                "GetVideo": AbstractTool(
                    name="GetVideo",
                    description="Get video related to the topic.",
                    function=get_video,
                ),
                "CreateVerticalBarChart": VerticalBarChartTool(),
                "CreateLineChart": LineChartTool(),
                "CreatePieChart": PieChartTool(),
            },
        )
