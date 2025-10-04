#!/bin/bash
set -euo pipefail

# корінь та PYTHONPATH
export PYTHONPATH="$(pwd)"

# Redis
if ! redis-cli ping >/dev/null 2>&1; then
  echo "Запуск Redis..."
  redis-server --daemonize yes
  sleep 2
  redis-cli ping >/dev/null || { echo "Redis не запускається!"; exit 1; }
else
  echo "Redis вже працює."
fi

# FastAPI
echo "Запуск FastAPI..."
uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers 1 \
  --proxy-headers &
UVICORN_PID=$!
sleep 2
ps -p "$UVICORN_PID" >/dev/null || { echo "FastAPI не запускається!"; exit 1; }
echo "FastAPI успішно запущено."


echo "🤖 Запуск Telegram-бота..."
python3 run_telegram_bot.py &
echo "✅ Telegram-бот запущено."

# Запуск Background task
while true; do
    echo "[`date`] Starting background task..."
    python3 run_background_task.py
    echo "[`date`] Task crashed or exited. Restarting in 5 seconds..."
    sleep 5
done &

echo "⏳ Очікування завершення всіх процесів..."
wait
