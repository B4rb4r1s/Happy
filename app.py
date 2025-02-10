from flask import Flask, request, session
from flask import redirect, url_for, flash, render_template, jsonify
import os
import time
import json

import datetime
import psycopg2

from run import Chain
from Verifying.doc_verification import verification

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
                        ORDER BY id DESC;''')
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

            # Методы для обработки документов
            chain = Chain()
            req = {'task': 'overwiev',
                   'path': file_path,
                   'dataset_handle': False}
            chain.handle_request(req)

            # Попытка подключения к базе данных
            conn = db_connection()

            # Запись файла в базу данных
            cursor = conn.cursor()
            try:
                # Запись в табоицу DOCUMENTS
                cursor.execute("""  INSERT INTO documents (filename,
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

                # Записать в таблицу NAMED_ENTITIES
                print(req['entities'], flush=True)
                print(req['entities'][0], flush=True)
                for tup in req['entities']:
                    cursor.execute("""  INSERT INTO named_entities (doc_id, entity, value)
                                        VALUES (
                                            (SELECT id 
                                            FROM documents 
                                            ORDER BY ID DESC LIMIT 1 ), %s, %s)""",
                                            (
                                            tup[0], 
                                            tup[1]
                                            )
                                    )

                # Подтверждение изменений
                jls_extract_var = conn
                jls_extract_var.commit()
                print(f'[{datetime.datetime.now()}][ DEBUG ] Data successfully uploaded to Database', flush=True)
            except Exception as err:
                print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Problem with uploading document to Database\n{err}', flush=True)

            # Завершение подключения к базе данных
            cursor.close()
            conn.close()

            # Удаление временно загруженного файла
            os.remove(file_path)

            
            flash(f'Файл \'{file.filename}\' успешно загружен и обработан')
            return redirect(url_for('index'))
        
        else:
            flash(f'Неправильный формат файла c расширением {ext}')
            return redirect(url_for('index'))


@app.route('/delete_documents', methods=['POST'])
def delete_documents():
    document_ids = request.form.getlist('document_ids')
    
    if document_ids:
        document_ids = [int(doc_id) for doc_id in document_ids]

        conn = db_connection()
        cursor = conn.cursor()

        try:
            # Выполнение удаления по всем таблицам базы данных
            cursor.execute('DELETE FROM documents       WHERE id        = ANY(%s)', (document_ids,))
            cursor.execute('DELETE FROM metadata        WHERE doc_id    = ANY(%s)', (document_ids,))
            cursor.execute('DELETE FROM named_entities  WHERE doc_id    = ANY(%s)', (document_ids,))
            
            conn.commit()
        except Exception as err:
            print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Problem with deleting documents from Databes\n{err}')
        
        cursor.close()
        conn.close()
    else:
        flash(f'Не выбраны документы для удаления')
    
    return redirect(url_for('index'))


# Страница для просмотра результатов обработки (например, список сущностей)
@app.route('/results/<int:doc_id>')
def results(doc_id):
    # Здесь должны быть данные, полученные после обработки документа

    # Отображение результатов для выбранного документа
    conn = db_connection()
    cursor = conn.cursor()
    
    cursor.execute(''' SELECT *
                    FROM documents 
                    RIGHT JOIN metadata ON documents.id = metadata.doc_id
                    WHERE documents.id = %s;
                ''', (doc_id,))
    document = cursor.fetchone()
    cursor.execute(''' SELECT entity, value
                    FROM named_entities
                    INNER JOIN documents ON documents.id = named_entities.doc_id
                    WHERE documents.id = %s;
                ''', (doc_id,))
    doc_entities = cursor.fetchall()
    
    cursor.close()
    conn.close()
    print(f'[ DEBUG APP ] {document}')
    
    if document:
        return render_template('results.html', 
                               filename=document[1], 
                               extracted_text=document[2], 
                               summary=document[3], 
                               big_summary=document[5],
                               # Метаинформация
                               format=document[8],
                               author=document[9],
                               creator=document[10],
                               title=document[11],
                               subject=document[12],
                               keywords=document[13],
                               creation_date=document[14],
                               producer=document[15],
                               # Сущности
                               entities = doc_entities
                               )
    else:
        flash('Документ не найден')
        return redirect(url_for('index'))


@app.route('/dataset/')
def dataset():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''  SELECT * 
                        FROM doc_dataset
                        ORDER BY id DESC;''')
    documents = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('dataset.html', dataset=documents)


@app.route('/dataset_document/<int:doc_id>')
def dataset_document(doc_id):
    conn = db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                    SELECT *
                    FROM doc_dataset
                    WHERE doc_dataset.id = %s;
                ''', (doc_id,))
    docs = cursor.fetchone()
    
    cursor.execute(''' SELECT *
                    FROM metadata_dataset
                    WHERE doc_id = %s;
                ''', (doc_id,))
    metadata = cursor.fetchone()
    
    cursor.execute(''' SELECT entity, value
                    FROM named_entities_dataset
                    INNER JOIN doc_dataset ON doc_dataset.id = named_entities_dataset.doc_id
                    WHERE doc_dataset.id = %s;
                ''', (doc_id,))
    dataset_entities = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('dataset_document.html', doc_full=docs, metadata=metadata, entities=dataset_entities)


# Простая функция чат-бота (заглушка)
def chatbot_response(user_input):
    # Здесь можно подключить вашу модель или API чат-бота
    return f"Вы сказали: {user_input}. Я пока просто эхо-бот."

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.json.get('message', '')
        # Логика обработки сообщения пользователя
        bot_response = chatbot_response(user_message)
        return jsonify({"response": bot_response})
    
    return render_template('chat-assistant.html')
    if request.method == 'POST':
        user_message = request.form.get('message')
        if user_message:
            bot_response = chatbot_response(user_message)
            return jsonify({'user_message': user_message, 'bot_response': bot_response})
        return jsonify({'error': 'Сообщение не должно быть пустым'}), 400
    
    return render_template('chat-assistant.html')


@app.route('/error')
def error():
    flash('Ошибка в чтении файла', 'warning')
    return redirect(url_for('index'))




if __name__ == '__main__':
    # Запускаем приложение Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
