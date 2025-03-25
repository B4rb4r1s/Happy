import subprocess
import os
import re
import tqdm
import time
import logging
import config

import psycopg2
import torch



class BaseSummarizer:
    def __init__(self, model_path, device='cpu'):
        self.model_path = model_path
        self.column = None
        self.device = device 
        self.tokenizer = None
        self.model = None

        self.tokenization_args = {}
        self.generation_args = {}

        self.encodings = {'input_ids': torch.tensor([[]])}
        self.set_model()

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
        num_tokens = len(tokens)
        batch_size = 1024
        num_batches = num_tokens // batch_size
        if num_tokens % batch_size != 0:
            num_batches += 1
        # print(self.tokenizer.encode(text))

        summary = []
        start = time.time()
        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, num_tokens)
            batch_text = ' '.join(text.split(' ')[start_index:end_index])

            input_ids = self.tokenizer(batch_text, **self.tokenization_args)["input_ids"].to(self.device)
            self.set_generation_arguments()

            output_ids = self.model.generate(input_ids=input_ids, **self.generation_args).to(self.device)
            summary.append(self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0])

        stop = time.time() - start
        with open('Happy/Utility/Summarizer/logs.txt', 'a') as f:
            f.write(f'\tDocment with {len(config.PROCESSING_HANDLER(text))} symbols on {len(tokens)} tokens processed in {stop} sec\n')

        return ' '.join(summary)
    


    def run_and_load(self, db_handler):
        print(f'Computing using GPU') if self.device=='cuda:0' else print(f'Computing using CPU')
        
        with open('Happy/Utility/Summarizer/logs.txt', 'a') as f:
            f.write(f'Model: {self.column},\tcomputing using {self.device}\n')

        # extra_condition = '{SUMMARIES_TABLE}.lingvo_summary IS NOT NULL'
        extra_condition = None
        dataset = db_handler.get_db_table(table=config.SUMMARIES_TABLE, 
                                          column=self.column, 
                                          extra_condition=extra_condition)
        for doc_id, text in tqdm.tqdm(dataset, desc=f"Processing {self.column}"):
            try:
                print(f"Обработка документа {doc_id}")
                processed_text = config.PROCESSING_HANDLER(text)
                summary = self.summarize_text(processed_text)
                db_handler.upload_summary(column=self.column, doc_id=doc_id, text=summary)
            except Exception as err:
                print(f"[ ERROR ] Документ {doc_id}: {err}")
        return
