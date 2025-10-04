#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

cd "$(dirname "$0")"   # <<< важливо: запускаємося з кореня проєкту

REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Активуємо venv, якщо є
if [[ -d ".venv" ]]; then
  source .venv/bin/activate
fi

# --- Redis ---
if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
  command -v redis-server >/dev/null || { echo "redis-server недоступний"; exit 1; }
  echo "Запуск Redis..."
  redis-server --daemonize yes
  for i in {1..20}; do
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1 && break
    sleep 0.5
    [[ $i -eq 20 ]] && { echo "Redis не стартував"; exit 1; }
  done
fi

# --- Uvicorn у foreground (критичний сервіс) ---
echo "Стартую Uvicorn..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 >> ./logs/uvicorn.out 2>&1 &
UVICORN_PID=$!

# чекаємо, поки порт дійсно відкриється
for i in {1..40}; do
  if lsof -i :8000 >/dev/null 2>&1 || ss -lntp 2>/dev/null | grep -q ':8000'; then
    echo "Uvicorn слухає порт 8000 ✅"
    break
  fi
  if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
    echo "Uvicorn впав під час старту. Лог нижче:"
    tail -n 200 ./logs/uvicorn.out || true
    exit 1
  fi
  sleep 0.5
  [[ $i -eq 40 ]] && { echo "Порт 8000 не відкрився вчасно"; exit 1; }
done

# --- другорядні процеси (бот і бекграунд) ---
echo "Стартую Telegram-бота..."
python3 run_telegram_bot.py >> ./logs/telegram_bot.out 2>&1 &
BOT_PID=$!

echo "Стартую бекграунд-таск..."
( while true; do
    python3 run_background_task.py || true
    echo "Task рестарт через 5с..."
    sleep 5
  done ) >> ./logs/background_task.out 2>&1 &
BG_PID=$!

# Якщо Uvicorn помирає — валимося й даємо оркестратору перезапустити
wait "$UVICORN_PID"
echo "Uvicorn завершився — завершаю скрипт."
exit 1
