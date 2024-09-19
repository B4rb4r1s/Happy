import io
import pytesseract
from pdf2image import convert_from_path
 
def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path, 900)
     
    # Extract text from each page using Tesseract OCR
    text_data = ''
    for page in pages:
        text = pytesseract.image_to_string(page, lang='eng+rus')
        text_data += text + '\n'
     
    # Return the text data
    return text_data
 
text = extract_text_from_pdf('../Data/PDF/scan/scan1.pdf')
print(text)