# -*- coding: utf-8 -*-

import datetime
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import MBartTokenizer, MBartForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM

from Source.Handler import Handler

import sys
sys.stdout.flush()

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Установка параметров работы модели
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f'[{datetime.datetime.now()}][ DEBUG ] Computing using device - {device}')



# BART
MODEL_NAME = 'IlyaGusev/mbart_ru_sum_gazeta'
MODEL_PATH = 'Models/Summary/IlyaGusev--mbart_ru_sum_gazeta'
tokenizer = MBartTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = MBartForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)

# T5
# MODEL_NAME = 'utrobinmv/t5_summary_en_ru_zh_base_2048'
# MODEL_PATH = 'Models/Summary/utrobinmv--t5_summary_en_ru_zh_base_2048'
# tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
# model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)

# mT5
# MODEL_NAME = 'csebuetnlp/mT5_multilingual_XLSum'
# MODEL_PATH = 'Models/Summary/csebuetnlp--mT5_multilingual_XLSum'
# tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
# model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)

model.eval()


# Структура апроса:
# request{
#     task:           Текущая задача в цепочке
#     dataset_handle: Флаг, ***
#     file_format:    Формат документа (устанавливается в FileOverwiev.py)
#     meta:           Словарь метаинформации документа (устанавливается в ExtractMeta.py)
#     text:           Текстовый слой PDF-файла (устанавливается в DocReader.py)
#     text_tesseract: Текст извлеченный с помощью Tesseract (устанавливается в DocReader.py)
#     text_dedoc:     Текст извлеченный с помощью DeDoc (устанавливается в DocReader.py)
#     tables:         Таблицы выделенные DeDoc (устанавливается в DocReader.py)
# 
#     summary:        Краткое сгенерированное содержание (устанавливается в Summarizer.py)
#     big_summary:    Более полное сгенерированное содержание (устанавливается в Summarizer.py)
# 
#     entities:       Словарь сущность - класс сущности (устанавливается в NERer.py)
# }
class SummaryGenerationHandler(Handler):
    def handle(self, request, 
               n_words=None, 
               compression=None, 
               max_length=1000, 
               num_beams=3, 
               do_sample=False, 
               repetition_penalty=10.0, 
               no_repeat_ngram_size=4, 
               **kwargs):
        

        if 'text' in request and request['task'] == 'generate_summary' and request['summary_needed']:
            try:
                if request['text'] == '':
                    text = request['text_dedoc']
                    if request['tables']:
                        tables_texts = '\n\n'.join(['\n'.join([' '.join(row) for row in table]) for table in request['tables']])
                        text += tables_texts
                else:
                    text = request['text']
                if not text:
                    request['summary'] = ''
                    request['big_summary'] = ''
                    return super().handle(request)
                
                print(f"[{datetime.datetime.now()}][ DEBUG ] Text length: {len(text)} characters")
                
                # Define chunk size and calculate steps
                CHUNK_SIZE = 100 * 1024  # 3KB chunks
                num_steps = (len(text) // CHUNK_SIZE) + 1 if len(text) > CHUNK_SIZE else 0
                print(f'[ DEBUG ] Needed steps: {num_steps}')
                
                # Process text in chunks for large documents
                summary_parts = []
                
                for step in range(num_steps):
                    start = step * CHUNK_SIZE
                    end = start + CHUNK_SIZE
                    chunk = text[start:end]
                    print(f'[ DEBUG ] start: {start}, finish: {end}')

                    # Generate summary for each chunk
                    summary = self._generate_summary(
                        chunk, n_words, compression, 
                        max_length, num_beams, do_sample,
                        repetition_penalty, no_repeat_ngram_size
                    )
                    summary_parts.append(summary)

                if num_steps > 0:
                    big_summary = '\n'.join(summary_parts)
                    request['big_summary'] = big_summary
                    try:
                        final_summary = self._generate_summary(
                            big_summary, n_words, compression, 
                            max_length, num_beams, do_sample, 
                            repetition_penalty, no_repeat_ngram_size
                        )
                        request['summary'] = final_summary
                    except:
                        print(f'[ DEBUG ] Big summary is too long to summarize')
                        request['summary'] = ''
                else:
                    # Handle small documents directly
                    request['summary'] = self._generate_summary(
                        text, n_words, compression, max_length, num_beams,
                        do_sample, repetition_penalty,
                        no_repeat_ngram_size
                    )
                    request['big_summary'] = ''

                print(f"[ DEBUG ] SummaryGenerationHandler: Обработано")

                print(f"[{datetime.datetime.now()}][ DEBUG ] Summary generated: {request['summary'][:50]}")
                request['task'] = 'extract_entities'
                return super().handle(request)
            
            except Exception as err:
                print(f"[ {datetime.datetime.now()} ][ DEBUG ERROR SUMM ] Handling failed\n>>> {err}")
                return super().handle(request)
            
        elif not request['summary_needed']:
            request['task'] = 'extract_entities'
            request['summary'] = ''
            request['big_summary'] = ''
            print(f"[ DEBUG ] Task SummaryGenerationHandler is not needed")
            return super().handle(request)
             
        else:
            print(f"[ DEBUG ] Task SummaryGenerationHandler skipped >>> {request['task']}")
            return super().handle(request)

        
    def _generate_summary(
            self, text, n_words, compression, max_length,
            num_beams, do_sample, repetition_penalty,
            no_repeat_ngram_size, **kwargs
        ):
        if not text:
            return ''

        if n_words:
            # n_words - приблизительное кол-во слов, которые нужно сгенерировать
            text = '[{}] '.format(n_words) + text
        elif compression:
            # compression - приблизительное отношение объема аннотации 
            #               и оригинального текста.
            text = '[{0:.1g}] '.format(compression) + text

        prefix = 'summary big: '
        text = prefix + text

        inputs = tokenizer(text, 
                           return_tensors='pt', 
                           padding=True
                           ).to(device)

        # with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=num_beams,
            do_sample=do_sample,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            **kwargs
        )

        return tokenizer.decode(output[0], skip_special_tokens=True)
              
              
    
if __name__ == "__main__":
    sum_handler = SummaryGenerationHandler()
    
    # Создаем тестовый запрос с текстом
    request = {
        'task': 'generate_summary',
        'text': "Высота башни составляет 324 метра (1063 фута), примерно такая же высота, как у 81-этажного здания, и самое высокое сооружение в Париже. Его основание квадратно, размером 125 метров (410 футов) с любой стороны. Во время строительства Эйфелева башня превзошла монумент Вашингтона, став самым высоким искусственным сооружением в мире, и этот титул она удерживала в течение 41 года до завершения строительство здания Крайслер в Нью-Йорке в 1930 году. Это первое сооружение которое достигло высоты 300 метров. Из-за добавления вещательной антенны на вершине башни в 1957 году она сейчас выше здания Крайслер на 5,2 метра (17 футов). За исключением передатчиков, Эйфелева башня является второй самой высокой отдельно стоящей структурой во Франции после виадука Мийо."}
    
    # Запускаем обработку
    sum_handler.handle(request)
    
    print(f"Краткое содержние: {request.get('summery')}")
