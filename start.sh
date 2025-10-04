#!/bin/bash

# запуск fast-api
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 &

# Запуск Telegram бота
python3 run_telegram_bot.py &

# Запуск Background task
while true; do
    echo "[`date`] Starting background task..."
    python3 run_background_task.py
    echo "[`date`] Task crashed or exited. Restarting in 5 seconds..."
    sleep 5
done &

# Очікування завершення усіх бекграунд-процесів
wait
