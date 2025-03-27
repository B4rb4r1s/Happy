from SpellModels import Omage_corrector
import config
import os
import re
import time
import pandas as pd
# sys.path.append('/task/Happy/Utility')

import logging
import sys
# sys.path.insert(1, '/app/Happy/Utility')
# from DatabaseHandler import DatabaseHandler



def run_full_correction():
    db_handler = DatabaseHandler('docker')
    db_handler.set_doc_ids(config.SPELL_CORRECTION_TABLE)

    correctors = [SpellModels.Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    for corrector in correctors:
        corrector.run_and_load(db_handler)

    db_handler.close_db_connection()

def run():
    corr = SpellModels.Omage_corrector('./Happy/Models/SpellCheck/ai-forever--FRED-T5-large-spell')
    # corr = SpellModels.Omage_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')

    text = 'Проблнма изучания социокультурных особенностей формирования социального потенциаламолодежи в усл овиях происхлдящих кризисных явленийи трансформаци российского общества является многоаспектной.'
    print(f'original: {text}\ncorrect: {corr.correct_text(text)}')




def i_luv_u():
    original = 'я тбя люблб!'
    print(original)
    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    for corrector in correctors:
        text = corrector.correct_text(original)
        print(f'{corrector.column} >>> {text}')



def folder_txt():
    path = 'Happy/Data/TXT/SpellCorrection'
    # logging.basicConfig(filename='Happy/Utility/Cleaner/logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
    start = time.time()
    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    print(f'all models loaded in {time.time()-start} sec')
    texts = []

    with open('Happy/Utility/Cleaner/logs.txt', 'w') as f:
        f.write('')


    timers_s = []
    for corrector in correctors:
        timers = []

        # logging.info(f'Corrector: {corrector.column}')
        with open('Happy/Utility/Cleaner/logs.txt', 'a') as res:
            res.write(f'Corrector: {corrector.column}\n')
        print(f'Corrector: {corrector.column}')

        for document in os.listdir(path):
            if '.' in document:
                with open('Happy/Utility/Cleaner/logs.txt', 'a') as res:
                    res.write(f'\tDocument {document}\n')
                with open(f'{path}/{document}', 'r', encoding='windows-1251') as f:
                    original_text = f.read()
                
                start = time.time()
                corr_text = corrector.correct_text(original_text)
                stop = time.time()-start

                with open('Happy/Utility/Cleaner/logs.txt', 'a') as res:
                    res.write(f'\tDoc: {document} \tText: {len(original_text)} charecters proccesed in {stop} sec\n')
                print(f'Text: {len(original_text)} charecters proccesed in {stop} sec')

                with open(f'{path}/correct/corr_{corrector.column}_{document}', 'w', encoding='windows-1251') as f:
                    f.write(corr_text)
                


if __name__ == '__main__':
    folder_txt()
    # corrector = T5_russ_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')
    # print('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.\n')
    # text = corrector.correct_text('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.')
    # print(text)
    
    # corr = Omage_corrector('./Happy/Models/SpellCheck/ai-forever--FRED-T5-large-spell')


    # run()
    # run_full_correction()
    


