from pathlib import Path

from gigavibe.app.commands import QUIT_COMMAND
from gigavibe.app.protocols import ChatBackend
from gigavibe.app.request import request_completion
from gigavibe.service.attachments import AttachmentError, read_limited_text_file
from gigavibe.service.chunks import iter_chunks, parse_chunk_command
from gigavibe.service.message import messages_for_api


def run_file_chunk_mode(
    command_text: str,
    system_prompt: str | None,
    backend: ChatBackend,
) -> None:
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

    chunk_iterator = iter(iter_chunks(file_text, command))

    try:
        current_chunk = next(chunk_iterator)
    except StopIteration:
        print('No chunks found.')
        return

    while True:
        try:
            next_chunk = next(chunk_iterator)
            has_next = True
        except StopIteration:
            next_chunk = ''
            has_next = False

        chunk_prompt = build_chunk_prompt(prompt, current_chunk)
        answer = request_completion(
            backend,
            messages_for_api(system_prompt, []),
            chunk_prompt,
        )

        if answer is None:
            return

        if not backend.stream:
            print(answer)

        if not command.auto and has_next:
            next_value = input('Press Enter for next chunk or \\q to exit: ').strip()
            if next_value == QUIT_COMMAND:
                break

        if not has_next:
            break

        current_chunk = next_chunk

    print('File processing finished.')


def build_chunk_prompt(prompt: str, chunk: str) -> str:
    if prompt.strip() == '':
        return chunk
    return f'{prompt.strip()}\n\n{chunk}'