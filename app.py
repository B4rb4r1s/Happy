from flask import Flask, request, session
from flask import redirect, url_for, flash, render_template, jsonify
import os
import time
import json
import traceback

import datetime
import psycopg2

from run import Chain

import sys
sys.stdout.flush()


# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Секретный ключ для защиты сессий и сообщений
app.secret_key = 'your_secret_key'

# Папка для загрузки файлов
UPLOAD_FOLDER = 'static/Uploads'
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
                        FULL JOIN metadata ON documents.id = metadata.doc_id
                        ORDER BY id DESC;''')
    documents = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('index.html', documents=documents)


# Обработка загрузки файла
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or not request.files['file'].filename.strip():
        flash('Нет файла для загрузки')
        return redirect(request.url)
    
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    chain = Chain()
    req = {'task': 'overwiev',
            'path': file_path,
            'dataset_handle': False}
    chain.handle_request(req)

    conn = db_connection()
    cursor = conn.cursor()

    # Запись файла в базу данных
    try:
        # Запись в табоицу DOCUMENTS
        cursor.execute("""  
            INSERT INTO documents (filename, 
                                   content, 
                                   summary, 
                                   upload_time, 
                                   doc_format,
                                   text_tesseract,
                                   text_dedoc)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (file.filename,
                req['text'],
                req['summary'],
                datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                req['file_format'],
                req['text_tesseract'],
                req['text_dedoc'],
                )
            )
        
        cursor.execute('''
            SELECT id 
            FROM documents 
            ORDER BY ID DESC LIMIT 1
        ''')
        doc_id = cursor.fetchone()[0] 
        
        # Запись в табоицу METADATA
        if req['file_format'] == 'pdf' and 'meta' in req:
            metadata = req['meta']
            cursor.execute("""
                INSERT INTO metadata (doc_id, 
                                      format, 
                                      author, 
                                      creator, 
                                      title, 
                                      subject, 
                                      keywords, 
                                      creation_date, 
                                      producer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (
                    doc_id, 
                    metadata.get('format'), 
                    metadata.get('author'),
                    metadata.get('creator'), 
                    metadata.get('title'),
                    metadata.get('subject'), 
                    metadata.get('keywords'),
                    metadata.get('creation_date') or None, 
                    metadata.get('producer')
                    )
            )
        # if req['file_format'] in ['jpg', 'jpeg', 'png']:
        #     cursor.execute("""INSERT INTO metadata (doc_id, format)
        #                         VALUES (
        #                             (SELECT id 
        #                             FROM documents 
        #                             ORDER BY ID DESC LIMIT 1 ), 
        #                                 %s)""", 
        #                             (req['file_format'],)
        #                     )

        # Записать в таблицу NAMED_ENTITIES
        if req.get('entities'):
            for tup in req['entities']:
                cursor.execute("""  
                    INSERT INTO named_entities (doc_id, entity, value)
                    VALUES (
                        %s, %s, %s)""",
                        (
                        doc_id,
                        tup[0], 
                        tup[1]
                        )
                )

        # Запись в таблицу таблиц, если есть
        if req['tables']:
            for table in req['tables']:
                cursor.execute("""
                    INSERT INTO tables (doc_id, rows)
                    VALUES (%s, %s)
                """, (doc_id, table)
                )

        # Подтверждение изменений
        conn.commit()

        print(f'[{datetime.datetime.now()}][ DEBUG ] Data successfully uploaded to Database', flush=True)
    except Exception as err:
        print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Problem with uploading document to Database\n>>> {err}', flush=True)
        print(f'>>> {traceback.format_exc()}', flush=True)

    # Завершение подключения к базе данных
    cursor.close()
    conn.close()

    # Удаление временно загруженного файла
    # os.remove(file_path)
    
    flash(f'Файл \'{file.filename}\' успешно загружен и обработан')
    return redirect(url_for('index'))


@app.route('/delete_documents', methods=['POST'])
def delete_documents():
    document_ids = request.form.getlist('document_ids')
    
    if not document_ids:
        flash(f'Не выбраны документы для удаления')
        return redirect(url_for('index'))

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
        print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Problem with deleting documents from Databes\n>>> {err}')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('index'))


# Страница для просмотра результатов обработки (например, список сущностей)
@app.route('/results/<int:doc_id>')
def results(doc_id):
    # Здесь должны быть данные, полученные после обработки документа

    # Отображение результатов для выбранного документа
    conn = db_connection()
    cursor = conn.cursor()
    
    cursor.execute(''' 
        SELECT documents.id,
               filename, 
               content, 
               text_tesseract,
               text_dedoc,
               big_summary,
               summary, 
               upload_time, 
               doc_format,
            
               metadata.id,
               doc_id,
               format, 
               author, 
               creator, 
               title, 
               subject, 
               keywords, 
               creation_date, 
               producer
        FROM documents 
        FULL JOIN metadata ON documents.id = metadata.doc_id
        WHERE documents.id = %s;
        ''', (doc_id,))
    document = cursor.fetchone()
    
    matadata = document[8:]
    document = document[:9]

    cursor.execute(''' 
        SELECT entity, value
        FROM named_entities
        INNER JOIN documents ON documents.id = named_entities.doc_id
        WHERE documents.id = %s;
        ''', (doc_id,))
    doc_entities = cursor.fetchall()

    cursor.execute(''' 
        SELECT doc_id, header, rows
        FROM tables
        WHERE doc_id = %s;
    ''', (doc_id,))
    tables = cursor.fetchall()
    
    cursor.close()
    conn.close()
    # print(f'[ DEBUG APP ] {document}')
    
    if document:
        return render_template('results.html', 
                               filename =       document[1],
                               extracted_text = document[2],
                               text_tesseract = document[3],
                               text_dedoc =     document[4],
                               big_summary =    document[5],
                               summary =        document[6],
                               upload_time =    document[7],
                               doc_format =     document[8],

                               # Метаинформация
                               doc_id =         matadata[1],
                               format =         matadata[2],
                               author =         matadata[3],
                               creator =        matadata[4],
                               title =          matadata[5],
                               subject =        matadata[6],
                               keywords =       matadata[7],
                               creation_date =  matadata[8],
                               produce =        matadata[9],

                               # Сущности
                               entities = doc_entities,

                               # Таблицы
                               tables = tables
                               )
    else:
        flash('Документ не найден')
        return redirect(url_for('index'))


@app.route('/dataset/')
def dataset():
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute('''  
        SELECT doc_dataset.id,
               filename,
               event,
               format,
               full_text_tesseract,
               full_text_dedoc
        FROM doc_dataset
        ORDER BY id DESC;
    ''')
    documents = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('dataset.html', dataset=documents)


@app.route('/dataset_document/<int:doc_id>')
def dataset_document(doc_id):
    conn = db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT doc_dataset.id,
               full_text_tesseract,
               full_text_dedoc,
               filename, 
               event,
               format,
               big_summary,
               summary
        FROM doc_dataset
        WHERE doc_dataset.id = %s;
    ''', (doc_id,))
    docs = cursor.fetchone()
    
    cursor.execute('''
        SELECT metadata_dataset.id,
               doc_id,
               format, 
               author, 
               creator, 
               title, 
               subject, 
               keywords, 
               creation_date, 
               producer
        FROM metadata_dataset
        WHERE doc_id = %s;
    ''', (doc_id,))
    metadata = cursor.fetchone()
    
    cursor.execute('''
        SELECT entity, value
        FROM named_entities_dataset
        INNER JOIN doc_dataset ON doc_dataset.id = named_entities_dataset.doc_id
        WHERE doc_dataset.id = %s;
    ''', (doc_id,))
    dataset_entities = cursor.fetchall()
    
    cursor.execute(''' 
        SELECT doc_id, header, rows
        FROM tables_dataset
        WHERE doc_id = %s;
    ''', (doc_id,))
    tables = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('dataset_document.html', 
                        #    doc_full=docs, 
                           id_doc =         docs[0],
                           text_tesseract = docs[1],
                           texy_dedoc =     docs[2],
                           filename =       docs[3],
                           event =          docs[4],
                           doc_format =     docs[5],
                           big_summary =    docs[6],
                           summar =         docs[7],

                        #    metadata=metadata, 
                           metadata_dataset_id =    metadata[0],
                           doc_id =                 metadata[1],
                           format =                 metadata[2],
                           author =                 metadata[3],
                           creator =                metadata[4],
                           title =                  metadata[5],
                           subject =                metadata[6],
                           keywords =               metadata[7],
                           creation_date =          metadata[8],
                           producer =               metadata[9],

                           entities=dataset_entities,
                           
                           tables = tables)


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
