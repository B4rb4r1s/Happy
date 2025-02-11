# Используем официальный образ Python в качестве базового образа
FROM python:3.9

# Устанавливаем необходимые пакеты Linux
RUN apt-get update && apt-get install

# Создаем директорию для приложения
WORKDIR /app

# Копируем файлы вашего проекта в контейнер
COPY ./requirements.txt /app

# Устанавливаем зависимости из файла requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install nano
# Установка пакетов для OCR
RUN apt-get install -y poppler-utils \
    tesseract-ocr \
    tesseract-ocr-rus
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
# Установка моделей для NER
RUN python -m spacy download ru_core_news_sm 
RUN python -m spacy download ru_core_news_md 
RUN python -m spacy download ru_core_news_lg
RUN pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install "dedoc[torch]"

# Определяем команду для запуска приложения
# CMD /bin/bash

CMD [ "python", "app.py" ]
# ENTRYPOINT [ "python", "app.py" ]
# CMD ["-it", "--name", "hap", "-p", "5000:5000", "--gpus", "all"]

# Запуск контейнера со всеми необходимыми параметрами
# docker run -it --name hap -p 5000:5000 -v .:/app --rm --gpus all happy
# 
# docker start -it hap