from gigavibe.dto.message import ChatMessage


class ConversationMemory:
    def __init__(self, limit_message: int | None, limit_chars: int | None) -> None:
        self.limit_message = limit_message
        self.limit_chars = limit_chars
        self._items: list[ChatMessage] = []

    def add_user_message(self, content: str) -> ChatMessage:
        message = ChatMessage('user', self._crop_left(content))
        self._trim_for(message)
        self._items.append(message)
        return message

    def add_assistant_message(self, content: str) -> None:
        message = ChatMessage('assistant', content)
        self._trim_for(message)
        self._items.append(message)

    def reset(self) -> None:
        self._items.clear()

    def list_messages(self) -> list[ChatMessage]:
        return list(self._items)

    def _crop_left(self, text: str) -> str:
        if self.limit_chars is None or len(text) <= self.limit_chars:
            return text
        return text[-self.limit_chars :]

    def _trim_for(self, next_message: ChatMessage) -> None:
        if self.limit_message is not None:
            while len(self._items) + 1 > self.limit_message and self._items:
                self._items.pop(0)

        if self.limit_chars is None:
            return

        total = sum(len(item.content) for item in self._items) + len(next_message.content)
        while self._items and total > self.limit_chars:
            removed = self._items.pop(0)
            total -= len(removed.content)


def messages_for_api(
    system_prompt: str | None,
    history: list[ChatMessage],
) -> list[dict[str, str]]:
    messages: list[ChatMessage] = []
    if system_prompt:
        messages.append(ChatMessage('system', system_prompt))
    messages.extend(history)
    return [message.as_dict() for message in messages]