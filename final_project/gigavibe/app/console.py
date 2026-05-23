import os

from gigavibe.app.chunk_mode import run_file_chunk_mode
from gigavibe.app.commands import CHUNK_COMMANDS, PROMPT, QUIT_COMMAND, RESET_COMMAND
from gigavibe.app.protocols import ChatBackend
from gigavibe.app.request import request_completion
from gigavibe.service.attachments import expand_attachments
from gigavibe.service.message import ConversationMemory, messages_for_api


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
                run_file_chunk_mode(text, self.system_prompt, self.backend)
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

        answer = request_completion(self.backend, messages)

        if answer is None:
            return

        if not self.backend.stream:
            print(answer)

        self.memory.add_assistant_message(answer)