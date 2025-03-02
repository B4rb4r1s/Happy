import io
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import psycopg2
import pymupdf 
import subprocess

import os

from dedoc import DedocManager
from dedoc.attachments_handler import AttachmentsHandler
from dedoc.converters import DocxConverter, PNGConverter, ConverterComposition
from dedoc.metadata_extractors import BaseMetadataExtractor, MetadataExtractorComposition
from dedoc.readers import DocxReader, PdfAutoReader, PdfImageReader, ReaderComposition
from dedoc.structure_extractors import DefaultStructureExtractor, StructureExtractorComposition
from dedoc.structure_constructors import TreeConstructor, StructureConstructorComposition

dedoc_manager = DedocManager(
    manager_config={
        "attachments_handler": AttachmentsHandler(),
        "converter": ConverterComposition([DocxConverter(), PNGConverter()]),
        "reader": ReaderComposition([DocxReader(), PdfAutoReader(), PdfImageReader()]),
        "structure_extractor": StructureExtractorComposition(extractors={DefaultStructureExtractor.document_type: DefaultStructureExtractor()}, default_key=DefaultStructureExtractor.document_type),
        "structure_constructor": StructureConstructorComposition(constructors={"tree": TreeConstructor()}, default_constructor=TreeConstructor()),
        "document_metadata_extractor": MetadataExtractorComposition([BaseMetadataExtractor()])
    }
)



def mero_load(dir):
    # dr = './datasets/Mero'
    # dr = './Data/PDF'
    directory = os.fsencode(dir)
    
    for event in os.listdir(dir):
        for doc in os.listdir(dir+'/'+event):
            doc_path = dir+'/'+event+'/'+doc
            forma = doc[doc.find('.')+1:]

            text_tesseract = ''
            text_dedoc = ''

            cursor.execute('''
                SELECT file_name, full_text_tesseract, full_text_dedoc, id
                FROM doc_dataset
                WHERE file_name = %s;
                           ''', (doc,))
            already_uploaded_docs = cursor.fetchall()

            if len(already_uploaded_docs) > 0:

                # Tesseract text
                print(already_uploaded_docs, flush=True)
                if already_uploaded_docs[0][1] == None:
                    print(f'[ DEBUG ] Uploading document using Tesseract OCR {doc}')
                    text_tesseract = ''
                    try:
                        pages = convert_from_path(doc_path, 900)
                        for page in pages:
                            text = pytesseract.image_to_string(page, lang='eng+rus')
                            text_tesseract += text + '\n'
                    except Exception as err:
                        print(f'[ DEBUG ERROR ] Document {doc} is too big to process')
                        continue
                    cursor.execute("""
                        UPDATE doc_dataset 
                        SET full_text_tesseract = %s
                        WHERE id = %s
                                """, (text_tesseract, already_uploaded_docs[0][3]))
                    connection.commit()

                    
                # Dedoc text
                if already_uploaded_docs[0][2] == None:
                    print(f'[ DEBUG ] Uploading document using Dedoc {doc}')
                    text_dedoc = ''
                    try:
                        parsed_document = dedoc_manager.parse(doc_path)
                        rec = concat_subpara([], parsed_document.content.structure)
                        text_dedoc = '\n'.join(rec)
                    except Exception as err:
                        print(f'[ DEBUG ERROR ] Document {doc} is too big to process')
                        continue
                    cursor.execute("""
                        UPDATE doc_dataset 
                        SET full_text_dedoc = %s
                        WHERE id = %s
                                """, (text_dedoc, already_uploaded_docs[0][3]))
                    connection.commit()
                
                if already_uploaded_docs[0][1] and already_uploaded_docs[0][2]:
                    print(f'[ DEBUG ] Dcoument {doc} is already uploaded and processed in Database')
                    continue

            else:
                print(f'[ DEBUG ] Uploading document using Tesseract OCR {doc}')
                try:
                    pages = convert_from_path(doc_path, 900)
                    text_tesseract = ''
                    for page in pages:
                        text = pytesseract.image_to_string(page, lang='eng+rus')
                        text_tesseract += text + '\n'
                except Exception as err:
                    text_tesseract = ''
                    print(f'[ DEBUG ERROR ] Document {doc} is too big to process')
                    continue

                print(f'[ DEBUG ] Uploading document using Dedoc {doc}')
                text_dedoc = ''
                try:
                    parsed_document = dedoc_manager.parse(doc_path)
                    rec = concat_subpara([], parsed_document.content.structure)
                    text_dedoc = '\n'.join(rec)
                except Exception as err:
                    print(f'[ DEBUG ERROR ] Document {doc} is too big to process')
                    continue    

                cursor.execute('''
                    INSERT INTO doc_dataset (full_text_tesseract, full_text_dedoc, file_name, event, format)
                    VALUES (%s, %s, %s, %s, %s);''', 
                    (text_tesseract, text_dedoc, doc, event, forma))
                connection.commit()
            
            print(f'[ Success ] Data uploaded\n\t{text_tesseract[:20]}, {text_dedoc[:20]}, {doc}, {event}, {forma}')
    return 0



