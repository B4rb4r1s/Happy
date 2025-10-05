import re
import torch

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
# DEVICE = "cpu"

OFFLINEUSE = True


if OFFLINEUSE:
    #  Offline use
    SUMMARY_MODELS = [
    '/app/Models/Summary/csebuetnlp--mT5_multilingual_XLSum',
    '/app/Models/Summary/IlyaGusev--mbart_ru_sum_gazeta',
    '/app/Models/Summary/IlyaGusev--rut5_base_sum_gazeta',
    '/app/Models/Summary/utrobinmv--t5_summary_en_ru_zh_base_2048',
    
    # Local use
    # './Happy/Models/Summary/csebuetnlp--mT5_multilingual_XLSum',
    # './Happy/Models/Summary/IlyaGusev--mbart_ru_sum_gazeta',
    # './Happy/Models/Summary/IlyaGusev--rut5_base_sum_gazeta',
    # './Happy/Models/Summary/utrobinmv--t5_summary_en_ru_zh_base_2048',
    ]
else:
    # Online use
    SUMMARY_MODELS = [
    'csebuetnlp/mT5_multilingual_XLSum',
    'IlyaGusev/mbart_ru_sum_gazeta',
    'IlyaGusev/rut5_base_sum_gazeta',
    'utrobinmv/t5_summary_en_ru_zh_base_2048',
    ]



SUMMARIES_TABLE = 'elibrary_dataset'
PROCESSING_HANDLER = lambda k: re.sub(r' {2,}', ' ', re.sub('\n+', '\n', re.sub(r'(?<!\n)\n(?!\n)', ' ', re.sub('-\n', '', k.strip()))))
