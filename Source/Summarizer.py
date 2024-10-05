# -*- coding: utf-8 -*-

import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import MBartTokenizer, MBartForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForCausalLM

from Source.Handler import Handler

# Установка параметров работы модели
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f'[ DEBUG ] Computing using device - {device}')

# T5
# MODEL_NAME = 'cointegrated/rut5-base-absum'
# MODEL_PATH = 'Source/Models/T5'
# tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
# model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)

# BART
MODEL_NAME = 'IlyaGusev/mbart_ru_sum_gazeta'
MODEL_PATH = 'Source/Models/MBART'
tokenizer = MBartTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = MBartForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)

# GPT
# MODEL_NAME = 'IlyaGusev/rugpt3medium_sum_gazeta'
# MODEL_PATH = 'Source/Models/GPT'
# tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
# model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

model.eval()


class SummaryGenerationHandler(Handler):
    def handle(self, request, n_words=None, compression=None, 
               max_length=1000, num_beams=3, do_sample=False, 
               repetition_penalty=10.0, no_repeat_ngram_size=4, **kwargs):
        '''
        Текущий запрос:
            request = ['text']
        '''
        if 'text' in request and request['task'] == 'generate_summary':
            text = request['text']
            if text != '':

                if n_words:
                    # n_words - приблизительное кол-во слов, которые нужно сгенерировать
                    text = '[{}] '.format(n_words) + text
                elif compression:
                    # compression - приблизительное отношение объема аннотации 
                    #               и оригинального текста.
                    text = '[{0:.1g}] '.format(compression) + text

                x = tokenizer(text, return_tensors='pt', padding=True).to(device)
                with torch.inference_mode():
                    out = model.generate(
                        **x, 
                        max_length=max_length, num_beams=num_beams, 
                        do_sample=do_sample, repetition_penalty=repetition_penalty, 
                        no_repeat_ngram_size = no_repeat_ngram_size,
                        **kwargs
                    )
            
                request['summary'] = tokenizer.decode(out[0], skip_special_tokens=True)
            else:
                request['summary'] = ''
            
            print(f"[ Debug ] TextSummarizationHandler: Обработано")
            print(request['summary'])
            request['task'] = 'extract_entities'
            return super().handle(request)
        else:
            print("[ Debug Error ] Error during handing (Summary)")
            return super().handle(request)



if __name__ == "__main__":
    sum_handler = SummaryGenerationHandler()
    
    # Создаем тестовый запрос с текстом
    request = {
        'task': 'generate_summary',
        'text': "Высота башни составляет 324 метра (1063 фута), примерно такая же высота, как у 81-этажного здания, и самое высокое сооружение в Париже. Его основание квадратно, размером 125 метров (410 футов) с любой стороны. Во время строительства Эйфелева башня превзошла монумент Вашингтона, став самым высоким искусственным сооружением в мире, и этот титул она удерживала в течение 41 года до завершения строительство здания Крайслер в Нью-Йорке в 1930 году. Это первое сооружение которое достигло высоты 300 метров. Из-за добавления вещательной антенны на вершине башни в 1957 году она сейчас выше здания Крайслер на 5,2 метра (17 футов). За исключением передатчиков, Эйфелева башня является второй самой высокой отдельно стоящей структурой во Франции после виадука Мийо."}
    
    # Запускаем обработку
    sum_handler.handle(request)
    
    print(f"Краткое содержние: {request.get('summery')}")
