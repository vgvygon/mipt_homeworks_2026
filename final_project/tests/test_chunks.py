import pytest

from gigavibe.service.chunks import iter_chunks, parse_chunk_command, split_paragraphs


def test_parse_default_chunk_command() -> None:
    command = parse_chunk_command('/filechunk')

    assert command.mode == 'paragraph'
    assert command.paragraph_count == 1
    assert command.auto is False


def test_parse_length_command() -> None:
    command = parse_chunk_command('/filechunk len=3 -y')

    assert command.mode == 'length'
    assert command.chunk_length == 3
    assert command.auto is True


def test_parse_invalid_command() -> None:
    with pytest.raises(ValueError):
        parse_chunk_command('/filechunk len=0')


def test_iter_length_chunks() -> None:
    command = parse_chunk_command('/filechunk len=2')

    assert list(iter_chunks('abcdef', command)) == ['ab', 'cd', 'ef']


def test_iter_paragraph_chunks() -> None:
    command = parse_chunk_command('/filechunk paragraph=2')

    assert list(iter_chunks('one\n\ntwo\n\nthree', command)) == ['one\n\ntwo', 'three']


def test_split_paragraphs_fallback_to_lines() -> None:
    assert split_paragraphs('one\ntwo\n') == ['one', 'two']