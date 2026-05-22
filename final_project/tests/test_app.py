from __future__ import annotations

from typing import Callable

from gigavibe.app import ConsoleAssistant
from gigavibe.messages import ConversationMemory


class FakeBackend:
    def __init__(self, answer: str = 'ok', stream: bool = False) -> None:
        self.answer = answer
        self.stream = stream

    def ask(
        self,
        messages: list[dict[str, str]],
        on_token: Callable[[str], None] | None = None,
    ) -> str:
        if self.stream and on_token is not None:
            on_token(self.answer)
        return self.answer


def test_build_chunk_prompt() -> None:
    memory = ConversationMemory(limit_message=10, limit_chars=100)
    assistant = ConsoleAssistant(None, FakeBackend(), memory)

    assert assistant._build_chunk_prompt('', 'chunk') == 'chunk'
    assert assistant._build_chunk_prompt('do it', 'chunk') == 'do it\n\nchunk'


def test_regular_message_adds_answer() -> None:
    memory = ConversationMemory(limit_message=10, limit_chars=100)
    assistant = ConsoleAssistant('system', FakeBackend('answer'), memory)

    assistant._handle_regular_message('hello')

    assert [message.content for message in memory.list_messages()] == ['hello', 'answer']


def test_regular_stream_message_adds_answer() -> None:
    memory = ConversationMemory(limit_message=10, limit_chars=100)
    assistant = ConsoleAssistant('system', FakeBackend('answer', stream=True), memory)

    assistant._handle_regular_message('hello')

    assert [message.content for message in memory.list_messages()] == ['hello', 'answer']
