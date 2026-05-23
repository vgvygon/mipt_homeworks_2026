from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_host: str
    model: str
    temperature: float
    limit_message: int | None
    limit_chars: int | None
    system_prompt: str | None
    stream: bool