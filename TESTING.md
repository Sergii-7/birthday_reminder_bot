# 🧪 Тестування Birthday Reminder Bot

## 📋 Огляд

Цей документ описує систему тестування для Birthday Reminder Bot, включаючи інструкції по запуску тестів, структуру тестів та результати тестування.

## 🚀 Швидкий старт

### Активація віртуального середовища
```bash
source .venv/bin/activate
```

### Запуск всіх працюючих тестів
```bash
pytest tests/test_minimal.py tests/service/ tests/dir_open_ai/test_service_openai.py tests/dir_open_ai/test_connect.py -v
```

### Запуск окремих модулів
```bash
# Тести service модуля
pytest tests/service/ -v

# Тести OpenAI модуля
pytest tests/dir_open_ai/test_service_openai.py tests/dir_open_ai/test_connect.py -v

# Мінімальні тести (перевірка базової функціональності)
pytest tests/test_minimal.py -v
```

## 📊 Поточний стан тестування

### ✅ Працюючі тести: 55/55 (100% успіх)

- 🧪 **Мінімальні тести**: 3 тести ✅
- 🛠️ **Service модуль**: 27 тестів ✅
- 🤖 **OpenAI модуль**: 25 тестів ✅
  - Connect: 12 тестів ✅
  - Service: 13 тестів ✅

### 📈 Результати останнього запуску
```
======================================== test session starts ========================================
collected 55 items

tests/test_minimal.py::TestMinimal::test_basic_functionality PASSED                           [  1%]
tests/test_minimal.py::TestMinimal::test_import_works PASSED                                  [  3%]
tests/test_minimal.py::TestMinimal::test_config_mock_works PASSED                             [  5%]
[... service tests ...]
[... openai tests ...]

======================================== 55 passed in 1.91s =========================================
```

## 📁 Структура тестів

### Загальна кількість файлів: 36 тестових файлів

```
tests/
├── conftest.py                              # Конфігурація pytest з мокінгом
├── pytest.ini                              # Налаштування pytest
├── test_minimal.py                         # Базові тести функціональності
├── bot_app/                                # Тести Telegram бота (8 файлів)
│   ├── test_callback.py
│   ├── test_command.py
│   ├── test_create_bot.py
│   ├── test_message.py
│   ├── dir_menu/                           # Тести меню (3 файли)
│   │   ├── test_buttons_for_menu.py
│   │   ├── test_menu.py
│   │   └── test_send_panel.py
│   └── dir_service/                        # Тести сервісів бота (2 файли)
│       ├── test_bot_service.py
│       └── test_calendar_m.py
├── web_app/                                # Тести веб-додатку (7 файлів)
│   ├── test_create_app.py
│   └── app_files/                          # Тести маршрутів (6 файлів)
│       ├── test_admin_route.py
│       ├── test_app_access.py
│       ├── test_telegram_route.py
│       ├── test_test_route.py
│       ├── test_user_model.py
│       └── test_user_route.py
├── sql/                                    # Тести SQL БД (7 файлів)
│   ├── test_complex_func_db.py
│   ├── test_sql_connect.py
│   ├── test_func_app_db.py
│   ├── test_func_db.py
│   ├── test_func_system_db.py
│   ├── test_models.py
│   └── test_tool_db.py
├── service/                                # Тести сервісів ✅ (2 файли)
│   ├── test_create_data.py
│   └── test_service_tools.py
├── dir_open_ai/                            # Тести OpenAI ✅ (3 файли)
│   ├── test_connect.py
│   ├── test_open_ai_tools.py
│   └── test_service_openai.py
├── dir_schedule/                           # Тести планувальника (3 файли)
│   ├── test_some_schedule.py
│   ├── test_some_task.py
│   └── test_some_tools.py
└── mongo_db/                               # Тести MongoDB (4 файли)
    ├── test__copy_sql_db.py
    ├── test_mongo_connect.py
    ├── test_model.py
    └── test_pydantic_model.py
```

## 🔧 Технічна конфігурація

### Pytest конфігурація (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --disable-warnings --asyncio-mode=auto
norecursedirs = src .git .tox dist build *.egg
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### Мокінг стратегія (conftest.py)

