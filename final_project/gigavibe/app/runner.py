from gigavibe.app.console import ConsoleAssistant
from gigavibe.config.setting_loader import load_settings
from gigavibe.service.llm_gateway import LLMGateway
from gigavibe.service.message import ConversationMemory


def run() -> int:
    settings = load_settings()
    backend = LLMGateway.from_settings(settings)
    memory = ConversationMemory(settings.limit_message, settings.limit_chars)
    assistant = ConsoleAssistant(settings.system_prompt, backend, memory)
    return assistant.run()