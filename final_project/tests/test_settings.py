from pathlib import Path

import pytest

from gigavibe.settings import SettingsError, load_settings

ENV_NAMES = (
    'API_KEY',
    'API_HOST',
    'MODEL',
    'LIMIT_MESSAGE',
    'LIMIT_CHARS',
    'TEMPERATURE',
    'STREAM',
)


@pytest.fixture(autouse=True)
def clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / 'config.yaml'
    path.write_text(text, encoding='utf-8')
    return path


def test_load_settings_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = write_config(
        tmp_path,
        """
api_key: key
api_host: http://localhost:11434/v1/
model: model
temperature: 0.4
limit_message: 10
limit_chars: 100
system_prompt: hello
stream: true
""",
    )
    monkeypatch.chdir(tmp_path)

    settings = load_settings(path)

    assert settings.api_key == 'key'
    assert settings.model == 'model'
    assert settings.temperature == pytest.approx(0.4)
    assert settings.stream is True


def test_env_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = write_config(
        tmp_path,
        """
api_key: yaml-key
api_host: http://localhost:11434/v1/
limit_message: 10
temperature: 0.4
""",
    )
    monkeypatch.setenv('API_KEY', 'env-key')
    monkeypatch.setenv('MODEL', 'env-model')

    settings = load_settings(path)

    assert settings.api_key == 'env-key'
    assert settings.model == 'env-model'


def test_missing_config_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SettingsError):
        load_settings()


def test_bad_temperature_raises(tmp_path: Path) -> None:
    path = write_config(
        tmp_path,
        """
api_key: key
api_host: http://localhost:11434/v1/
temperature: 2
limit_message: 10
""",
    )

    with pytest.raises(SettingsError):
        load_settings(path)
