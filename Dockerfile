FROM python:3.12-slim

# --- базові оптимізації Python ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- системні пакети ---
# curl для HEALTHCHECK, tini як init-процес (правильні сигнали), redis-server/ffmpeg якщо справді треба всередині контейнера
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    redis-server \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

# --- робоча директорія ---
WORKDIR /app

# --- спочатку залежності (кеш шарів) ---
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- тепер код ---
COPY . /app
RUN chmod +x /app/start.sh

# --- мережа ---
EXPOSE 8000

# --- healthcheck на простий ендпойнт (створи /health у FastAPI) ---
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# --- запуск через tini, щоб коректно ловити SIGTERM/SIGINT ---
ENTRYPOINT ["/usr/bin/tini", "--"]

# Якщо в start.sh вже є shebang `#!/usr/bin/env bash` і він виконавний:
CMD ["/app/start.sh"]
