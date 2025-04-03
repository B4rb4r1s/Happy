import tqdm

import config
from SpellCheck import BaseSpellCorrector
# import DatabaseHandler

from transformers import T5ForConditionalGeneration, AutoTokenizer
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import AutoModelForSeq2SeqLM, T5TokenizerFast

# './Happy/Models/SpellCheck/ai-forever--FRED-T5-large-spell',
# './Happy/Models/SpellCheck/ai-forever--RuM2M100-1.2B',
# './Happy/Models/SpellCheck/ai-forever--sage-fredt5-distilled-95m',
# './Happy/Models/SpellCheck/ai-forever--sage-fredt5-large',
# './Happy/Models/SpellCheck/ai-forever--sage-m2m100-1.2B'
# './Happy/Models/SpellCheck/UrukHan--t5-russian-spell'

# fre_t5_large
# rum2m100
# sage_fredt5_distilled
# sage_fredt5_large
# sage_m2m100

class Omage_corrector(BaseSpellCorrector):
    def set_model(self):
        if self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--FRED-T5-large-spell':
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_path).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, eos_token="</s>")
            self.column = 'fred_t5_large'
            self.tokenization_args = {}
            return True
        
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--RuM2M100-1.2B':
            self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_path).to(self.device)
            self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_path, src_lang="ru", tgt_lang="ru")
            self.column = 'rum2m100'
            self.tokenization_args = {}
            return True
        
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-fredt5-distilled-95m' or \
             self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-fredt5-large':
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.column = 'sage_fredt5_distilled' if self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-fredt5-distilled-95m' else 'sage_fredt5_large'
            self.tokenization_args = {
                'max_length':           None, 
                'padding':              "longest", 
                'truncation':           False
            }
            return True
        
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-m2m100-1.2B':
            self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_path).to(self.device)
            self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_path, src_lang="ru", tgt_lang="ru")
            self.column = 'sage_m2m100'
            self.tokenization_args = {}
            return True
        
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/UrukHan--t5-russian-spell':
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path).to(self.device)
            self.tokenizer = T5TokenizerFast.from_pretrained(self.model_path)
            self.column = 't5_russ'
            self.tokenization_args = {
                'padding': "longest",
                'max_length': config.MAX_INPUT,
                'truncation': True
            }
            return True
        
        else:
            config.logger.debug(f"[ ERROR ] Unknown model")
            return False
        
    def set_generation_arguments(self):
        if self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--FRED-T5-large-spell':
            self.generation_args = {
                # 'max_new_tokens':       len(self.text.split()),
                'max_length':           self.encodings["input_ids"].size(1) * 1.5,
                'eos_token_id':         self.tokenizer.eos_token_id, 
                'early_stopping':       False # Debug
            }
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--RuM2M100-1.2B':
            self.generation_args = {
                'forced_bos_token_id':  self.tokenizer.get_lang_id("ru")
                }
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-fredt5-distilled-95m' or \
             self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-fredt5-large':
            self.generation_args = {
                'low_cpu_mem_usage':    True,
                'max_length':           self.encodings["input_ids"].size(1) * 1.5
            }
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/ai-forever--sage-m2m100-1.2B':
            self.generation_args = {
                'forced_bos_token_id':  self.tokenizer.get_lang_id("ru")
            }
        elif self.model_path == './DocumentAnalysisSystem/Models/SpellCheck/UrukHan--t5-russian-spell':
            self.generation_args = {}




class FRED_T5_corrector(BaseSpellCorrector):
    def set_model(self):
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, eos_token="</s>")
        collumn = 'fred_t5_large_spell'

    def correct_text(self, text):
        prefix = "Исправь: "
        text = prefix + text

        encodings = self.tokenize(text)

        generated_tokens = self.model.generate(
            **encodings, 
            max_new_tokens=len(text.split()),
            eos_token_id=self.tokenizer.eos_token_id, 
            early_stopping=True)
        
        correttion = self.decode(generated_tokens)
        return correttion


class RuM2M100_corrector(BaseSpellCorrector):
    def set_model(self):
        self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_path)
        self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_path, src_lang="ru", tgt_lang="ru")
        collumn = 'rum2m100'

    def correct_text(self, text):
        encodings = self.tokenize(text)

        generated_tokens = self.model.generate(
            **encodings, 
            forced_bos_token_id=self.tokenizer.get_lang_id("ru"))
        
        correttion = self.decode(generated_tokens)
        return correttion


class sage_FREDT5_corrector(BaseSpellCorrector):
    def set_model(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        collumn = 'sage_fredt5_distilled'
        collumn = 'sage_fredt5_large'
        
    def correct_text(self, text):
        encodings = self.tokenize(
            text,
            max_length=None, 
            padding="longest", 
            truncation=False)
        
        generated_tokens = self.model.generate(
            **encodings.to(self.model.device),
            low_cpu_mem_usage=True,
            max_length = encodings["input_ids"].size(1) * 1.5)
        
        correttion = self.decode(generated_tokens)
        return correttion


class sage_M2M100_corrector(BaseSpellCorrector):
    def set_model(self):
        self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_path)
        self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_path, src_lang="ru", tgt_lang="ru")
        collumn = 'sage_m2m100'

    def correct_text(self, text):
        encodings = self.tokenize(text)

        generated_tokens = self.model.generate(
            **encodings, 
            forced_bos_token_id=self.tokenizer.get_lang_id("ru"))
        
        correttion = self.decode(generated_tokens)
        return correttion


class T5_russ_corrector(BaseSpellCorrector):
    def set_model(self):
        self.tokenizer = T5TokenizerFast.from_pretrained(self.model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)

    def correct_text(self, text):
        encodings = self.tokenize(
            text,
            padding="longest",
            max_length=config.MAX_INPUT,
            truncation=True)
        
        generated_tokens = self.model.generate(**encodings) 

        correttion = self.decode(generated_tokens)
        return correttion



if __name__ == '__main__':
    # corrector = T5_russ_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')
    # print('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.\n')
    # text = corrector.correct_text('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.')
    # print(text)
    
    corr = Omage_corrector('./Happy/Models/SpellCheck/ai-forever--FRED-T5-large-spell')
    corr.correct_text('я тебя люблб!')