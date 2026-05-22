from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Protocol

from gigavibe.attachments import AttachmentError, expand_attachments, read_limited_text_file
from gigavibe.chunks import iter_chunks, parse_chunk_command
from gigavibe.llm_gateway import LLMGateway
from gigavibe.messages import ConversationMemory, messages_for_api
from gigavibe.settings import SettingsError, load_settings

QUIT_COMMAND = r'\q'
RESET_COMMAND = '/reset'
CHUNK_COMMANDS = ('/filechunk', '/file_chunk')
PROMPT = '> '

TokenPrinter = Callable[[str], None]


class ChatBackend(Protocol):
    @property
    def stream(self) -> bool:
        ...

    def ask(
        self,
        messages: list[dict[str, str]],
        on_token: TokenPrinter | None = None,
    ) -> str:
        ...


class ConsoleAssistant:
    def __init__(
        self,
        settings_system_prompt: str | None,
        backend: ChatBackend,
        memory: ConversationMemory,
    ) -> None:
        self.system_prompt = settings_system_prompt
        self.backend = backend
        self.memory = memory

    def run(self) -> int:
        print('GigaVibeMiptCode. Commands: \\q, /reset, /filechunk')

        while True:
            try:
                raw_text = input(PROMPT)
            except EOFError:
                print()
                return 0

            text = raw_text.strip()

            if text == '':
                continue

            if text == QUIT_COMMAND:
                print('Bye.')
                return 0

            if text == RESET_COMMAND:
                self._reset_chat()
                continue

            if text.startswith(CHUNK_COMMANDS):
                self._run_file_chunk_mode(text)
                continue

            self._handle_regular_message(raw_text)

    def _reset_chat(self) -> None:
        self.memory.reset()
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Chat was reset.')

    def _handle_regular_message(self, raw_text: str) -> None:
        prepared_text, errors = expand_attachments(raw_text)

        for error in errors:
            print(f'Attachment error: {error}')

        self.memory.add_user_message(prepared_text)
        messages = messages_for_api(self.system_prompt, self.memory.list_messages())

        answer = self._request(messages)

        if answer is None:
            return

        if not self.backend.stream:
            print(answer)

        self.memory.add_assistant_message(answer)

    def _run_file_chunk_mode(self, command_text: str) -> None:
        try:
            command = parse_chunk_command(command_text)
        except ValueError as exc:
            print(f'Invalid command: {exc}')
            return

        path_text = input('File path: ').strip()

        if path_text == QUIT_COMMAND:
            return

        prompt = input('Prompt for each chunk: ').strip()

        if prompt == QUIT_COMMAND:
            return

        path = Path(path_text).expanduser()

        try:
            file_text = read_limited_text_file(path)
        except AttachmentError as exc:
            print(f'File error: {exc}')
            return

        chunks = list(iter_chunks(file_text, command))

        if not chunks:
            print('No chunks found.')
            return

        for index, chunk in enumerate(chunks, start=1):
            chunk_prompt = self._build_chunk_prompt(prompt, chunk)
            answer = self._request(messages_for_api(self.system_prompt, []), chunk_prompt)

            if answer is None:
                return

            if not self.backend.stream:
                print(answer)

            if command.auto or index == len(chunks):
                continue

            next_value = input('Press Enter for next chunk or \\q to exit: ').strip()
            if next_value == QUIT_COMMAND:
                break

        print('File processing finished.')

    def _request(
        self,
        messages: list[dict[str, str]],
        chunk_prompt: str | None = None,
    ) -> str | None:
        if chunk_prompt is not None:
            messages = [*messages, {'role': 'user', 'content': chunk_prompt}]

        try:
            if self.backend.stream:
                result = self.backend.ask(messages, self._print_token)
                print()
                return result
            return self.backend.ask(messages)
        except KeyboardInterrupt:
            print('\nRequest was cancelled.')
            return None
        except Exception as exc:
            print(f'LLM error: {exc}')
            return None

    @staticmethod
    def _print_token(text: str) -> None:
        print(text, end='', flush=True)

    @staticmethod
    def _build_chunk_prompt(prompt: str, chunk: str) -> str:
        if prompt.strip() == '':
            return chunk
        return f'{prompt.strip()}\n\n{chunk}'


def run() -> int:
    try:
        settings = load_settings()
    except SettingsError as exc:
        print(f'Config error: {exc}')
        return 1

    try:
        backend = LLMGateway.from_settings(settings)
    except Exception as exc:
        print(f'Cannot initialize LLM client: {exc}')
        return 1

    memory = ConversationMemory(settings.limit_message, settings.limit_chars)
    assistant = ConsoleAssistant(settings.system_prompt, backend, memory)

    return assistant.run()
