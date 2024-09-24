#!/bin/bash

# запуск fast-api
#uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 &
python3 main.py &

# Запуск Telegram бота
python3 run_telegram_bot.py &

# Очікування завершення усіх бекграунд-процесів
wait