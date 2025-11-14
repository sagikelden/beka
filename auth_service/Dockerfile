# Используем минимальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Чтобы Python выводил логи сразу (без буферизации)
ENV PYTHONUNBUFFERED=1

# Копируем только requirements для ускорения билда
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код сервиса в контейнер
COPY . .

# Команда для запуска FastAPI с автообновлением при изменениях
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
