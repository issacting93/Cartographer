"""
Adapter that wraps the Anthropic async SDK to match the OpenAI
client.chat.completions.create() interface used by the Atlas pipeline.
"""

import anthropic


class _Message:
    """Mimics openai.types.chat.ChatCompletionMessage."""
    def __init__(self, content: str):
        self.content = content


class _Choice:
    """Mimics openai.types.chat.ChatCompletionChoice."""
    def __init__(self, content: str):
        self.message = _Message(content)


class _Response:
    """Mimics openai.types.chat.ChatCompletion."""
    def __init__(self, content: str):
        self.choices = [_Choice(content)]


class _ChatCompletions:
    """Mimics client.chat.completions with a .create() async method."""

    def __init__(self, client: anthropic.AsyncAnthropic):
        self._client = client

    async def create(self, *, model: str, messages: list, temperature: float = 0.0,
                     max_tokens: int = 300, **kwargs) -> _Response:
        # Separate system message from user/assistant messages
        system_text = ""
        api_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_text += msg["content"] + "\n"
            else:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Ensure messages alternate and start with user
        if not api_messages or api_messages[0]["role"] != "user":
            api_messages.insert(0, {"role": "user", "content": "Please respond to the system instructions above."})

        response = await self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_text.strip() if system_text.strip() else "You are a helpful assistant.",
            messages=api_messages,
        )

        # Extract text from content blocks
        text = "".join(block.text for block in response.content if block.type == "text")
        return _Response(text)


class _Chat:
    """Mimics client.chat namespace."""
    def __init__(self, client: anthropic.AsyncAnthropic):
        self.completions = _ChatCompletions(client)


class AsyncAnthropicOpenAIAdapter:
    """
    Drop-in replacement for AsyncOpenAI that routes calls to Anthropic.

    Usage:
        client = AsyncAnthropicOpenAIAdapter(api_key="sk-ant-...")
        response = await client.chat.completions.create(
            model="claude-haiku-4-5-20251001",
            messages=[...],
        )
        text = response.choices[0].message.content
    """

    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)
        self.chat = _Chat(self._client)


class _SyncChatCompletions:
    """Mimics client.chat.completions with a .create() sync method."""

    def __init__(self, client: anthropic.Anthropic):
        self._client = client

    def create(self, *, model: str, messages: list, temperature: float = 0.0,
               max_tokens: int = 300, **kwargs) -> _Response:
        # Separate system message from user/assistant messages
        system_text = ""
        api_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_text += msg["content"] + "\n"
            else:
                api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Ensure messages alternate and start with user
        if not api_messages or api_messages[0]["role"] != "user":
            api_messages.insert(0, {"role": "user", "content": "Please respond to the system instructions above."})

        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_text.strip() if system_text.strip() else "You are a helpful assistant.",
            messages=api_messages,
        )

        # Extract text from content blocks
        text = "".join(block.text for block in response.content if block.type == "text")
        return _Response(text)


class _SyncChat:
    """Mimics client.chat namespace for sync client."""
    def __init__(self, client: anthropic.Anthropic):
        self.completions = _SyncChatCompletions(client)


class AnthropicOpenAIAdapter:
    """
    Drop-in replacement for synchronous OpenAI client that routes calls to Anthropic.
    """

    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)
        self.chat = _SyncChat(self._client)
