from SpellModels import Omage_corrector
from LT_corrector import LT_corrector
import config
import os
import re
import time
import pandas as pd
# sys.path.append('/task/Happy/Utility')

import logging
import sys
sys.path.append('/task/Happy/Utility')
# print(sys.path)
from DatabaseHandler import DatabaseHandler



def run_full_correction():
    db_handler = DatabaseHandler('docker')
    db_handler.set_doc_ids(config.SPELL_CORRECTION_TABLE)

    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    for corrector in correctors:
        corrector.run_and_load(db_handler)

    db_handler.close_db_connection()

def run():
    corr = Omage_corrector(config.SPELL_CORRECTION_MODELS[1]) # ai-forever--sage-m2m100-1.2B
    # corr = SpellModels.Omage_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')

    text = 'Проблнма изучания социокультурных особенностей формирования социального потенциаламолодежи в усл овиях происхлдящих кризисных явленийи трансформаци российского общества является многоаспектной.'
    print(f'original: {text}\ncorrect: {corr.correct_text(text)}')


# python ./Happy/Utility/Corrector/run_corrector.py
def LT_with_NN():
    db_handler = DatabaseHandler('docker')
    # db_handler.set_doc_ids(config.SPELL_CORRECTION_TABLE)

    langtool = LT_corrector()

    doc_text = config.PROCESSING_HANDLER(db_handler.get_db_table('elibrary_dataset_spell', 'langtool')[10][1])
    # print(doc_text)

    with open('Happy/Utility/Cleaner/logs.txt', 'a') as f:
        f.write('task: LT_with_NN')

    matches = langtool.run_LT(doc_text)
    print(matches)

    return 0



def folder_txt():
    path = 'Happy/Data/TXT/SpellCorrection'
    # logging.basicConfig(filename='Happy/Utility/Cleaner/logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
    start = time.time()
    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    print(f'all models loaded in {time.time()-start} sec')
    texts = []

    with open('Happy/Utility/Cleaner/logs.txt', 'a') as f:
        f.write('task: folder_txt')

    for corrector in correctors:

        # logging.info(f'Corrector: {corrector.column}')
        with open('Happy/Utility/Cleaner/logs.txt', 'a') as res:
            res.write(f'\tCorrector: {corrector.column}\n')
        print(f'Corrector: {corrector.column}')

        for document in os.listdir(path):
            if '.' in document:
                with open('Happy/Utility/Cleaner/logs.txt', 'a') as res:
                    res.write(f'\t\tDocument {document}\n')
                with open(f'{path}/{document}', 'r', encoding='windows-1251') as f:
                    original_text = f.read()
                
                start = time.time()
                corr_text = corrector.correct_text(original_text)
                stop = time.time()-start

                with open('Happy/Utility/Cleaner/logs.txt', 'a') as res:
                    res.write(f'\t\tDoc: {document} \tText: {len(original_text)} charecters proccesed in {stop} sec\n')
                print(f'Text: {len(original_text)} charecters proccesed in {stop} sec')

                with open(f'{path}/correct/corr_{corrector.column}_{document}', 'w', encoding='windows-1251') as f:
                    f.write(corr_text)


def i_luv_u():
    original = 'я тбя люблб!'
    print(original)
    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    for corrector in correctors:
        text = corrector.correct_text(original)
        print(f'{corrector.column} >>> {text}')




if __name__ == '__main__':
    LT_with_NN()
    # folder_txt()
    # corrector = T5_russ_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')
    # print('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.\n')
    # text = corrector.correct_text('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.')
    # print(text)
    
    # corr = Omage_corrector('./Happy/Models/SpellCheck/ai-forever--FRED-T5-large-spell')


    # run()
    # run_full_correction()
    


