import re
import torch

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
# DEVICE = "cpu"

SUMMARY_MODELS = [
    './Happy/Models/Summary/csebuetnlp--mT5_multilingual_XLSum',
    './Happy/Models/Summary/IlyaGusev--mbart_ru_sum_gazeta',
    './Happy/Models/Summary/IlyaGusev--rut5_base_sum_gazeta',
    './Happy/Models/Summary/utrobinmv--t5_summary_en_ru_zh_base_2048'
]

SUMMARIES_TABLE = 'elibrary_dataset_summaries'
PROCESSING_HANDLER = lambda k: re.sub(r' {2,}', ' ', re.sub('\n+', '\n', re.sub(r'(?<!\n)\n(?!\n)', ' ', re.sub('-\n', '', k.strip()))))