def read_tables(tables):
    res_tables = []
    for table in tables:
        # header = [cell.get_text() for cell in table.cells[0]]
        rows = [[cell.get_text() for cell in row] for row in table.cells]
        res_tables.append(rows)
    return res_tables

def concat_subpara(full, para):
    # full = []
    full.append(para.text)
    if len(para.subparagraphs) > 0:
        for par in para.subparagraphs:
            concat_subpara(full, par)
    return full

def dedoc_scan(path):
    text_dedoc = ''
    parsed_document = dedoc_manager.parse(path)
    rec = concat_subpara([], parsed_document.content.structure)
    tables = read_tables(parsed_document.content.tables)
    text_dedoc = '\n'.join(rec)
    return text_dedoc, tables


def elibrary_load(cursor, dir):
    # Название таблыцы в базе данных
    db_table = 'elibrary_dataset'

    cursor.execute('''
        SELECT filename
        FROM elibrary_dataset
    ''')
    already_uploaded = [item[0] for item in cursor.fetchall()]

    for doc in os.listdir(dir):
        doc_path = dir + '/' + doc

        # Проверка - загружен ли уже документ?
        if doc in already_uploaded:
            print(f'[ DEBUG ] Documnet {doc} is already uploaded')
            continue
        else:
            if doc[doc.find('.')+1:].lower() == 'pdf':
                text_dedoc = ''

                # Сканирование с помощью DeDoc
                try:
                    text_dedoc, tables = dedoc_scan(doc_path)
                    print(doc, text_dedoc[:10])
                except Exception as err:
                    print(f'[ ERROR ] >>> {err}')
                    # subprocess.run(['mv', doc_path, '/app/\!Datasets/GRNTI/troubles/'])
                    continue


                # Загрузка в базу данных
                cursor.execute('''
                    INSERT INTO elibrary_dataset (filename, text_dedoc)
                    VALUES (%s, %s);''', 
                    (doc, text_dedoc,))

                if tables:
                    for table in tables:
                        cursor.execute('''
                            INSERT INTO elibrary_dataset_tables (doc_id, rows)
                            VALUES (
                                (SELECT id 
                                FROM elibrary_dataset 
                                ORDER BY ID DESC LIMIT 1), %s)
                        ''', (table,))
                connection.commit()
                print(f'[ DEBUG ] Documnet {doc} has successfuly uploaded')

            else:
                print(f'[ DEBUG ] Documnet {doc} is not PDF format')
                continue
    



if __name__ == '__main__':
    connection = psycopg2.connect(database='happy_db', 
                                  user="happy_user", 
                                  password="happy", 
                                  host="postgre", 
                                  port="5432")
    cursor = connection.cursor()

    elibrary_load(cursor, '!Datasets/GRNTI/elibrary044100')
    
    cursor.close()
    connection.close()