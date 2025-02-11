# Используем официальный образ Python в качестве базового образа
FROM python:3.9

RUN curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
# Устанавливаем необходимые пакеты Linux
RUN apt-get update && apt-get install

RUN apt-get install -y nano libreoffice djvulibre-bin unzip \
    automake binutils-dev build-essential ca-certificates clang g++ g++-multilib gcc-multilib libcairo2 libffi-dev \
    libgdk-pixbuf2.0-0 libglib2.0-dev libjpeg-dev libleptonica-dev libpango-1.0-0 libpango1.0-dev libpangocairo-1.0-0 libpng-dev libsm6 \
    libtesseract-dev libtool libxext6 make pkg-config poppler-utils shared-mime-info software-properties-common swig zlib1g-dev
RUN apt-get install -y nvidia-container-toolkit
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