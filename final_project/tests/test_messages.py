from gigavibe.messages import ChatMessage, ConversationMemory, messages_for_api


def test_messages_for_api_adds_system_prompt() -> None:
    history = [ChatMessage('user', 'hello')]
    result = messages_for_api('system', history)

    assert result == [
        {'role': 'system', 'content': 'system'},
        {'role': 'user', 'content': 'hello'},
    ]


def test_memory_trims_by_message_count() -> None:
    memory = ConversationMemory(limit_message=2, limit_chars=None)

    memory.add_user_message('one')
    memory.add_assistant_message('two')
    memory.add_user_message('three')

    assert [message.content for message in memory.list_messages()] == ['two', 'three']


def test_memory_trims_by_char_count() -> None:
    memory = ConversationMemory(limit_message=None, limit_chars=10)

    memory.add_user_message('123456')
    memory.add_assistant_message('abc')
    memory.add_user_message('zz')

    assert [message.content for message in memory.list_messages()] == ['abc', 'zz']


def test_memory_crops_long_user_message() -> None:
    memory = ConversationMemory(limit_message=None, limit_chars=3)

    memory.add_user_message('abcdef')

    assert memory.list_messages()[0].content == 'def'
