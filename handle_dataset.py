import io
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import psycopg2
import datetime

from run import Chain

import os




if __name__ == '__main__':
    
    connection = psycopg2.connect(database='happy_db', user="happy_user", password="happy", host="postgre", port="5432")

    cursor = connection.cursor()
    cursor.execute('''
        SELECT * 
        FROM doc_dataset;
                   ''')
    
    
    chain = Chain()
    uploaded_docs = cursor.fetchall()
    for doc in uploaded_docs:
        # file_path = './DATA/PDF/scan/'+doc[2]

        doc_id = doc[0]
        text = doc[1]
        doc_file_name = doc[2]

        if not doc[5] and not doc[6]:
        
            req = {'task': 'generate_summary',
                'text': doc[1]}
            
            chain.handle_request(req)

            # print(req)

            cursor = connection.cursor()
            try:
                # Запись в табоицу DOC_DATASET
                cursor.execute("""
                            UPDATE doc_dataset 
                            SET big_summary = %s, summary = %s
                            WHERE id = %s
                            """, (req['big_summary'], req['summary'], doc_id))
                    
                # Запись в табоицу METADATA_DATASET
                # cursor.execute("""INSERT INTO metadata_dataset (doc_id, format, author, 
                #                                         creator, title, subject, 
                #                                         keywords, creation_date, producer)
                #                     VALUES (
                #                         (SELECT id 
                #                         FROM documents 
                #                         ORDER BY ID DESC LIMIT 1 ), 
                #                             %s, %s, %s, %s, %s, %s, %s, %s)""", 
                #                         (
                #                             req['meta']['format'],
                #                             req['meta']['author'],
                #                             req['meta']['creator'],
                #                             req['meta']['title'],
                #                             req['meta']['subject'],
                #                             req['meta']['keywords'],
                #                             # Формат 02.04.2024 20:28:19
                #                             #  (%d.%m.%Y %H:%M:%S)
                #                             datetime.datetime.strptime(req['meta']['creation_date'], '%d.%m.%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
                #                         #  datetime.datetime.strptime(req['meta']['modification_date'], '%d.%m.%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
                #                             req['meta']['producer'] 
                #                         )
                #                 )

                # Записать в таблицу NAMED_ENTITIES
                print(req['entities'], flush=True)
                print(req['entities'][0], flush=True)
                for tup in req['entities']:
                    cursor.execute("""  INSERT INTO named_entities_dataset (doc_id, entity, value)
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
                connection.commit()
                print(f'[{datetime.datetime.now()}][ DEBUG ] Data successfully uploaded to Dataset Database', flush=True)
            except Exception as err:
                print(f'[{datetime.datetime.now()}][ DEBUG ERROR ] Problem with uploading document to Dataset Database\n{err}', flush=True)
            
    cursor.close()
    connection.close()