import os
import sys
from datetime import datetime

from Source.Handler import Handler


sys.stdout.flush()

class FileOverwiever(Handler):
    def handle(self, request):
        '''
        Текущий запрос:
            request = {
                'task': 'overwiev',
                'path': './Data/*.*'}
        '''
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