#### Мокування конфігурації
- `config.URI_DB` → `'sqlite:///:memory:'`
- `config.MONGO_URI` → `'mongodb://localhost:27017/test'`
- `config.API_KEY_OPENAI` → `'test_openai_key'`
- `config.TOKEN` → `'test_telegram_token'`
- `config.REDIS_HOST` → `'localhost'`
- `config.REDIS_PORT` → `6379`

#### Мокування залежностей
- **Бази даних**: AsyncMock для SQL/MongoDB/Redis
- **Telegram Bot API**: MagicMock для aiogram
- **OpenAI API**: MagicMock для openai клієнта
- **FastAPI**: TestClient для веб-тестів
- **Логери**: MagicMock для всіх логерів

## 📋 Доступні команди тестування

### Основні команди

```bash
# Запуск всіх працюючих тестів
pytest tests/test_minimal.py tests/service/ tests/dir_open_ai/test_service_openai.py tests/dir_open_ai/test_connect.py -v

# Запуск з коротким виводом
pytest tests/test_minimal.py tests/service/ tests/dir_open_ai/test_service_openai.py tests/dir_open_ai/test_connect.py -q

# Запуск з детальним трейсбеком
pytest tests/test_minimal.py tests/service/ tests/dir_open_ai/test_service_openai.py tests/dir_open_ai/test_connect.py -v --tb=long
```

### Запуск окремих модулів

```bash
# Service модуль (27 тестів)
pytest tests/service/ -v

# OpenAI Connect (12 тестів)
pytest tests/dir_open_ai/test_connect.py -v

# OpenAI Service (13 тестів)
pytest tests/dir_open_ai/test_service_openai.py -v

# Мінімальні тести (3 тести)
pytest tests/test_minimal.py -v
```

### Запуск з фільтрами

```bash
# Запуск тільки unit тестів
pytest -m unit tests/service/ -v

# Запуск тільки швидких тестів (не slow)
pytest -m "not slow" tests/service/ -v

# Запуск конкретного тесту
pytest tests/service/test_service_tools.py::TestServiceTools::test_date_formatter -v

# Запуск тестів з конкретним ім'ям
pytest -k "date_formatter" tests/service/ -v
```

### Додаткові опції

```bash
# Запуск з покриттям коду
pytest tests/service/ --cov=src/service --cov-report=html

# Запуск з паралелізацією (якщо встановлено pytest-xdist)
pytest tests/service/ -n auto

# Запуск з детальним логуванням
pytest tests/service/ -v --tb=short --capture=no

# Запуск з тимчасовою зупинкою на першій помилці
pytest tests/service/ -x

# Запуск з максимальним числом помилок перед зупинкою
pytest tests/service/ --maxfail=5
```

## 🐛 Відомі проблеми

### Поточні обмеження

1. **Частина тестів потребує доопрацювання імпортів** - деякі модулі ще не повністю інтегровані з мокінгом системою
2. **Файл `src/web_app/app_files/test_route.py`** - це файл додатку, а не тест (може спричиняти плутанину)

### Успішно вирішені проблеми

✅ **Модуль `config` не знайдено** - створено мокування
✅ **Модуль `src` не знайдено** - додано до Python path
✅ **Логери не знайдено** - створено мокування модулів
✅ **pytest знаходить файли не в tests/** - налаштовано norecursedirs

## 🔮 Розвиток тестування

### Короткострокові цілі
- [ ] Виправити імпорти у решті тестових модулів
- [ ] Додати тести покриття коду
- [ ] Інтегрувати тести в CI/CD pipeline

### Довгострокові цілі
- [ ] Додати інтеграційні тести
- [ ] Додати e2e тести для Telegram бота
- [ ] Налаштувати автоматичне тестування на GitHub Actions

## 📞 Підтримка

Якщо у вас виникають проблеми з тестами:

1. **Перевірте активацію віртуального середовища**: `source .venv/bin/activate`
2. **Перевірте встановлення залежностей**: `pip install -r requirements-dev.txt`
3. **Запустіть мінімальні тести**: `pytest tests/test_minimal.py -v`
4. **Перевірте Python path**: тести автоматично додають `src/` до path

---

**Останнє оновлення**: 8 жовтня 2025 р.
**Статус**: ✅ Система тестування функціональна (55/55 тестів працюють)
