#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# -------- Config ----------
REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
UVICORN_HOST="${UVICORN_HOST:-0.0.0.0}"
UVICORN_PORT="${UVICORN_PORT:-8000}"
UVICORN_WORKERS="${UVICORN_WORKERS:-1}"

# Опціонально — логи в файли:
LOG_DIR="${LOG_DIR:-./logs}"
mkdir -p "$LOG_DIR"

# -------- Utils ----------
die() { echo "ERROR: $*" >&2; exit 1; }

command -v redis-cli >/dev/null || die "redis-cli не знайдено. Встанови Redis або додай у PATH."
command -v redis-server >/dev/null || echo "⚠️  redis-server не знайдено у PATH (ОК, якщо Redis уже як сервіс)."
command -v python3 >/dev/null || die "python3 не знайдено."
# Запуск через модуль коректніший для venv:
python3 -c "import uvicorn" >/dev/null 2>&1 || echo "⚠️  uvicorn не в системі. Якщо він у .venv — активуємо нижче."

# Активація venv, якщо існує
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

PIDS=()

cleanup() {
  echo "Отримано сигнал. Зупиняю дочірні процеси..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
    fi
  done
  # Почекаємо коректного завершення
  wait || true
  echo "Всі процеси зупинені."
}
trap cleanup INT TERM EXIT

# -------- Redis ----------
echo "Перевіряю Redis на ${REDIS_HOST}:${REDIS_PORT}..."
if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
  echo "Redis не працює — пробую запустити локально..."
  if command -v redis-server >/dev/null; then
    redis-server --daemonize yes
  else
    die "redis-server недоступний і Redis не запущений."
  fi
fi

# Ретраї очікування готовності
for i in {1..20}; do
  if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
    echo "Redis готовий ✅"
    break
  fi
  sleep 0.5
  [[ $i -eq 20 ]] && die "Redis не стартував вчасно."
done

# -------- Uvicorn (FastAPI) ----------
if pgrep -f "uvicorn .*main:app" >/dev/null 2>&1; then
  echo "Uvicorn уже працює — пропускаю запуск."
else
  echo "Стартую Uvicorn на ${UVICORN_HOST}:${UVICORN_PORT} (workers=${UVICORN_WORKERS})..."
  python3 -m uvicorn main:app \
    --host "$UVICORN_HOST" \
    --port "$UVICORN_PORT" \
    --workers "$UVICORN_WORKERS" \
    >> "${LOG_DIR}/uvicorn.out" 2>&1 &
  PIDS+=($!)
fi

# -------- Telegram bot ----------
if pgrep -f "python3 .*run_telegram_bot.py" >/dev/null 2>&1; then
  echo "Telegram-бот уже працює — пропускаю запуск."
else
  echo "Стартую Telegram-бота..."
  python3 run_telegram_bot.py >> "${LOG_DIR}/telegram_bot.out" 2>&1 &
  PIDS+=($!)
fi

# -------- Background task (з автоперезапуском) ----------
bg_loop() {
  while true; do
    echo "[$(date '+%F %T')] Starting background task..."
    python3 run_background_task.py
    rc=$?
    echo "[$(date '+%F %T')] Task exited (rc=${rc}). Restarting in 5s..."
    sleep 5
  done
}
if pgrep -f "python3 .*run_background_task.py" >/dev/null 2>&1; then
  echo "Бекграунд-таск уже працює — пропускаю запуск."
else
  echo "Стартую бекграунд-таск із автоперезапуском..."
  bg_loop >> "${LOG_DIR}/background_task.out" 2>&1 &
  PIDS+=($!)
fi

# -------- Wait --------
echo "Усі процеси запущені. Очікую завершення..."
wait
