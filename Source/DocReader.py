# импортирование библиотек
import os
import re
import PyPDF2
import pymupdf 
from datetime import datetime

from Source.Handler import Handler
from Source.OCR import extract_text_from_img


# Структура апроса:
# request{
#     task:           Текущая задача в цепочке
#     dataset_handle: Флаг, ***
#     file_format:    Формат документа (устанавливается в FileOverwiev.py)
#     meta:           Словарь метаинформации документа (устанавливается в ExtractMeta.py)
#     text:           Текстовый слой PDF-файла (устанавливается в DocReader.py)
#     text_tesseract: Текст извлеченный с помощью Tesseract (устанавливается в DocReader.py)
#     text_dedoc:     Текст извлеченный с помощью DeDoc (устанавливается в DocReader.py)
#     tables:         Таблицы выделенные DeDoc (устанавливается в DocReader.py)
# 
#     summary:        Краткое сгенерированное содержание (устанавливается в Summarizer.py)
#     big_summary:    Более полное сгенерированное содержание (устанавливается в Summarizer.py)
#     entities:       Словарь сущность - класс сущности (устанавливается в NERer.py)
# }
class TextExtractionHandler(Handler):
    def handle(self, request):
        '''
        Текущий запрос:
            request = {
                'task': 'extract_text',
                'path': './Data/PDF/text/text2.pdf',
                'dataset_handle': True/False}
        '''
        if request['task'] == 'extract_text' and request['dataset_handle'] == False:
            text_tesseract = None
            text_dedoc = None
            tables = None
            all_text = ''
            try:
                if request['file_format'] == 'pdf':
                    # Чтение текстового слоя
                    with open(request['path'], 'rb') as file:
                        reader = pymupdf.open(file)
                        for page in reader:
                            all_text += page.get_text()

                    text_tesseract, text_dedoc, tables = extract_text_from_img(request['path'], request['file_format'])

                elif request['file_format'] in ["jpg", "jpeg", "png"]:
                    print('[ DEBUG ] Extracting from IMG scan')
                    text_tesseract, text_dedoc, tables = extract_text_from_img(request['path'], request['file_format'])

                elif request['file_format'] in ["doc", "docx"]:
                    print('[ DEBUG ] Extracting from DOC scan')
                    text_tesseract, text_dedoc, tables = extract_text_from_img(request['path'], request['file_format'])

                request['text'] = ''
                request['text_tesseract'] = text_tesseract
                request['text_dedoc'] = text_dedoc
                request['tables'] = tables

                print(f"[ DEBUG ] TextExtractionHandler: Обработано")
                request['task'] = 'generate_summary'
                return super().handle(request)
            
            except Exception as err:
                print(f"[{datetime.now()}][ DEBUG ERROR ExtrMeta ] Handling failed\n>>> {err}")
                return super().handle(request)
        
        elif request['dataset_handle'] == True:
            print('[ DEBUG ] Extracting from scan')
            text_tesseract, text_dedoc, tables = extract_text_from_img(request['path'], request['file_format'])
            
            request['text'] = None
            request['text_tesseract'] = text_tesseract
            request['text_dedoc'] = text_dedoc
            request['tables'] = tables

            print(f"[ DEBUG ] TextExtractionHandler: Обработано")
            # print(request['text'])
            request['task'] = 'generate_summary'
            return super().handle(request)
            
        else:
            print(f"[ DEBUG ] Task TextExtractionHandler skipped >>> {request['task']}")
            return super().handle(request)



if __name__ == "__main__":
    reader = TextExtractionHandler()

    # Ручной запрос
    manual_request = {'task': 'extract_text',
                      'path': "./Data/PDF/text/text2.pdf"}
    
    reader.handle(manual_request)

    print(f"Содержние документа: {manual_request.get('summery')}")
    # texts = extract_text_from_pdfs_in_folder("./Data/PDF/text/")

    # for filename, text in texts.items():
    #     print(f"--- Содержимое файла: {filename} ---\n")
    #     print(text)
    #     print("\n")



