import PyPDF2
from datetime import datetime

from Source.Handler import Handler

class ExtractPDFMeta(Handler):
    def handle(self, request):
        '''
        Текущий запрос:
            request = {
                'task': 'extract_meta',
                'path': './Data/PDF/text/text2.pdf'}
        '''
        if request['task'] == 'extract_meta':
            with open(request['path'], 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                meta = reader.metadata

            meta_info = {
                'author': meta.get('/Author', 'Unknown'),
                'creator': meta.get('/Creator', 'Unknown'),
                'title': meta.get('/Title', 'Unknown'),
                'subject': meta.get('/Subject', 'Unknown'),
                'creation_date': self.convert_date(meta.get('/CreationDate', 'Unknown')),
                'modification_date': self.convert_date(meta.get('/ModificationDate', 'Unknown')),
                'producer': meta.get('/Producer', 'Unknown')
            }

            request['meta'] = meta_info

            print(f"ExtractPDFMeta: Обработано")
            print(request['meta'])
            request['task'] = 'extract_text'
            return super().handle(request)
        else:
            print("Error during handing (Mets)")
            return super().handle(request)
        

    def convert_date(self, date):
        if date.startswith('D:'):
            date = date[2:]

        try:
            parsed_date = datetime.strptime(date[:14], '%Y%m%d%H%M%S')
            readable_date = parsed_date.strftime('%d-%m-%Y %H:%M:%S')
            return readable_date
        except ValueError:
            return "Unknown"
        


if __name__ == "__main__":
    reader = ExtractPDFMeta()

    # Ручной запрос
    manual_request = {'task': 'extract_meta',
                      'path': "./Data/PDF/text/text2.pdf"}
    
    reader.handle(manual_request)

    print(f"Мета-данные документа: {manual_request.get('meta')}")
