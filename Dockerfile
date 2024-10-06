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
# Установка пакетов для OCR
RUN apt-get install poppler-utils -y
RUN apt-get install tesseract-ocr -y
RUN apt-get install tesseract-ocr-rus -y
# Установка моделей для NER
RUN python -m spacy download ru_core_news_sm
RUN python -m spacy download ru_core_news_md
RUN python -m spacy download ru_core_news_lg

# Определяем команду для запуска приложения
# CMD /bin/bash
ENTRYPOINT [ "python", "app.py" ]
CMD ["-it", "--name", "hap", "-p", "5000:5000", "--gpus", "all"]

# Запуск контейнера со всеми необходимыми параметрами
# docker run -it --name hap -p 5000:5000 --gpus all happy
# 
# docker start -it hap