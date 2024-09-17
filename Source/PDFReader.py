# импортирование библиотек
import os
import re
import PyPDF2

from Source.Handler import Handler


class TextExtractionHandler(Handler):
    def handle(self, request):
        '''
        Текущий запрос:
            request = {
                'task': 'extract_text',
                'path': './Data/PDF/text/text2.pdf'}
        '''
        if request['task'] == 'extract_text':
            with open(request['path'], 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                all_text = ''

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    all_text += page.extract_text()

                # clean_text = re.sub(r'(?<=[а-яa-z,-])\s\r?\n(?=[а-яА-Яa-zA-Z])', '', all_text)
                clean_text = all_text
                request['text'] = clean_text

            print(f"TextExtractionHandler: Обработано")
            print(request['text'])
            request['task'] = 'generate_summary'
            return super().handle(request)
        else:
            print("Error during handing (Reader)")
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

    print(f"Содержние документа: {manual_request.get('text')}")
    # texts = extract_text_from_pdfs_in_folder("./Data/PDF/text/")

    # for filename, text in texts.items():
    #     print(f"--- Содержимое файла: {filename} ---\n")
    #     print(text)
    #     print("\n")



