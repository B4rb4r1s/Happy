from Source.Summarizer.SummaryLoader import BaseSummarizer

from transformers import T5ForConditionalGeneration, AutoTokenizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import MBartTokenizer, MBartForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM

MODEL_PATH = '/app/Models/Summary'

class Omega_summarizer(BaseSummarizer):
    def set_model(self):
        if self.model_path == f'{MODEL_PATH}/csebuetnlp--mT5_multilingual_XLSum':
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path).to(self.device)
            self.column='mt5_summary'
            self.tokenization_args = {
                'return_tensors':     "pt",
                'padding':            "max_length",
                'truncation':         True,
                # 'max_length':         512
            }
            return True

        elif self.model_path == f'{MODEL_PATH}/IlyaGusev--mbart_ru_sum_gazeta':
            self.tokenizer = MBartTokenizer.from_pretrained(self.model_path)
            self.model = MBartForConditionalGeneration.from_pretrained(self.model_path).to(self.device)
            self.column='mbart_summary'
            self.tokenization_args = {
                'return_tensors':     "pt",
                'padding':            "max_length",
                'truncation':         True,
                # 'max_length':         900
            }
            return True

        elif self.model_path == f'{MODEL_PATH}/IlyaGusev--rut5_base_sum_gazeta':
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_path).to(self.device)
            self.column='rut5_summary'
            self.tokenization_args = {
                'add_special_tokens':   True,
                'max_length':           600,
                'padding':              "max_length",
                'truncation':           True,
                'return_tensors':       "pt"
            }
            return True

        elif self.model_path == f'{MODEL_PATH}/utrobinmv--t5_summary_en_ru_zh_base_2048':
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_path).to(self.device)
            self.column='t5_summary'
            self.tokenization_args = {
                'return_tensors':     "pt",
                'padding':            "max_length",
                'truncation':         True,
                'add_special_tokens': True,
                # 'max_length':         600
            }
            return True
            
        else:
            print(f'Unknown model', flush=True)

    def set_generation_arguments(self):
        if self.model_path == f'{MODEL_PATH}/csebuetnlp--mT5_multilingual_XLSum':
            self.generation_args = {
                # 'max_length':             512,
                'no_repeat_ngram_size':   2,
                'num_beams':              4
            }
        elif self.model_path == f'{MODEL_PATH}/IlyaGusev--mbart_ru_sum_gazeta':
            self.generation_args = {
                'no_repeat_ngram_size':   4
            }

        elif self.model_path == f'{MODEL_PATH}/IlyaGusev--rut5_base_sum_gazeta':
            self.generation_args = {
                'no_repeat_ngram_size':   4
            }

        elif self.model_path == f'{MODEL_PATH}/utrobinmv--t5_summary_en_ru_zh_base_2048':
            self.generation_args = {
                'no_repeat_ngram_size':   4
            }

        else:
            print(f'Unknown model', flush=True)

