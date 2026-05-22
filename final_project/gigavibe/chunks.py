from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from typing import Iterator, Literal

ChunkMode = Literal['paragraph', 'length']


@dataclass(frozen=True)
class ChunkCommand:
    mode: ChunkMode
    paragraph_count: int = 1
    chunk_length: int | None = None
    auto: bool = False


def parse_chunk_command(command: str) -> ChunkCommand:
    parts = shlex.split(command)
    if not parts or parts[0] not in {'/filechunk', '/file_chunk'}:
        raise ValueError('not a file chunk command')

    paragraph_count = 1
    chunk_length: int | None = None
    auto = False

    for part in parts[1:]:
        if part in {'-y', '--yes'}:
            auto = True
        elif part.startswith('paragraph='):
            if chunk_length is not None:
                raise ValueError('paragraph and len cannot be used together')
            paragraph_count = _positive_int(part.split('=', 1)[1], 'paragraph')
        elif part.startswith('len='):
            if paragraph_count != 1:
                raise ValueError('paragraph and len cannot be used together')
            chunk_length = _positive_int(part.split('=', 1)[1], 'len')
        else:
            raise ValueError(f'unknown option: {part}')

    if chunk_length is not None:
        return ChunkCommand('length', chunk_length=chunk_length, auto=auto)

    return ChunkCommand('paragraph', paragraph_count=paragraph_count, auto=auto)


def iter_chunks(text: str, command: ChunkCommand) -> Iterator[str]:
    if command.mode == 'length':
        length = command.chunk_length
        if length is None:
            return
        for index in range(0, len(text), length):
            yield text[index : index + length]
        return

    paragraphs = split_paragraphs(text)
    for index in range(0, len(paragraphs), command.paragraph_count):
        yield '\n\n'.join(paragraphs[index : index + command.paragraph_count])


def split_paragraphs(text: str) -> list[str]:
    stripped = text.strip()

    if stripped == '':
        return []

    parts = re.split(r'\n\s*\n', stripped)

    if len(parts) > 1:
        return [part.strip() for part in parts if part.strip()]

    return [line.strip() for line in stripped.splitlines() if line.strip()]


def _positive_int(value: str, name: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f'{name} must be an integer') from exc

    if number <= 0:
        raise ValueError(f'{name} must be positive')

    return number
