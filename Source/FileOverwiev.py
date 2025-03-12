import os
import sys
from datetime import datetime

from Source.Handler import Handler


sys.stdout.flush()


# Структура апроса:
# request{
#     task:           Текущая задача в цепочке
#     dataset_handle: Флаг, ***
# 
#     file_format:    Формат документа (устанавливается в FileOverwiev.py)
# 
#     meta:           Словарь метаинформации документа (устанавливается в ExtractMeta.py)
#     text:           Текстовый слой PDF-файла (устанавливается в DocReader.py)
#     text_tesseract: Текст извлеченный с помощью Tesseract (устанавливается в DocReader.py)
#     text_dedoc:     Текст извлеченный с помощью DeDoc (устанавливается в DocReader.py)
#     tables:         Таблицы выделенные DeDoc (устанавливается в DocReader.py)
#     summary:        Краткое сгенерированное содержание (устанавливается в Summarizer.py)
#     big_summary:    Более полное сгенерированное содержание (устанавливается в Summarizer.py)
#     entities:       Словарь сущность - класс сущности (устанавливается в NERer.py)
# }
class FileOverwiever(Handler):
    def handle(self, request):
        if request['task'] == 'overwiev':
            try:
                file_format = request['path'][request['path'].rfind('.')+1:].lower()
                print(f"[ {datetime.now()} ][ DEBUG ] FileOverwiev: Обработано\n>>> {file_format}")

                request['file_format'] = file_format
                request['task'] = 'extract_meta'
                return super().handle(request)
            
            except Exception as err:
                print(f"[ {datetime.now()} ][ DEBUG ERROR FileOW ] Handling failed\n>>> {err}")
        else:
            print(f"[ DEBUG ] Task FileOverwiev skipped >>> {request['task']}")
            return super().handle(request)

    


if __name__ == '__main__':
    overwiever = FileOverwiever()

    # Ручной запрос
    manual_request = {'task': 'overwiev',
                      'path': "./Data/PDF/text/text2.pdf"}
    
    overwiever.handle(manual_request)

    print(f"Формат документа: {manual_request.get('format')}")