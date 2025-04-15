import subprocess
import os
import re
import tqdm
import time
import logging
import Source.Summarizer.config as config

import psycopg2
import torch



class BaseSummarizer:
    def __init__(self, model_path, device='cuda:1'):
        self.model_path = model_path
        self.column = None
        self.device = device or "cuda:1" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None

        self.tokenization_args = {}
        self.generation_args = {}

        self.encodings = {'input_ids': torch.tensor([[]])}
        self.set_model()

        self.logger_path = '/app/Source/Summarizer/logs.txt'

    def logger(self, message, level):
        padding = '\t'*level
        with open(self.logger_path, 'a') as f:
            f.write(f'{padding}{message}')

    def set_model(self):
        raise NotImplementedError("Метод set_model должен быть реализован в подклассе.")
    
    def set_generation_arguments(self):
        raise NotImplementedError("Метод set_generation_arguments должен быть реализован в подклассе.")
    
    def decode(self, generated_tokens, **kwargs):
        return self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
            **kwargs
        )[0]
    


    def summarize_text(self, text):
        tokens = self.tokenizer.encode(config.PROCESSING_HANDLER(text))
        
        words = text.split(' ')
        num_tokens = len(tokens)
        batch_size = 1024
        num_batches = num_tokens // batch_size
        if num_tokens % batch_size != 0:
            num_batches += 1
        # print(self.tokenizer.encode(text))

        token_chunks = [tokens[i:i+batch_size] for i in range(0, len(tokens), batch_size)]
        text_chunks = [self.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in token_chunks]

        summary = []
        start = time.time()
        for text_chunk in text_chunks:

            input_ids = self.tokenizer(text_chunk, **self.tokenization_args)["input_ids"].to(self.device)
            self.set_generation_arguments()

            output_ids = self.model.generate(input_ids=input_ids, **self.generation_args).to(self.device)
            summary.append(self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0])

        stop = time.time() - start
        self.logger(f'with {len(config.PROCESSING_HANDLER(text))} symbols, {len(words)} words and {len(tokens)} tokens processed in {stop} sec\n', 2)

        return ' '.join(summary)
    


    def run_and_load(self, db_handler, extra_condition=None):
        print(f'Computing using GPU') if 'cuda' in self.device else print(f'Computing using CPU')
        
        self.logger(f'Task - run_and_load\n', 0)
        self.logger(f'Model: {self.column},\tcomputing using {self.device}\n', 1)

        # extra_condition = '{SUMMARIES_TABLE}.lingvo_summary IS NOT NULL'
        dataset = db_handler.get_db_table(table=conconfigfigur.SUMMARIES_TABLE, 
                                          column=self.column, 
                                          extra_condition=extra_condition)
        for doc_id, text in dataset:
            try:
                print(f"Обработка документа {doc_id}")
                self.logger(f'Document: {doc_id}\t', 2)
                processed_text = config.PROCESSING_HANDLER(text)
                summary = self.summarize_text(processed_text)
                db_handler.upload_summary(column=self.column, doc_id=doc_id, text=summary)
            except Exception as err:
                print(f"[ ERROR ] Документ {doc_id}: {err}")

        self.logger(f'Model: {self.column}, all documents processed!\n', 1)
        return
