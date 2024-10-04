### Birthday reminder telegram-bot  by fast-api and aiogram for Avrora

## alembic start to work:
```pip install alembic```

```alembic init alembic```

### change in file: alembic.ini:
```sqlalchemy.url = postgresql://user:password@localhost:5432/database_name```

### change in file: alembic/env.py:
```from your_model_file import Base  # Змініть на реальний шлях до файлу з вашими моделями```

```target_metadata = Base.metadata```

### create migration after changing in models:
```alembic revision --autogenerate -m "initial migration"```

```alembic upgrade head```

