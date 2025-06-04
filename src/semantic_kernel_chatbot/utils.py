"""
Utility functions.
"""

import json
import logging
from typing import Any

from botbuilder.core import CardFactory
from botbuilder.schema import Activity, ActivityTypes, Attachment
from data_models.attachments import Chart, Citation, LineChart, Media, PieChart, VerticalBarChart
from data_models.conversation_data import ConversationTurn

logger = logging.getLogger(__name__)


def extract_attachments(result: Any) -> list[Any]:
    """
    Extracts attachments from the result object.

    Args:
        result (Any): The result object from which to extract attachments.

    Returns:
       list[Any]: A list containing attachments categorized by their type.

    """
    attachments = []

    def _collect(value: Any) -> None:
        if isinstance(value, Citation) or isinstance(value, Media) or isinstance(value, Chart):
            attachments.append(value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                _collect(item)
        elif isinstance(value, dict):
            for item in value.values():
                _collect(item)

    _collect(result)
    return attachments


def get_citations_element(citation: Citation) -> Attachment:
    """
    Generates an Adaptive Card for displaying citations.

    Args:
        citation (Citation): The citation object.

    Returns:
        Attachment: An Attachment object.

    """
    return {
        "type": "Container",
        "items": [
            {
                "type": "TextBlock",
                "text": f"[{citation.title}]({citation.url})",
                "wrap": True,
                "size": "Medium",
            },
            {
                "type": "CodeBlock",
                "codeSnippet": (json.dumps(citation.metadata) if citation.metadata else ""),
                "language": "Json",
            },
        ],
    }


def get_media_element(media: Media) -> Attachment:
    """
    Generates an Adaptive Card for displaying media attachments.

    Args:
        media (Media): The media object containing the content and metadata.

    Returns:
        Attachment: An Attachment object containing the Adaptive Card with media information.

    """
    return {
        "type": "Media",
        "sources": [
            {
                "mimeType": media.mime_type,
                "url": media.content,
                "label": media.label or "Media Attachment",
            }
        ],
    }


def get_chart_card(chart: Chart) -> Attachment:
    """
    Generates an Adaptive Card for displaying charts.

    Args:
        chart (Chart): The chart object containing the title, data, and type.

    Returns:
        Attachment: An Attachment object containing the Adaptive Card with chart information.

    Raises:
        ValueError: If the chart type is unsupported.

    """
    type = ""
    if isinstance(chart, VerticalBarChart):
        type = "Chart.VerticalBar"
    elif isinstance(chart, LineChart):
        type = "Chart.Line"
    elif isinstance(chart, PieChart):
        type = "Chart.Pie"

    if not type:
        raise ValueError("Unsupported chart type")

    return {
        "id": chart.id,
        "type": type,
        "title": chart.title,
        "data": [data.model_dump(mode="json") for data in chart.data] if chart.data else [],
    }


def get_expandable_block(id: str, title: str, elements: list[Any]) -> dict[str, Any]:
    """
    Generates an expandable block for Adaptive Cards.

    Args:
        id (str): Unique identifier for the block.
        title (str): Title of the block.
        elements (list[Any]): List of elements to be included in the block.

    Returns:
        dict[str, Any]: A dictionary representing the expandable block structure.

    """
    return {
        "type": "Container",
        "items": [
            {
                "type": "ColumnSet",
                "columns": [
                    {
                        "type": "Column",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": title,
                                "wrap": True,
                                "size": "Medium",
                            }
                        ],
                        "width": "stretch",
                    },
                    {
                        "type": "Column",
                        "id": f"chevronDown{id}",
                        "spacing": "Small",
                        "verticalContentAlignment": "Center",
                        "items": [
                            {
                                "type": "Image",
                                "url": "https://adaptivecards.io/content/down.png",
                                "width": "20px",
                                "altText": "collapsed",
                            }
                        ],
                        "width": "auto",
                        "isVisible": False,
                    },
                    {
                        "type": "Column",
                        "id": f"chevronUp{id}",
                        "spacing": "Small",
                        "verticalContentAlignment": "Center",
                        "items": [
                            {
                                "type": "Image",
                                "url": "https://adaptivecards.io/content/up.png",
                                "width": "20px",
                                "altText": "expanded",
                            }
                        ],
                        "width": "auto",
                    },
                ],
                "selectAction": {
                    "type": "Action.ToggleVisibility",
                    "targetElements": [
                        f"cardContent{id}",
                        f"chevronUp{id}",
                        f"chevronDown{id}",
                    ],
                },
            },
            {
                "type": "Container",
                "id": f"cardContent{id}",
                "items": [
                    {
                        "type": "Container",
                        "fallback": {
                            "type": "TextBlock",
                            "text": "The elements for this block aren't supported.",
                            "wrap": True,
                        },
                        "items": elements,
                    }
                ],
                "isVisible": False,
            },
        ],
        "separator": True,
        "spacing": "Small",
    }


def get_activity_card(turn: ConversationTurn) -> Activity:
    """
    Generates an Activity card for a conversation turn.

    Args:
        turn (ConversationTurn): The conversation turn containing the content and attachments.

    Returns:
        Activity: An Activity object containing the card with the conversation turn details.

    """
    citations = []
    media = []
    charts = []

    for attachment in turn.attachments:
        if isinstance(attachment, Citation):
            citations.append(get_citations_element(attachment))
        elif isinstance(attachment, Media):
            media.append(get_media_element(attachment))
        elif isinstance(attachment, Chart):
            charts.append(get_chart_card(attachment))

    attachments_body = []
    if citations:
        attachments_body.append(get_expandable_block("Citations", "Citations", citations))
    if media:
        attachments_body.append(get_expandable_block("Media", "Media Attachments", media))
    if charts:
        attachments_body.append(get_expandable_block("Charts", "Charts", charts))

    attachments_card = {
        "type": "AdaptiveCard",
        "body": attachments_body,
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "fallbackText": "This card requires Adaptive Cards v1.2 support to be rendered properly.",
    }

    logger.info("Generated Adaptive Card: %s", attachments_card)

    return Activity(
        type=ActivityTypes.message,
        text=turn.content,
        attachments=([CardFactory.adaptive_card(attachments_card)] if (citations or media or charts) else None),
    )
