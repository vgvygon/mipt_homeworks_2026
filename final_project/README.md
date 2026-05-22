# Итоговый проект — GigaVibeMiptCode

Консольный чат-бот для работы с OpenAI-compatible LLM.

Проект умеет хранить контекст диалога, прикреплять текстовые файлы к сообщениям,
обрабатывать большие файлы по частям и выводить ответы модели в streaming-режиме.

## Возможности проекта

Проект поддерживает:

- чат с OpenAI-compatible LLM;
- хранение истории сообщений;
- ограничение контекста по символам и количеству сообщений;
- system prompt;
- конфигурацию через `config.yaml` и `.env`;
- streaming response;
- прикрепление текстовых файлов через `@::path::`;
- обработку больших файлов по чанкам (`/filechunk`);
- обработку ошибок API и файлов;
- unit-тесты и проверку покрытия;
- команды `\q` и `/reset`.

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Создание config.yaml

Создайте файл `config.yaml` в папке `final_project`.

Пример конфигурации:

```yaml
api_key: ollama
api_host: http://localhost:11434/v1/
model: gemma3:270m
temperature: 0.7
limit_message: 20
limit_chars: 2000
system_prompt: You are a helpful assistant.
stream: true
```

### 3. Установка Ollama

Скачать Ollama: https://ollama.com/download

После установки скачайте модель:

```bash
ollama pull gemma3:270m
```

Проверить список моделей:

```bash
ollama list
```

Запустить Ollama:

```bash
ollama serve
```

### 4. Запуск проекта

Из папки `final_project`:

```bash
python main.py
```

или

```bash
python -m gigavibe
```

### 5. Пример работы

```text
> Привет
Привет! Чем могу помочь?

> Объясни этот код @::main.py::

> /filechunk paragraph=3 -y
```

## Переменные окружения

Переменные окружения имеют приоритет над `config.yaml`.

Пример `.env`:

```env
API_KEY=ollama
API_HOST=http://localhost:11434/v1/
MODEL=gemma3:270m
LIMIT_MESSAGE=20
LIMIT_CHARS=2000
TEMPERATURE=0.7
STREAM=true
```

## Команды

```text
\q
```

Выход из программы.

```text
/reset
```

Очистка истории сообщений и экрана.

```text
/filechunk
```

Режим обработки файла по чанкам.

## Проверка проекта

```bash
ruff check . --config ruff.toml
mypy --config-file mypy.ini .
pytest tests --cov=gigavibe --cov-report=html
```

HTML-отчёт создаётся в папке `htmlcov`.
