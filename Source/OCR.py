import io
import pytesseract
from pdf2image import convert_from_path
 
def extract_text_from_img(path, file_format):
#     pages = convert_from_path(path, 1000)
     
#     # Extract text from each page using Tesseract OCR
#     text_data = ''
#     for page in pages:
#         text = pytesseract.image_to_string(page, lang='eng+rus')
#         text_data += text + '\n'
     
#     # Return the text data
#     return text_data

    text_tesseract = ''
    try:
        if file_format in ['pdf', 'jpg', 'jpeg', 'png']:
            if file_format == 'pdf':
                try:
                    pages = convert_from_path(path, 1000)
                except Exception as err:
                    print(f'[ DEBUG ERROR ] PDF is too big to process\n>>> {err}')
                    return ''

            if file_format in ['jpg', 'jpeg', 'png']:
                pages = [path]

            # Extract text from each page using Tesseract OCR
            text_tesseract = ''
            for page in pages:
                text = pytesseract.image_to_string(page, lang='eng+rus')
                text_tesseract += text + '\n'
    
    except Exception as err:
        print(f'[ DEBUG ERROR OCR] Error during OCR\n>>> {err}')
    
    return text_tesseract
    
    
    

if __name__ == '__main__':
    text = extract_text_from_img('Data/PDF/scan/scan1.pdf')
    print(text)