"""User Profile Data Model."""


class UserProfile:
    """Data model for user profile information."""

    def __init__(self, name: str = None):
        self.name = name
