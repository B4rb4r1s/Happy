from SummaryLoader import BaseSummarizer
import config

from transformers import T5ForConditionalGeneration, AutoTokenizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import MBartTokenizer, MBartForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM


class mT5_Summarizer(BaseSummarizer):
    def set_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)

    def summarize_text(self, text):
        input_ids = self.tokenizer(
            [config.PROCESSING_HANDLER(text)],
            # text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512
        )["input_ids"]

        output_ids = self.model.generate(
            input_ids=input_ids,
            max_length=512,
            no_repeat_ngram_size=2,
            num_beams=4
        )[0]

        mt5_summary = self.tokenizer.decode(
            output_ids, 
            skip_special_tokens=True, 
            clean_up_tokenization_spaces=False
        )
        return mt5_summary



class MBART_Summarizer(BaseSummarizer):
    def set_model(self):
        self.tokenizer = MBartTokenizer.from_pretrained(self.model_path)
        self.model = MBartForConditionalGeneration.from_pretrained(self.model_path).to(device)
        
    def summarize_text(self, text, max_source_tokens_count=600):
        input_ids = self.tokenizer(
            PROCESSING_HANDLER(text),
            # text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=max_source_tokens_count
        )["input_ids"].to(device)
            
        output_ids = self.model.generate(
            input_ids=input_ids,
            no_repeat_ngram_size=4
        )

        mbart_summary = self.tokenizer.batch_decode(
            output_ids, 
            skip_special_tokens=True
        )[0]
        return mbart_summary



class ruT5_Summarizer(BaseSummarizer):
    def set_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
        
    def summarize_text(self, text):
        input_ids = self.tokenizer(
            [PROCESSING_HANDLER(text)],
            # [text],
            max_length=600,
            add_special_tokens=True,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )["input_ids"]

        output_ids = self.model.generate(
            input_ids=input_ids,
            no_repeat_ngram_size=4
        )[0]

        rut5_summary = self.tokenizer.decode(
            output_ids, 
            skip_special_tokens=True
        )
        return rut5_summary



class T5_Summarizer(BaseSummarizer):
    def set_model(self):
        self.tokenizer = T5Tokenizer.from_pretrained(MODELS[3])
        self.model = T5ForConditionalGeneration.from_pretrained(MODELS[3])
        self.model.eval()
        self.model.to(device)

    def summarize_text(self, text):
        prefix = 'summary big: '
        src_text = prefix + PROCESSING_HANDLER(text),
        input_ids = self.tokenizer(src_text, return_tensors="pt")

        generated_tokens = self.model.generate(**input_ids.to(device))

        t5_summary = self.tokenizer.batch_decode(
            generated_tokens, 
            skip_special_tokens=True
        )[0]
        return t5_summary
        