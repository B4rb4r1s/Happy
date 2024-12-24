
from Source.ExtractMeta import ExtractPDFMeta
from Source.PDFReader import TextExtractionHandler
from Source.Summarizer import SummaryGenerationHandler
from Source.NERer import NamedEntityRecognitionHandler


class Chain:
    def __init__(self):

        # Объявление обработчиков
        self.meta_extraction_handler = ExtractPDFMeta()
        self.text_extraction_handler = TextExtractionHandler()
        self.summary_generation_handler = SummaryGenerationHandler()
        self.NER_handler = NamedEntityRecognitionHandler()

        # Создание цепочки
        self.meta_extraction_handler.set_next(
            self.text_extraction_handler).set_next(
                self.summary_generation_handler).set_next(
                    self.NER_handler
                )

    # Добавление обработчиков
    #   не реализовано
    # def add_handler(self, handler):
    #     self.handlers.append(handler)

    def handle_request(self, request):
        self.meta_extraction_handler.handle(request)



if __name__ == '__main__':

    # Объявление обработчиков
    # text_extraction_handler = TextExtractionHandler()
    # summary_generation_handler = SummaryGenerationHandler()
    # NER_handler = NamedEntityRecognitionHandler()

    chain = Chain()    
    request = {'task': 'extract_meta',
               'path': './Data/PDF/text/text2.pdf'}

    chain.handle_request(request)
