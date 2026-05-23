from pathlib import Path

import pytest

from gigavibe.service.attachments import (
    AttachmentError,
    expand_attachments,
    normalize_path,
    read_limited_text_file,
)


def test_normalize_path_relative(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert normalize_path('file.txt') == tmp_path / 'file.txt'


def test_read_limited_text_file(tmp_path: Path) -> None:
    path = tmp_path / 'file.txt'
    path.write_text('hello', encoding='utf-8')

    assert read_limited_text_file(path) == 'hello'


def test_read_limited_text_file_too_large(tmp_path: Path) -> None:
    path = tmp_path / 'big.txt'
    path.write_text('abcd', encoding='utf-8')

    with pytest.raises(AttachmentError):
        read_limited_text_file(path, max_size=1)


def test_expand_attachments(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / 'code.py'
    path.write_text('print(1)', encoding='utf-8')

    result, errors = expand_attachments('check @::code.py::')

    assert 'print(1)' in result
    assert errors == []


def test_expand_missing_attachment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    result, errors = expand_attachments('check @::missing.py::')

    assert '@::missing.py::' not in result
    assert errors