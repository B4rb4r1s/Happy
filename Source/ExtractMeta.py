import fitz  # PyMuPDF
from datetime import datetime

from Source.Handler import Handler

import sys
sys.stdout.flush()


# Структура апроса:
# request{
#     task:           Текущая задача в цепочке
#     dataset_handle: Флаг, ***
#     file_format:    Формат документа (устанавливается в FileOverwiev.py)
#     meta:           Словарь метаинформации документа (устанавливается в ExtractMeta.py)
# 
#     text:           Текстовый слой PDF-файла (устанавливается в DocReader.py)
#     text_tesseract: Текст извлеченный с помощью Tesseract (устанавливается в DocReader.py)
#     text_dedoc:     Текст извлеченный с помощью DeDoc (устанавливается в DocReader.py)
#     tables:         Таблицы выделенные DeDoc (устанавливается в DocReader.py)
#     summary:        Краткое сгенерированное содержание (устанавливается в Summarizer.py)
#     big_summary:    Более полное сгенерированное содержание (устанавливается в Summarizer.py)
#     entities:       Словарь сущность - класс сущности (устанавливается в NERer.py)
# }
class ExtractMeta(Handler):
    def handle(self, request):
        '''
        Текущий запрос:
            request = {
                'task': 'extract_meta',
                'path': './Data/PDF/text/*.*',
                'file_format': '.*'
                }
        '''
        if request['task'] == 'extract_meta':
            try:
                if request['file_format'] == 'pdf':
                    doc = fitz.open(request['path'])

                    meta = doc.metadata

                    meta_info = {
                        'format': meta.get('format', 'Нет данных'),
                        'author': meta.get('author', 'Нет данных'),
                        'creator': meta.get('creator', 'Нет данных'),
                        'title': meta.get('title', 'Нет данных'),
                        'subject': meta.get('subject', 'Нет данных'),
                        'keywords': meta.get('keywords', 'Нет данных'),
                        'trapped': meta.get('trapped', 'Нет данных'),
                        'encryption': meta.get('encryption', 'Нет данных'),
                        'creation_date': self.convert_date(meta.get('creationDate', 'Нет данных')),
                        'modification_date': self.convert_date(meta.get('modDate', 'Нет данных')),
                        'producer': meta.get('producer', 'Нет данных')
                    }
                    request['meta'] = meta_info

                elif request['file_format'] in ["jpg", "jpeg", "png"]:
                    # request['meta'] = {
                    #     'format': request['file_format'],
                    # }
                    print(f"[ DEBUG ] Task ExtractPDFMeta skipped >>> IMG FORMAT")
                    request['task'] = 'extract_text'
                    return super().handle(request)
                
                elif request['file_format'] in ["doc", "docx"]:
                    print(f"[ DEBUG ] Task ExtractPDFMeta skipped >>> DOC FORMAT")
                    request['task'] = 'extract_text'
                    return super().handle(request)

                else:
                    print(f"[ {datetime.now()} ][ DEBUG META ] UNKNOWN FORMAT")
                    return super().handle(request)
                

                print(f"[ {datetime.now()} ][ DEBUG ] ExtractPDFMeta: Обработано")
                print(request['meta'])

                request['task'] = 'extract_text'
                return super().handle(request)
            
            except Exception as err:
                print(f"[{datetime.now()}][ DEBUG ERROR ExtrMeta ] Handling failed\n>>> {err}")
                return super().handle(request)
        else:
            # Пропуск по предварительной настройке
            print(f"[ DEBUG ] Task ExtractPDFMeta skipped >>> {request['task']}")
            return super().handle(request)
        

    def convert_date(self, date):
        if date.startswith('D:'):
            date = date[2:]

        try:
            parsed_date = datetime.strptime(date[:14], '%Y%m%d%H%M%S')
            readable_date = parsed_date.strftime('%d.%m.%Y %H:%M:%S')
            return readable_date
        except ValueError:
            return "Unknown"
        


if __name__ == "__main__":
    reader = ExtractMeta()

    # Ручной запрос
    manual_request = {'task': 'extract_meta',
                      'path': "./Data/PDF/text/text2.pdf"}
    
    reader.handle(manual_request)

    print(f"Мета-данные документа: {manual_request.get('meta')}")
