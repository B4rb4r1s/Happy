import io
import pytesseract
from pdf2image import convert_from_path

import traceback

from dedoc import DedocManager
from dedoc.attachments_handler import AttachmentsHandler
from dedoc.converters import DocxConverter, PNGConverter, ConverterComposition
from dedoc.metadata_extractors import BaseMetadataExtractor, MetadataExtractorComposition
from dedoc.readers import DocxReader, PdfAutoReader, PdfImageReader, ReaderComposition
from dedoc.structure_extractors import DefaultStructureExtractor, StructureExtractorComposition
from dedoc.structure_constructors import TreeConstructor, StructureConstructorComposition

dedoc_manager = DedocManager(
    manager_config={
        "attachments_handler": AttachmentsHandler(),
        "converter": ConverterComposition([DocxConverter(), PNGConverter()]),
        "reader": ReaderComposition([DocxReader(), PdfAutoReader(), PdfImageReader()]),
        "structure_extractor": StructureExtractorComposition(extractors={DefaultStructureExtractor.document_type: DefaultStructureExtractor()}, default_key=DefaultStructureExtractor.document_type),
        "structure_constructor": StructureConstructorComposition(constructors={"tree": TreeConstructor()}, default_constructor=TreeConstructor()),
        "document_metadata_extractor": MetadataExtractorComposition([BaseMetadataExtractor()])
    }
)

def tesseract_scan(path, file_format):
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

    return text_tesseract

    
def concat_subpara(full, para):
    # full = []
    full.append(para.text)
    if len(para.subparagraphs) > 0:
        for par in para.subparagraphs:
            concat_subpara(full, par)
    return full
def dedoc_scan(path):
    text_dedoc = ''
    parsed_document = dedoc_manager.parse(path)
    rec = concat_subpara([], parsed_document.content.structure)
    text_dedoc = '\n'.join(rec)

    return text_dedoc

 
def extract_text_from_img(path, file_format):
    text_tesseract = None
    text_dedoc = None
    try:
        if file_format in ['pdf', 'jpg', 'jpeg', 'png']:
            text_tesseract = tesseract_scan(path, file_format)
            text_dedoc = dedoc_scan(path)
        elif file_format in ["doc", "docx"]:
            text_tesseract = None
            text_dedoc = dedoc_scan(path)
    
    except Exception as err:
        print(f'[ DEBUG ERROR OCR] Error during OCR\n>>> {err}')
        print(f'>>> {traceback.format_exc()}', flush=True)
    
    return text_tesseract, text_dedoc
    
    
    

if __name__ == '__main__':
    text = extract_text_from_img('Data/PDF/scan/scan1.pdf')
    print(text)