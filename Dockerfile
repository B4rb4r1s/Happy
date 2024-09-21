# Используем официальный образ Python в качестве базового образа
FROM python:3.9

# Устанавливаем необходимые пакеты Linux
RUN apt-get update && apt-get install

# Создаем директорию для приложения
WORKDIR /app

# Копируем файлы вашего проекта в контейнер
COPY . /app

# Устанавливаем зависимости из файла requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install nano
# RUN apt-get install poppler-utils
# RUN apt-get install tesseract-ocr
# RUN apt-get install tesseract-ocr-rus
RUN python -m spacy download ru_core_news_sm
RUN python -m spacy download ru_core_news_md
RUN python -m spacy download ru_core_news_lg

# Определяем команду для запуска вашего приложения
CMD /bin/bash
# CMD ["python", "./run.py"]