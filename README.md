# Semantic Kernel Chatbot Sample

This repository contains a Python implementation of a chatbot that integrates [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) with the Bot Framework. The project demonstrates how to build an agent capable of handling natural language requests, invoking tools, and returning results in Adaptive Cards.

## Key Concepts

- **Application entry point** – `src/semantic_kernel_chatbot/app.py` sets up an `aiohttp` web server to receive Bot Framework activities. It configures authentication, conversation state storage, OpenTelemetry tracing and creates the bot instance.
- **Bot implementation** – `SemanticKernelBot` in `src/semantic_kernel_chatbot/bots/semantic_kernel_bot.py` manages user conversations. It tracks conversation history, handles single sign‑on login and delegates message processing to an agent.
- **Agents** – The `agents` package contains an abstract chat completion agent implemented with Semantic Kernel. The example `MathSemanticKernelAgent` (`src/semantic_kernel_chatbot/agents/chat_completion_agents/math_chat_completion_agent.py`) exposes tools for arithmetic operations, chart creation and simple web lookup helpers.
- **Tools** – Utility classes under `src/semantic_kernel_chatbot/tools` provide functionality that an agent can invoke, such as math operators, chart generators and media retrieval.
- **Data models** – Pydantic models in `src/semantic_kernel_chatbot/data_models` define conversation turns, attachments (citations, media and charts) and user profile information.
- **Dialogs** – The `dialogs` package includes a login dialog enabling OAuth sign‑in when single sign‑on is configured.
- **Tracing and logging** – The `trace` package configures OpenTelemetry and logging, allowing telemetry to be sent to Azure Monitor when connection information is present.

## Development

The project targets Python 3.10. Development container definitions are provided under `.devcontainer`. Formatting, linting and type checks are configured via `pyproject.toml` and can be executed with `make check-all`.

To install dependencies locally:

```bash
pip install -r requirements.txt
```

To run the bot during development:

```bash
python -m semantic_kernel_chatbot.app
```

This will start an `aiohttp` server listening on port 3978 by default. You can then connect to it using the Bot Framework Emulator or a Direct Line channel.
