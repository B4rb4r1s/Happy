from flask import Flask, request, session
from flask import redirect, url_for, flash, render_template
import os
import time

import datetime
import psycopg2

from run import Chain
from doc_verification import verification

import sys
sys.stdout.flush()


# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Секретный ключ для защиты сессий и сообщений
app.secret_key = 'your_secret_key'

# Папка для загрузки файлов
UPLOAD_FOLDER = 'Uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def db_connection():
    try:
        try:
            # подключение по docker-compose
            connection = psycopg2.connect(database='happy_db',\
                                            user="happy_user",\
                                            password="happy",\
                                            host="postgre",\
                                            port="5432")
            print(f'[{datetime.datetime.now()}][ DEBUG ] Connection to DB through Docker-compose', flush=True)
            return connection
        except:
            # локальное подключение
            connection = psycopg2.connect(database='happy_db',\
                                                user="happy_user",\
                                                password="happy",\
                                                host="localhost",\
                                                port="5432")
            print(f'[{datetime.datetime.now()}][ DEBUG ] Connection to local DB', flush=True)
            return connection
    except Exception as err:
        print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Error while connecting to Database\n{err}')
        return 0


# Главная страница с формой для загрузки файлов
@app.route('/')
def index():
    # Попытка подключения к базе данных
        conn = db_connection()
        cursor = conn.cursor() 

        cursor.execute('''  SELECT documents.id, filename, upload_time, creation_date 
                            FROM documents 
                            RIGHT JOIN metadata ON documents.id = metadata.doc_id
                            ORDER BY id DESC LIMIT 10;''')
        documents = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template('index.html', documents=documents)


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
            # file_content = file.read()
            
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

            # Попытка подключения к базе данных
            conn = db_connection()

            # Запись файла в базу данных
            cursor = conn.cursor()
            try:
                # Запись в табоицу DOCUMENTS
                cursor.execute("""INSERT INTO documents (filename,
                                                        content,
                                                        summary,
                                                        upload_time)
                                VALUES (%s, %s, %s, %s)""",
                                    (file.filename,
                                    req['text'],
                                    req['summary'],
                                    datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                                    )
                                )
                
                # Запись в табоицу METADATA
                cursor.execute("""INSERT INTO metadata (doc_id, format, author, 
                                                        creator, title, subject, 
                                                        keywords, creation_date, producer)
                                  VALUES (
                                        (SELECT id 
                                        FROM documents 
                                        ORDER BY ID DESC LIMIT 1 ), 
                                            %s, %s, %s, %s, %s, %s, %s, %s)""", 
                                        (
                                         req['meta']['format'],
                                         req['meta']['author'],
                                         req['meta']['creator'],
                                         req['meta']['title'],
                                         req['meta']['subject'],
                                         req['meta']['keywords'],
                                         # Формат 02.04.2024 20:28:19
                                         #  (%d.%m.%Y %H:%M:%S)
                                         datetime.datetime.strptime(req['meta']['creation_date'], '%d.%m.%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
                                        #  datetime.datetime.strptime(req['meta']['modification_date'], '%d.%m.%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
                                         req['meta']['producer'] 
                                        )
                                )

                # Подтверждение изменений
                conn.commit()
                cursor.close()
                print(f'[{datetime.datetime.now()}][ DEBUG ] Data successfully uploaded to Database', flush=True)
            except Exception as err:
                print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Problem with uploading document to Database\n{err}', flush=True)

            # Завершение подключения к базе данных
            conn.close()

            # Удаление временно загруженного файла
            os.remove(file_path)

            if session['extracted_text'] == '':
                flash(f'Ошибка в чтении файла \'{file.filename}\'', 'warning')
                return redirect(url_for('index'))
            
            flash(f'Файл \'{file.filename}\' успешно загружен и обработан')
            return redirect(url_for('index'))
        
        else:
            flash(f'Неправильный формат файла c расширением {ext}')
            return redirect(url_for('index'))


# Страница для просмотра результатов обработки (например, список сущностей)
@app.route('/results/<int:doc_id>')
def results(doc_id):
    # Здесь должны быть данные, полученные после обработки документа

    # Отображение результатов для выбранного документа
    conn = db_connection()
    cur = conn.cursor()
    
    # Извлекаем результаты обработки для конкретного документа по ID
    cur.execute(''' SELECT *
                    FROM documents 
                    RIGHT JOIN metadata ON documents.id = metadata.doc_id
                    WHERE documents.id = %s;
                ''', (doc_id,))
    document = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if document:
        return render_template('results.html', 
                               filename=document[1], 
                               extracted_text=document[2], 
                               summary=document[3],
                               # Метаинформация
                               format=document[7],
                               author=document[8],
                               creator=document[9],
                               title=document[10],
                               subject=document[11],
                               keywords=document[12],
                               creation_date=document[13],
                               producer=document[14],
                               # Сущности - заглушка БД
                               entities = session.get('entities', []))
    else:
        flash('Документ не найден')
        return redirect(url_for('index'))
    
    # Передаем данные в шаблон для отображения
    # return render_template('results.html', 
    #                        extracted_text = session.get('extracted_text', 'Нет данных'), 
    #                        summary = session.get('summary', 'Нет данных'), 
    #                        entities = session.get('entities', []),
    #                        metadata = session.get('metadata', 'Нет данных'))


@app.route('/error')
def error():
    flash('Ошибка в чтении файла', 'warning')
    return redirect(url_for('index'))




if __name__ == '__main__':
    # Запускаем приложение Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
