# 1. Используем официальный легковесный образ Python 3.11
FROM python:3.11-slim

# 2. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 3. Отключаем буферизацию вывода Python и создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Копируем исходный код приложения и конфигурацию тестов
COPY app/ ./app
COPY tests/ ./tests
COPY pytest.ini .

# 6. Декларируем проброс порта 8000
EXPOSE 8000

# 7. Команда запуска веб-сервиса
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]