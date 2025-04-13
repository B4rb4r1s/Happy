from SpellModels import Omage_corrector
import config
import os
import sys
import time
import datetime
# sys.path.append('/task/Happy/Utility')

sys.path.append('/task/DocumentAnalysisSystem/Utility')
# print(sys.path)
from DatabaseHandler import DatabaseHandler



def run_full_correction():
    db_handler = DatabaseHandler('docker')
    db_handler.set_doc_ids(config.SPELL_CORRECTION_TABLE)

    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    # corrector = Omage_corrector(config.SPELL_CORRECTION_MODELS[1])

    for corrector in correctors:
        corrector.run_and_load(db_handler, 'elibrary_dataset_spell.doc_id <= 5140 and elibrary_dataset_spell.doc_id > 5120')
    # corrector.run_and_load(db_handler)

    db_handler.close_db_connection()

def run():
    corr = Omage_corrector(config.SPELL_CORRECTION_MODELS[1]) # ai-forever--sage-m2m100-1.2B
    # corr = SpellModels.Omage_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')

    text = 'Проблнма изучания социокультурных особенностей формирования социального потенциаламолодежи в усл овиях происхлдящих кризисных явленийи трансформаци российского общества является многоаспектной.'
    print(f'original: {text}\ncorrect: {corr.correct_text(text)}')



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

                with open('Happy/Utility/Corrector/logs.txt', 'a') as res:
                    res.write(f'\t\tDoc: {document} \tText: {len(original_text)} charecters proccesed in {stop} sec\n')
                print(f'Text: {len(original_text)} charecters proccesed in {stop} sec')

                with open(f'{path}/correct/corr_{corrector.column}_{document}', 'w', encoding='windows-1251') as f:
                    f.write(corr_text)



def check_tokens(text):
    corr = Omage_corrector(config.SPELL_CORRECTION_MODELS[1])
    print(corr.correct_text(text))


def i_luv_u():
    original = 'я тбя люблб!'
    print(original)
    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]
    for corrector in correctors:
        text = corrector.correct_text(original)
        print(f'{corrector.column} >>> {text}')



if __name__ == '__main__':
    # LT_with_NN()
    # folder_txt()
    # corrector = T5_russ_corrector('./Happy/Models/SpellCheck/UrukHan--t5-russian-spell')
    # print('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.\n')
    # text = corrector.correct_text('В статье анализируется эмпирический материал, полученный входе социологических исследований феномена бедности. Рассмотренодва основных вопроса: оценка доли бедных в населении современнойРоссии и изучение отношений самих россиян к различным аспектамбедности. Выделены основные признаки «бедности по-российски»в массовом сознании россиян, показаны массовые представленияпричин бедности, даны структура и характерные особенностироссийской бедности.')
    # print(text)
    
    # corr = Omage_corrector('./Happy/Models/SpellCheck/ai-forever--FRED-T5-large-spell')


    # run()
    run_full_correction()
    run_full_correction()
    run_full_correction()
    run_full_correction()
    run_full_correction()
    run_full_correction()
    run_full_correction()
    run_full_correction()
    # text = '''Опрос студентов 4-х курсов (анкетирование, сплошной опрос, 289 чел.) показал, что около 20% опрошенных изъявляют желание продолжить обучение после окончания техникума (15% респондентов будут поступать в ДВГУПС на обучение по программам высшего профессионального образования по специальности и 5% отдают предпочтение другим вузам), а более 18% не имеют такого желания; 17% серьезно относятся к изучению только специальных дисциплин, которые пригодятся им для дальнейшего обучения в вузе; и столько же студентов 17% игнорируют все дисциплины. Большое количество опрошенных вообще воздержалось от ответа на вопрос об отношении к учебе в вузе. Однако 60% респондентов отметили, что хотели бы продолжить обучение по программам ВПО ДВГУПС, если бы существовали сокращенные программы обучения, позволяющие выпускникам СПО поступать на ВПО на специальных условиях. [3]Одной из причин, мешающих поступать на общих основаниях, студенты назвали то, что не хотят сдавать ЕГЭ, поскольку боятся, что за несколько лет обучения в техникуме забыли школьную программу и низко оценивают свои шансы на успешную сдачу ЕГЭ. Однако, у выпускников СПО есть преимущества перед выпускниками школ и они должны быть учтены при приеме их на ВПО: выпускник СПО, желающий продолжить образование, уже не только имеет представление о будущей профессии, но и прошел практику, он имеет специальные знания и навыки, которыми не обладают выпускники школ. А подготовка к ЕГЭ происходит как раз во время написания дипломной работы, поэтому студент не сможет полноценно подготовиться к ЕГЭ и одновременно успешно написать диплом. Поэтому необходимо пересмотреть условия поступления выпускников техникума на обучение по программам ВПО в ДВГУПС. Для успешной профессиональной социализации студентов СПО необходимо применение программы не только адаптации студентов нового набора к учебному'''
    # check_tokens(text)
    


