"""
Semantic Kernel Bot implementation for handling conversations with an agent.
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

import jwt
from agents.abstract_agent import AbstractAgent
from botbuilder.core import ActivityHandler, ConversationState, MessageFactory, TurnContext, UserState
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus
from botbuilder.schema import ChannelAccount
from botframework.connector.auth.user_token_client import UserTokenClient
from data_models.conversation_data import ConversationData, ConversationTurn
from opentelemetry import trace

# from agents.semantic_kernel_agent import AbstractSemanticKernelAgent
from utils import get_activity_card

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class SemanticKernelBot(ActivityHandler):
    """
    Semantic Kernel Bot for handling conversations with an agent.
    """

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
        agent: AbstractAgent,
    ):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.conversation_data_accessor = self.conversation_state.create_property("ConversationData")
        self.user_profile_accessor = self.user_state.create_property("UserProfile")

        self.dialog = dialog
        self.welcome_message = os.getenv("LLM_WELCOME_MESSAGE", "Hello and welcome to the Semantic Kernel Bot Python!")
        self.agent = agent

        self.sso_enabled = os.getenv("SSO_ENABLED", False)
        if self.sso_enabled == "false":
            self.sso_enabled = False
        print(self.sso_enabled)
        self.sso_config_name = os.getenv("SSO_CONFIG_NAME", "default")

    async def on_turn(self, turn_context: TurnContext) -> None:
        """
        Handle a turn of conversation.

        Args:
            turn_context (TurnContext): The context for the current turn of conversation.

        """
        await super().on_turn(turn_context)

        # Save any state changes. The load happened during the execution of the Dialog.
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def handle_login(self, turn_context: TurnContext) -> bool:
        """
        Handle user login via Single Sign-On (SSO) if enabled.

        Args:
            turn_context (TurnContext): The context for the current turn of conversation.

        Returns:
            bool: True if the user is logged in, False otherwise.

        """
        if not self.sso_enabled:
            return True
        if turn_context.activity.text == "logout":
            await self.handle_logout(turn_context)
            return False

        user_profile_accessor = self.user_state.create_property("UserProfile")
        user_profile = await user_profile_accessor.get(turn_context, lambda: {})

        user_token_client = turn_context.turn_state.get(UserTokenClient.__name__, None)

        try:
            user_token = await user_token_client.get_user_token(
                turn_context.activity.from_property.id, self.sso_config_name, turn_context.activity.channel_id, None
            )
            decoded_token = jwt.decode(user_token.token, options={"verify_signature": False})
            user_profile["name"] = decoded_token.get("name")
            return True
        except Exception:
            dialog_set = DialogSet(self.conversation_state.create_property("DialogState"))
            dialog_set.add(self.dialog)
            dialog_context = await dialog_set.create_context(turn_context)
            results = await dialog_context.continue_dialog()
            if results.status == DialogTurnStatus.Empty:
                await dialog_context.begin_dialog(self.dialog.id)
            return False

    async def handle_logout(self, turn_context: TurnContext) -> None:
        """
        Handle user logout by clearing the user token.

        Args:
            turn_context (TurnContext): The context for the current turn of conversation.

        """
        user_token_client = turn_context.turn_state.get(UserTokenClient.__name__, None)
        await user_token_client.sign_out_user(
            turn_context.activity.from_property.id, self.sso_config_name, turn_context.activity.channel_id
        )
        await turn_context.send_activity("Signed out")

    async def send_interim_message(
        self, turn_context: TurnContext, interim_message: str, stream_sequence: Any, stream_id: str, stream_type: str
    ) -> Optional[str]:
        """
        Send an interim message to the user, either as a streaming message or an update.

        Args:
            turn_context (TurnContext): The context for the current turn of conversation.
            interim_message (str): The message to send.
            stream_sequence (Any): The stream sequence.
            stream_id (str): The ID of the message to update, if applicable.
            stream_type (str): The type of the stream ("typing" or "final").

        Returns:
            Optional[str]: The ID of the sent or updated message.

        """
        stream_supported = self.streaming and turn_context.activity.channel_id == "directline"
        update_supported = self.streaming and turn_context.activity.channel_id == "msteams"

        # If we can neither stream or update, return null
        if stream_type == "typing" and not stream_supported and not update_supported:
            return None

        # If we can update messages, do so
        if update_supported:
            if stream_id is None:
                create_activity = await turn_context.send_activity(interim_message)
                return create_activity.id
            else:
                update_message = MessageFactory.text(interim_message)
                update_message.id = stream_id
                update_message.type = "message"
                update_activity = await turn_context.update_activity(update_message)
                return update_activity.id
        # If we can stream messages, do so
        channel_data = {
            "streamId": stream_id,
            "streamSequence": stream_sequence,
            "streamType": "streaming" if stream_type == "typing" else "final",
        }
        message = MessageFactory.text(interim_message)
        message.channel_data = channel_data if stream_supported else None
        message.type = stream_type
        activity = await turn_context.send_activity(message)
        return activity.id

    # Modify onMembersAdded as needed
    async def on_members_added_activity(self, members_added: list[ChannelAccount], turn_context: TurnContext) -> None:
        """
        Handle members added to the conversation.

        Args:
            members_added (list[ChannelAccount]): List of members added to the conversation.
            turn_context (TurnContext): The context for the current turn of conversation.

        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(self.welcome_message)

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """
        Handle incoming message activities.

        Args:
            turn_context (TurnContext): The context for the current turn of conversation.

        """
        with tracer.start_as_current_span("on_message_activity") as span:
            span.set_attribute("activity_id", turn_context.activity.id)
            span.set_attribute("user_id", turn_context.activity.from_property.id)
            span.set_attribute("text", turn_context.activity.text)
            span.set_attribute("channel_id", turn_context.activity.channel_id)
            span.set_attribute("conversation_id", turn_context.activity.conversation.id)
            span.set_attribute("recipient_id", turn_context.activity.recipient.id)

            logger.info("Received message: %s", turn_context.activity.text)

            # Load conversation state
            conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData([]))

            # Add user message to history
            conversation_data.add_turn(
                ConversationTurn(role="user", content=turn_context.activity.text, created_at=datetime.now())
            )

            response = await self.agent.process(conversation_data)

            conversation_data.add_turn(response)

            logger.info("Agent response: %s", response)

            # Respond back to user
            await turn_context.send_activity(get_activity_card(response))
