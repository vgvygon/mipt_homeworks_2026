import importlib
from dataclasses import dataclass
from typing import Any, Callable, cast

from gigavibe.dto.settings import Settings

TokenPrinter = Callable[[str], None]


@dataclass(frozen=True)
class LLMGateway:
    client: Any
    model: str
    temperature: float
    stream: bool

    @classmethod
    def from_settings(cls, settings: Settings) -> 'LLMGateway':
        openai_module: Any = importlib.import_module('openai')
        openai_class = openai_module.OpenAI
        client = openai_class(api_key=settings.api_key, base_url=settings.api_host)

        return cls(
            client=client,
            model=settings.model,
            temperature=settings.temperature,
            stream=settings.stream,
        )

    def ask(
        self,
        messages: list[dict[str, str]],
        on_token: TokenPrinter | None = None,
    ) -> str:
        if self.stream:
            return self._ask_stream(messages, on_token)
        return self._ask_plain(messages)

    def _ask_plain(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        content = response.choices[0].message.content
        return cast(str, content or '')

    def _ask_stream(
        self,
        messages: list[dict[str, str]],
        on_token: TokenPrinter | None,
    ) -> str:
        events = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            stream=True,
        )

        answer_parts: list[str] = []

        for event in events:
            content = event.choices[0].delta.content
            if not content:
                continue

            answer_parts.append(content)

            if on_token is not None:
                on_token(content)

        return ''.join(answer_parts)