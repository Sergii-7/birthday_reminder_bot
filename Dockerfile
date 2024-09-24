FROM python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Тепер копіюємо решту файлів програми
COPY . .
# Копіюємо запускний скрипт та робимо його виконуваним
RUN chmod +x start.sh
# Відкриваємо порт для FastAPI
EXPOSE 8000
# Запуск Fast-Api
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
# Запуск стартового скрипта
CMD ["./start.sh"]