import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from gigavibe.dto.settings import Settings

DEFAULT_MODEL = 'gpt-3.5-turbo'
CONFIG_FILE = 'config.yaml'

ENV_KEYS = (
    'API_KEY',
    'API_HOST',
    'MODEL',
    'LIMIT_MESSAGE',
    'LIMIT_CHARS',
    'TEMPERATURE',
    'STREAM',
)


class SettingsError(ValueError):
    pass


def load_settings(path: Path | None = None) -> Settings:
    load_dotenv()

    config_path = path or Path(CONFIG_FILE)
    yaml_data = _read_yaml(config_path) if config_path.is_file() else {}
    has_env = any(os.environ.get(key) is not None for key in ENV_KEYS)

    if not config_path.is_file() and not has_env:
        raise SettingsError('Create config.yaml or set environment variables.')

    api_key = _read_required_str('API_KEY', 'api_key', yaml_data)
    api_host = _read_required_str('API_HOST', 'api_host', yaml_data)
    model = _read_optional_str('MODEL', 'model', yaml_data) or DEFAULT_MODEL
    temperature = _read_float('TEMPERATURE', 'temperature', yaml_data, 0.7)
    limit_message = _read_optional_int('LIMIT_MESSAGE', 'limit_message', yaml_data)
    limit_chars = _read_optional_int('LIMIT_CHARS', 'limit_chars', yaml_data)
    system_prompt = _read_optional_str(None, 'system_prompt', yaml_data)
    stream = _read_bool('STREAM', 'stream', yaml_data, False)

    if not 0 <= temperature <= 1:
        raise SettingsError('temperature must be between 0 and 1.')

    if limit_message is not None and limit_message <= 0:
        raise SettingsError('limit_message must be positive.')

    if limit_chars is not None and limit_chars <= 0:
        raise SettingsError('limit_chars must be positive.')

    if limit_message is None and limit_chars is None:
        raise SettingsError('Set limit_message, limit_chars, or both.')

    return Settings(
        api_key=api_key,
        api_host=api_host,
        model=model,
        temperature=temperature,
        limit_message=limit_message,
        limit_chars=limit_chars,
        system_prompt=system_prompt,
        stream=stream,
    )


def _read_yaml(path: Path) -> dict[str, object]:
    try:
        data: Any = yaml.safe_load(path.read_text(encoding='utf-8'))
    except OSError as exc:
        raise SettingsError(f'Cannot read config file: {path}') from exc
    except yaml.YAMLError as exc:
        raise SettingsError(f'Invalid yaml file: {path}') from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise SettingsError('config.yaml must contain a mapping.')

    result: dict[str, object] = {}
    for key, value in data.items():
        if isinstance(key, str):
            result[key] = value
    return result


def _read_raw(
    env_name: str | None,
    yaml_name: str,
    yaml_data: dict[str, object],
) -> object | None:
    if env_name is not None:
        env_value = os.environ.get(env_name)
        if env_value is not None:
            return env_value
    return yaml_data.get(yaml_name)


def _read_optional_str(
    env_name: str | None,
    yaml_name: str,
    yaml_data: dict[str, object],
) -> str | None:
    raw = _read_raw(env_name, yaml_name, yaml_data)

    if raw is None:
        return None

    if not isinstance(raw, str):
        raise SettingsError(f'{yaml_name} must be a string.')

    value = raw.strip()
    if value == '':
        return None
    return value


def _read_required_str(
    env_name: str,
    yaml_name: str,
    yaml_data: dict[str, object],
) -> str:
    value = _read_optional_str(env_name, yaml_name, yaml_data)
    if value is None:
        raise SettingsError(f'{yaml_name} is required.')
    return value


def _read_float(
    env_name: str,
    yaml_name: str,
    yaml_data: dict[str, object],
    default: float,
) -> float:
    raw = _read_raw(env_name, yaml_name, yaml_data)

    if raw is None:
        return default

    if isinstance(raw, bool):
        raise SettingsError(f'{yaml_name} must be a number.')

    if isinstance(raw, (int, float, str)):
        try:
            return float(raw)
        except ValueError as exc:
            raise SettingsError(f'{yaml_name} must be a number.') from exc

    raise SettingsError(f'{yaml_name} must be a number.')


def _read_optional_int(
    env_name: str,
    yaml_name: str,
    yaml_data: dict[str, object],
) -> int | None:
    raw = _read_raw(env_name, yaml_name, yaml_data)

    if raw is None:
        return None

    if isinstance(raw, bool):
        raise SettingsError(f'{yaml_name} must be an integer.')

    if isinstance(raw, int):
        return raw

    if isinstance(raw, str):
        value = raw.strip()
        if value == '':
            return None
        try:
            return int(value)
        except ValueError as exc:
            raise SettingsError(f'{yaml_name} must be an integer.') from exc

    raise SettingsError(f'{yaml_name} must be an integer.')


def _read_bool(
    env_name: str,
    yaml_name: str,
    yaml_data: dict[str, object],
    default: bool,
) -> bool:
    raw = _read_raw(env_name, yaml_name, yaml_data)

    if raw is None:
        return default

    if isinstance(raw, bool):
        return raw

    if isinstance(raw, str):
        value = raw.strip().lower()
        if value in {'1', 'true', 'yes', 'y', 'on'}:
            return True
        if value in {'0', 'false', 'no', 'n', 'off'}:
            return False

    raise SettingsError(f'{yaml_name} must be a boolean.')