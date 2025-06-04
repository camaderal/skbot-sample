"""
Main application entry point for the Semantic Kernel Chatbot.
"""

import logging
import os
import sys
import traceback
from datetime import datetime
from trace.otel_configuration import OtelConfiguration

from agents.chat_completion_agents.math_chat_completion_agent import MathSemanticKernelAgent
from aiohttp import web
from aiohttp.web import Request, Response
from azure.identity import DefaultAzureCredential
from botbuilder.azure import (
    CosmosDbPartitionedConfig,
    CosmosDbPartitionedStorage,
)
from botbuilder.core import (
    ConversationState,
    MemoryStorage,
    TurnContext,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity, ActivityTypes
from bots import SemanticKernelBot
from config import DefaultConfig
from dialogs import LoginDialog
from dotenv import load_dotenv

load_dotenv()
CONFIG = DefaultConfig()
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))

# Setup logging and tracing
OtelConfiguration.configure()

# Create logger
logger = logging.getLogger(__name__)


async def on_error(context: TurnContext, error: Exception) -> None:
    """
    Catch-all for errors in the bot.

    Args:
        context (TurnContext): The context for the current turn of conversation with the user.
        error (Exception): The exception that was thrown.

    """
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity("To continue to run this bot, please fix the bot source code.")
    await context.send_activity(str(error))

    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

# Set up service authentication
credential = DefaultAzureCredential(managed_identity_client_id=os.getenv("MicrosoftAppId"))

# Conversation history storage
storage = None
if os.getenv("AZURE_COSMOSDB_ENDPOINT"):
    storage = CosmosDbPartitionedStorage(
        CosmosDbPartitionedConfig(
            cosmos_db_endpoint=os.getenv("AZURE_COSMOSDB_ENDPOINT"),
            database_id=os.getenv("AZURE_COSMOSDB_DATABASE_ID"),
            container_id=os.getenv("AZURE_COSMOSDB_CONTAINER_ID"),
            auth_key=os.getenv("AZURE_COSMOSDB_AUTH_KEY"),
        )
    )
    # storage.client = CosmosClient(os.getenv("AZURE_COSMOSDB_ENDPOINT"), auth=credential)
else:
    storage = MemoryStorage()

# Create conversation and user state
user_state = UserState(storage)
conversation_state = ConversationState(storage)

# Create the Bot
dialog = LoginDialog()
BOT = SemanticKernelBot(conversation_state, user_state, dialog, MathSemanticKernelAgent())


async def messages(req: Request) -> Response:
    """
    Handle incoming messages from the Bot Framework.

    Args:
        req (Request): The incoming request containing the activity.

    Returns:
        Response: The response to the incoming request.

    """
    return await ADAPTER.process(req, BOT)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        logger.info("Starting Semantic Kernel Chatbot...")
        web.run_app(APP, host="0.0.0.0", port=CONFIG.PORT)
    except Exception as error:
        raise error
