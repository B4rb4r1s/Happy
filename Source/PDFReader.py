# импортирование библиотек
import os
import re
import PyPDF2
import pymupdf 
from datetime import datetime

from Source.Handler import Handler
from Source.OCR import extract_text_from_img


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
            try:
                with open(request['path'], 'rb') as file:
                    reader = pymupdf.open(file)
                    all_text = ''

                    for page in reader:
                        all_text += page.get_text()

                    # for page_num in range(len(reader.pages)):
                    #     page = reader.pages[page_num]
                    #     all_text += page.extract_text()

                    if all_text == '':
                        try:
                            print('[ DEBUG ] Extracting from scan')
                            all_text = extract_text_from_img(request['path'], request['file_format'])
                        except:
                            print("[ DEBUG ERROR ExtrMeta ] Error during extracting from scan")
                            all_text = ''

                    # all_text = re.sub(r'(?<=[а-яa-z,-])\s\r?\n(?=[а-яА-Яa-zA-Z])', '', all_text)
                    request['text'] = all_text

                print(f"[ DEBUG ] TextExtractionHandler: Обработано")
                print(request['text'][:50])
                request['task'] = 'generate_summary'
                return super().handle(request)
            
            except Exception as err:
                print(f"[{datetime.now()}][ DEBUG ERROR ExtrMeta ] Handling failed\n>>> {err}")
                return super().handle(request)
        
        elif request['dataset_handle'] == True:
            print('[ DEBUG ] Extracting from scan')
            all_text = extract_text_from_img(request['path'], request['file_format'])
            
            request['text'] = all_text

            print(f"[ DEBUG ] TextExtractionHandler: Обработано")
            # print(request['text'])
            request['task'] = 'generate_summary'
            return super().handle(request)
            
        else:
            print(f"[ DEBUG ] Task TextExtractionHandler skipped >>> {request['task']}")
            request['task'] = 'generate_summary'
            return super().handle(request)


    # Функция чтения ВСЕХ PDF-файлов в папке
    def extract_text_from_pdfs_in_folder(self, folder_path):
        extracted_text = {}

        # Проходим по всем файлам в папке
        for filename in os.listdir(folder_path):
            if filename.endswith(".pdf"):  # Проверяем, является ли файл PDF
                pdf_path = os.path.join(folder_path, filename)
                text = self.extract_text_from_pdf(pdf_path)
                extracted_text[filename] = text

        return extracted_text



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



