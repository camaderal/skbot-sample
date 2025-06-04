"""Tools for creating media attachments."""

from data_models.attachments import Media
from tools import AbstractTool


class MediaTool(AbstractTool):
    """Tool for creating media attachments."""

    def __init__(
        self,
        name: str = "CreateMediaAttachment",
        description: str = "Generate a media attachment. The media would be included automatically in the response.",
    ):
        super().__init__(name=name, description=description, function=self.create_media_attachment)

    @staticmethod
    def create_media_attachment(url: str, mime_type: str, label: str) -> Media:
        """
        Create a media attachment with the given URL, MIME type, and label.

        Args:
            url (str): The URL of the media.
            mime_type (str): The MIME type of the media.
            label (str): A label for the media.

        Returns:
            Media: An instance of Media containing the media attachment.

        """
        return Media(
            content=url,
            mime_type=mime_type,
            label=label,
        )
