
from Source.FileOverwiev import FileOverwiever
from Source.ExtractMeta import ExtractMeta
from Source.PDFReader import TextExtractionHandler
from Source.Summarizer import SummaryGenerationHandler
from Source.NERer import NamedEntityRecognitionHandler


class Chain:
    def __init__(self):

        # Объявление обработчиков
        self.file_overwiever = FileOverwiever()
        self.meta_extraction_handler = ExtractMeta()
        self.text_extraction_handler = TextExtractionHandler()
        self.summary_generation_handler = SummaryGenerationHandler()
        self.NER_handler = NamedEntityRecognitionHandler()

        # Создание цепочки
        self.file_overwiever.set_next(
            self.meta_extraction_handler).set_next(
                self.text_extraction_handler).set_next(
                    self.summary_generation_handler).set_next(
                        self.NER_handler)

    # Добавление обработчиков
    #   не реализовано
    # def add_handler(self, handler):
    #     self.handlers.append(handler)

    def handle_request(self, request):
        self.file_overwiever.handle(request)



if __name__ == '__main__':

    # Объявление обработчиков
    # text_extraction_handler = TextExtractionHandler()
    # summary_generation_handler = SummaryGenerationHandler()
    # NER_handler = NamedEntityRecognitionHandler()

    chain = Chain()    
    request = {'task': 'overwieve',
               'path': './Data/PDF/text/text2.pdf'}

    chain.handle_request(request)
