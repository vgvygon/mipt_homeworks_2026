from gigavibe.app.protocols import ChatBackend


def request_completion(
    backend: ChatBackend,
    messages: list[dict[str, str]],
    chunk_prompt: str | None = None,
) -> str | None:
    if chunk_prompt is not None:
        messages = [*messages, {'role': 'user', 'content': chunk_prompt}]

    try:
        if backend.stream:
            result = backend.ask(messages, print_token)
            print()
            return result
        return backend.ask(messages)
    except KeyboardInterrupt:
        print('\nRequest was cancelled.')
        return None
    except Exception as exc:
        print(f'LLM error: {exc}')
        return None


def print_token(text: str) -> None:
    print(text, end='', flush=True)