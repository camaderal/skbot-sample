"""
Defines the AbstractChatCompletionAgent class and its associated methods.
"""

import inspect
import logging
import os
from abc import ABC
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from agents.abstract_agent import AbstractAgent
from azure.identity import ManagedIdentityCredential, get_bearer_token_provider
from data_models.conversation_data import ConversationData, ConversationTurn
from dotenv import load_dotenv
from openai.lib.azure import AsyncAzureOpenAI
from opentelemetry import trace
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions.kernel_function_from_method import KernelFunctionFromMethod
from semantic_kernel.functions.kernel_plugin import KernelPlugin
from tools import Tool
from utils import extract_attachments

load_dotenv(override=True)

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

# Static variables
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_BASE_URL = os.environ.get("AZURE_OPENAI_BASE_URL")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

# Set up the bearer token provider for MID authentication
token_provider = get_bearer_token_provider(
    ManagedIdentityCredential(client_id=AZURE_CLIENT_ID), "https://cognitiveservices.azure.com/.default"
)
agent_invoke_context: ContextVar[dict] = ContextVar("agent_invoke_context")


class AbstractChatCompletionAgent(AbstractAgent, ABC):
    """
    AbstractChatCompletionAgent is a specialized agent that integrates Semantic Kernel capabilities.

    This class provides methods to configure and utilize chat completion and text embedding services,
    as well as manage chat history and tool usage.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        prompt: str,
        tools: dict[str, Tool],
        settings: dict[str, Any] = None,
    ):
        """
        Initialize the AbstractChatCompletionAgent instance.

        Args:
            agent_id (str): Unique identifier for the agent.
            name (str): Name of the agent.
            description (str): Description of the agent.
            prompt (str): Initial prompt for the agent.
            tools (dict[str, Tool]): Dictionary of tools available to the agent.
            settings (dict[str, Any], optional): Optional settings for the agent.

        Raises:
            Exception: If the environment is not supported.

        """
        super().__init__(agent_id, name, description, prompt, tools, settings)

        # Create a semantic kernel
        self._kernel = Kernel()

        # Allow the kernel to use chat completion service
        if ENVIRONMENT == "local":
            async_openai_client = AsyncAzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_BASE_URL,
                api_version=AZURE_OPENAI_API_VERSION,
            )
        elif ENVIRONMENT == "demo" or ENVIRONMENT == "sandbox":
            async_openai_client = AsyncAzureOpenAI(
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_BASE_URL,
                azure_ad_token_provider=token_provider,
            )
        else:
            raise Exception("Invalid environment. Please set the environment to 'local', 'demo', or 'sandbox'.")

        # Create the chat completion service with the async client
        chat_completion = AzureChatCompletion(
            async_client=async_openai_client,
            service_id=agent_id,
        )
        self._kernel.add_service(chat_completion)

        # Add the plugin
        if tools:
            self._add_plugin(tools)

        execution_settings = self._kernel.get_prompt_execution_settings_from_service_id(service_id=agent_id)
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        if settings:
            if "maximum_auto_invoke_attempts" in settings:
                execution_settings.function_choice_behavior.maximum_auto_invoke_attempts = int(
                    settings["maximum_auto_invoke_attempts"]
                )

        # Create the agent
        self._agent = ChatCompletionAgent(
            id=agent_id,
            kernel=self._kernel,
            arguments=KernelArguments(settings=execution_settings),
            name=agent_id,
            instructions=prompt,
        )

    def _add_plugin(self, tools: dict[str, Tool]) -> None:
        """
        Add a plugin to the kernel using the provided tools.

        Args:
            tools (dict[str, Tool]): Dictionary of tools to add as plugins.

        """
        functions = []
        for tool in tools.values():
            build_func = self._build_func(tool)

            function = KernelFunctionFromMethod(
                method=kernel_function(build_func, tool.name, tool.description), plugin_name=tool.name
            )
            functions.append(function)

        self._kernel.add_plugin(KernelPlugin(name="plugin", functions=functions))

    def _build_func(self, tool: Tool) -> Any:
        """
        Build a function for the given tool.

        Args:
            tool (Tool): The tool to build the function for.

        Returns:
            Any: The built function.

        """

        async def new_plugin_func(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(f"{tool.name}_execute") as span:
                span.set_attribute("tool_name", tool.name)
                span.set_attribute("tool_description", tool.description)
                span.set_attribute("args", args)
                span.set_attributes(kwargs)

                resp = None

                start_time = datetime.now()
                if inspect.iscoroutinefunction(tool.function):
                    resp = await tool.function(*args, **kwargs)
                else:
                    resp = tool.function(*args, **kwargs)
                end_time = datetime.now()
                elapsed_time = end_time - start_time

                tool_usage = agent_invoke_context.get()["tool_usage"]
                tool_usage.append(
                    {
                        "tool_name": tool.name,
                        "args": args,
                        "kwargs": kwargs,
                        "result": resp,
                        "start_time": start_time.isoformat(),
                        "duration": elapsed_time.microseconds,
                    }
                )

                attachments = extract_attachments(resp)
                if attachments:
                    agent_invoke_context.get()["attachments"].extend(attachments)

                return resp

        # Update the signature of the new function
        plugin_func = kernel_function(tool.function, tool.name, tool.description)
        signature = inspect.signature(plugin_func)
        new_plugin_func.__signature__ = signature  # type: ignore[attr-defined]

        return new_plugin_func

    async def process(self, conversation_data: ConversationData) -> ConversationTurn:
        """
        Process a user message and generate a response using the agent.

        Args:
            conversation_data (ConversationData): The conversation data containing the history and current message.

        Returns:
            ConversationTurn: A turn representing the agent's response, including any tool usage and attachments.

        """
        with tracer.start_as_current_span("chat_completion_agent_process") as span:
            span.set_attribute("agent_id", self.id)
            span.set_attribute("name", self.name)

            token = agent_invoke_context.set(
                {
                    "tool_usage": [],
                    "attachments": [],
                }
            )

            history = ChatHistory()
            for message in conversation_data.history:
                if message.role == "user":
                    history.add_user_message(message.content)
                else:
                    history.add_assistant_message(message.content)

            response = await self._agent.get_response(
                history=history,
            )

            ctx = agent_invoke_context.get()
            agent_invoke_context.reset(token)

            turn = ConversationTurn(
                role="assistant",
                content=response.content,
                created_at=datetime.now(),
                metadata={"tool_usage": ctx["tool_usage"]},
                attachments=ctx["attachments"],
            )

            return turn
