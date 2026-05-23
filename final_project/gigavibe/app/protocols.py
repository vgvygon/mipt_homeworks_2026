from typing import Callable, Protocol

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