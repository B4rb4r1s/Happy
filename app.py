from flask import Flask, request, session
from flask import redirect, url_for, flash, render_template, jsonify, send_from_directory
import os
import re
import time
import json
import traceback

import datetime
import psycopg2

from Source import Chain

import sys
sys.stdout.flush()

WHITESPACE_HANDLER = lambda k: re.sub(r' {2,}', ' ', re.sub('\n+', '\n\t', re.sub(r'(?<!\n)\n(?!\n)', ' ', re.sub('-\n', '', k.strip()))))

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

    need_summary = 'summary' in request.form
    need_ner = 'ner' in request.form

    chain = Chain()
    req = {
        'task': 'overwiev',
        'path': file_path,
        'dataset_handle': False,
        'summary_needed': need_summary,
        'ner_needed': need_ner
    }
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
            creation_date=None if not req['meta'].get('creation_date') or req['meta'].get('creation_date')=='Unknown' else req['meta'].get('creation_date')
            cursor.execute("""
                SET datestyle = dmy;
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
                    req['meta'].get('format'), 
                    req['meta'].get('author'),
                    req['meta'].get('creator'), 
                    req['meta'].get('title'),
                    req['meta'].get('subject'), 
                    req['meta'].get('keywords'),
                    creation_date, 
                    req['meta'].get('producer')
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
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

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
    
    prev_id, next_id = get_adjacent_ids(doc_id, 'documents')
    
    cursor.close()
    conn.close()
    # print(f'[ DEBUG APP ] {document}')
    
    if document:
        return render_template('results.html', 
                               filename =       document[1],
                               extracted_text = document[2],
                               text_tesseract = document[3],
                               text_dedoc =     WHITESPACE_HANDLER(document[4]),
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
                               tables = tables,

                               prev_id = prev_id,
                               next_id = next_id)
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
    return render_template('dataset.html', dataset=documents, count = len(documents))


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

    prev_id, next_id = get_adjacent_ids(doc_id, 'doc_dataset')

    cursor.close()
    conn.close()
    return render_template('dataset_document.html', 
                        #    doc_full=docs, 
                           id_doc =         docs[0],
                           text_tesseract = docs[1],
                           texy_dedoc =     WHITESPACE_HANDLER(docs[2]),
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
                           
                           tables = tables,
                           
                           prev_id=prev_id, 
                           next_id=next_id)


@app.route('/elib_dataset/', methods=['GET', 'POST'])
def elib_dataset():
    conn = db_connection()
    cursor = conn.cursor()

    query = request.form.get('query')
    if query:
        cursor.execute('''
            SELECT elibrary_dataset.id, filename, text_dedoc, tag 
            FROM elibrary_dataset 
            WHERE content_vector @@ to_tsquery(%s);
        ''', (query,))
        documents = cursor.fetchall()

    else:
        cursor.execute('''  
            SELECT elibrary_dataset.id, filename, text_dedoc, tag
            FROM elibrary_dataset
            ORDER BY id DESC;
        ''')
        documents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('elib_dataset.html', dataset = documents,
                                                count = len(documents))

# @app.route('/elib_dataset/', methods=['POST'])
# def elib_dataset_search():
#     conn = db_connection()
#     cursor = conn.cursor()
    
#     query = request.form.get('query')
#     if query:
#         cursor.execute('''
#             SELECT * 
#             FROM elibrary_dataset 
#             WHERE content_vector @@ to_tsquery(%s);
#         ''', (query,))
#         documents = cursor.fetchall()

#         cursor.close()
#         conn.close()
#         return render_template('elib_dataset.html', dataset=documents,
#                                                     count = len(documents))
#     else:
#         return redirect(url_for('elib_dataset'))


@app.route('/elib_dataset_document/<int:doc_id>', methods=['GET', 'POST'])
def elib_dataset_document(doc_id):

    # changer = None
    # if request.method == 'POST':
    # changer = request.form.get('changer')

    conn = db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT elibrary_dataset.id,
               filename,
               text_dedoc
        FROM elibrary_dataset
        WHERE elibrary_dataset.id = %s;
    ''', (doc_id,))
    docs = cursor.fetchone()
    
    cursor.execute(''' 
        SELECT doc_id, header, rows
        FROM elibrary_dataset_tables
        WHERE doc_id = %s;
    ''', (doc_id,))
    tables = cursor.fetchall()
    
    cursor.execute(''' 
        SELECT lingvo_summary,
               mt5_summary,
               mbart_summary,
               rut5_summary,
               t5_summary
        FROM elibrary_dataset_summaries
        WHERE doc_id = %s;
    ''', (doc_id,))
    summaries = cursor.fetchone()
    if not summaries:
        summaries = [None]*5
        sums = False
    else:
        sums = True

    cursor.execute(''' 
        SELECT fred_t5_large,
               rum2m100,
               sage_fredt5_distilled,
               sage_fredt5_large,
               sage_m2m100,
               language_tool,
               langtool
        FROM elibrary_dataset_spell
        WHERE doc_id = %s;
    ''', (doc_id,))
    corrections = cursor.fetchone()
    if not corrections:
        corrections = [None]*7
        cors = False
    else:
        cors = True

    prev_id, next_id = get_adjacent_ids(doc_id, 'elibrary_dataset')

    cursor.close()
    conn.close()
    return render_template('elib_dataset_document.html', 
                           changer_ =       'summ',
                           id_doc =         docs[0],
                           filename =       docs[1],
                           text_dedoc =     WHITESPACE_HANDLER(docs[2]),
                           
                           tables = tables,
                           
                           sums =           sums,
                           lingvo_summary =     summaries[0],
                           mt5_summary =        summaries[1],
                           mbart_summary =      summaries[2],
                           rut5_summary =       summaries[3],
                           t5_summary =         summaries[4],

                           cors =           cors,
                           fred_t5_large =          corrections[0],
                           rum2m100 =               corrections[1],
                           sage_fredt5_distilled =  corrections[2],
                           sage_fredt5_large =      corrections[3],
                           sage_m2m100 =            corrections[4],
                           language_tool =          corrections[5],
                           langtool =               corrections[6],
                           
                           prev_id=prev_id, 
                           next_id=next_id)



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



def get_adjacent_ids(current_id, table):
    conn = db_connection()
    cursor = conn.cursor()

    # Получение предыдущего ID
    cursor.execute('''
        SELECT id
        FROM '''+ table +'''
        WHERE id < %s
        ORDER BY id DESC
        LIMIT 1;
    ''', (current_id,))
    prev_row = cursor.fetchone()
    prev_id = prev_row[0] if prev_row else None

    # Получение следующего ID
    cursor.execute('''
        SELECT id 
        FROM '''+ table +'''
        WHERE id > %s
        ORDER BY id ASC
        LIMIT 1;
    ''', (current_id,))
    next_row = cursor.fetchone()
    next_id = next_row[0] if next_row else None

    conn.close()
    return prev_id, next_id


@app.route('/pdf/<filename>')
def serve_pdf(filename):
    # return send_from_directory('uploads', filename)
    for dirs in os.listdir('prj/Datasets/GRNTI/elibrary'):
        if filename in os.listdir(f'prj/Datasets/GRNTI/elibrary/{dirs}'):
            print(f'prj/Datasets/GRNTI/elibrary/{dirs}/{filename}', flush=True)
            return send_from_directory(f'prj/Datasets/GRNTI/elibrary/{dirs}/', filename)
        else:
            print('No file')
            continue


@app.route('/error')
def error():
    flash('Ошибка в чтении файла', 'warning')
    return redirect(url_for('index'))




if __name__ == '__main__':
    # Запускаем приложение Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
