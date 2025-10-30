### Birthday reminder telegram-bot  by fast-api and aiogram for Avrora

### Activate VENV
```source .venv/bin/activate```

## alembic start to work:
```pip install alembic```

```
alembic init alembic
```

### change in file: alembic.ini:
```sqlalchemy.url = postgresql://user:password@localhost:5432/database_name```

### change in file: alembic/env.py:
```from your_model_file import Base  # Змініть на реальний шлях до файлу з вашими моделями```

```target_metadata = Base.metadata```

### create migration after changing in models:
```
alembic revision --autogenerate -m "initial migration"
```

```
alembic upgrade head
```

## pytest
### Без coverage
```
pytest --no-cov
```

### Тільки швидкі тести
```
pytest -m "not slow"
```

#### З детальним coverage
```
pytest --cov-report=term-missing --cov-report=html
```

### Тести з нижчим порогом покриття
```
pytest --cov-fail-under=70
```

### Open report in html
``` ai ignore
open htmlcov/index.html
```
