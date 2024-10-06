from flask import Flask, request, session
from flask import redirect, url_for, flash, render_template
import os
import time

import psycopg2

from run import Chain
from doc_verification import verification

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Секретный ключ для защиты сессий и сообщений
app.secret_key = 'your_secret_key'

# Папка для загрузки файлов
UPLOAD_FOLDER = 'Uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Главная страница с формой для загрузки файлов
@app.route('/')
def index():
    return render_template('index.html')


# Обработка загрузки файла
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Нет файла для загрузки')
        return redirect(request.url)
    # redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Не выбран файл для загрузки')
        return redirect(request.url)
    
    if file:
        # Проверка загруженного файла
        ext = verification(file.filename)
        if ext == '.pdf':

            # Сохраняем файл в папку uploads
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Прочитать содержимое файла
            file_content = file.read()

            # Подключение к базе данных
            connection = psycopg2.connect(database='happy_db',\
                            user="happy_user",\
                            password="happy",\
                            host="localhost",\
                            port="5432")
            # Запись файла в базу данных
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO documents (filename, filedata) VALUES (%s, %s)", (file.filename, file_content))
                # Подтверждение изменений
                connection.commit()
                cursor.close()

            # Завершение подключения к базе данных
            connection.close()
            
            # Методы для обработки документов
            chain = Chain()
            req = {'task': 'extract_meta',
                    'path': file_path}
            chain.handle_request(req)

            # Сохраняем результаты в сессии
            session['metadata'] = req['meta']
            session['extracted_text'] = req['text']
            session['summary'] = req['summary']
            session['entities'] = req['entities']

            if session['extracted_text'] == '':
                flash(f'Ошибка в чтении файла \'{file.filename}\'', 'warning')
                return redirect(url_for('index'))
            
            flash(f'Файл \'{file.filename}\' успешно загружен и обработан')
            return redirect(url_for('index'))
        
        else:
            flash(f'Неправильный формат файла c расширением {ext}')
            return redirect(url_for('index'))


# Страница для просмотра результатов обработки (например, список сущностей)
@app.route('/results')
def results():
    # Здесь должны быть данные, полученные после обработки документа
    # Например, из базы данных или глобальной переменной
    
    # extracted_text = req['text']
    # summary = req['summary']
    # entities = [
    #     ("Barack Obama", "PERSON"),
    #     ("United States", "GPE"),
    #     ("Washington", "GPE")
    # ]
    
    # Передаем данные в шаблон для отображения
    return render_template('results.html', 
                           extracted_text = session.get('extracted_text', 'Нет данных'), 
                           summary = session.get('summary', 'Нет данных'), 
                           entities = session.get('entities', []),
                           metadata = session.get('metadata', 'Нет данных'))


@app.route('/error')
def error():
    flash('Ошибка в чтении файла', 'warning')
    return redirect(url_for('index'))




if __name__ == '__main__':
    # Запускаем приложение Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
