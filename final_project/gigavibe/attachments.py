from __future__ import annotations

import re
from pathlib import Path

MAX_FILE_SIZE = 5 * 1024 * 1024
FILE_PATTERN = re.compile(r'@::(.*?)::')


class AttachmentError(ValueError):
    pass


def normalize_path(path_text: str) -> Path:
    path = Path(path_text).expanduser()
    if path.is_absolute():
        return path
    return (Path.cwd() / path).resolve()


def read_limited_text_file(path: Path, max_size: int = MAX_FILE_SIZE) -> str:
    if not path.exists():
        raise AttachmentError(f'file not found: {path}')

    if not path.is_file():
        raise AttachmentError(f'not a file: {path}')

    try:
        size = path.stat().st_size
    except OSError as exc:
        raise AttachmentError(f'cannot read file info: {path}') from exc

    if size > max_size:
        raise AttachmentError(f'file is too large: {path}')

    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError as exc:
        raise AttachmentError(f'cannot read file: {path}') from exc


def expand_attachments(text: str, max_size: int = MAX_FILE_SIZE) -> tuple[str, list[str]]:
    errors: list[str] = []

    def replace(match: re.Match[str]) -> str:
        path_text = match.group(1).strip()

        if path_text == '':
            errors.append('empty file reference')
            return ''

        path = normalize_path(path_text)

        try:
            content = read_limited_text_file(path, max_size)
        except AttachmentError as exc:
            errors.append(str(exc))
            return ''

        return f'\n{content}'

    return FILE_PATTERN.sub(replace, text), errors
