import os
import sys
from datetime import datetime

from Handler import Handler


sys.stdout.flush()

class FileOverwiever(Handler):
    def handle(self, request):
        '''
        Текущий запрос:
            request = {
                'task': 'overwiev',
                'path': './Data/*.*'}
        '''

        file_format = request['path'][request['path'].rfind('.')+1:].lower()

        print(f"[{datetime.now()}][ Debug ] FileOverwiev: Обработано")
        print(f'{file_format}')
        
        request['task'] = 'extract_meta'
        request['format'] = file_format
        return super().handle(request)
    


if __name__ == '__main__':
    overwiever = FileOverwiever()

    # Ручной запрос
    manual_request = {'task': 'overwiev',
                      'path': "./Data/PDF/text/text2.pdf"}
    
    overwiever.handle(manual_request)

    print(f"Формат документа: {manual_request.get('format')}")