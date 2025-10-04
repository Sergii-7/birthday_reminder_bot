FROM python:3.12

# Оновлення списку пакетів та встановлення Redis + ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    redis-server \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Тепер копіюємо решту файлів програми
COPY . .

# Копіюємо запускний скрипт та робимо його виконуваним
RUN chmod +x start.sh

# Відкриваємо порт для FastAPI
EXPOSE 8000

# Запуск стартового скрипта
CMD ["./start.sh"]
