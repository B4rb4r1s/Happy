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
            text_tesseract = None
            text_dedoc = None
            all_text = ''
            try:
                if request['file_format'] == 'pdf':
                    with open(request['path'], 'rb') as file:
                        reader = pymupdf.open(file)

                        for page in reader:
                            all_text += page.get_text()

                        # if all_text == '':
                    text_tesseract, text_dedoc = extract_text_from_img(request['path'], request['file_format'])


                elif request['file_format'] in ["jpg", "jpeg", "png"]:
                    print('[ DEBUG ] Extracting from IMG scan')
                    text_tesseract, text_dedoc = extract_text_from_img(request['path'], request['file_format'])

                elif request['file_format'] in ["doc", "docx"]:
                    print('[ DEBUG ] Extracting from DOC scan')
                    text_tesseract, text_dedoc = extract_text_from_img(request['path'], request['file_format'])

                request['text'] = all_text
                request['text_tesseract'] = text_tesseract
                request['text_dedoc'] = text_dedoc

                print(f"[ DEBUG ] TextExtractionHandler: Обработано")
                print(request['text'][:50])
                request['task'] = 'generate_summary'
                return super().handle(request)
            
            except Exception as err:
                print(f"[{datetime.now()}][ DEBUG ERROR ExtrMeta ] Handling failed\n>>> {err}")
                return super().handle(request)
        
        elif request['dataset_handle'] == True:
            print('[ DEBUG ] Extracting from scan')
            _, all_text = extract_text_from_img(request['path'], request['file_format'])
            
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



