import SpellModels
import sys
sys.path.insert(1, '/app/Happy/Utility')
from DatabaseHandler import DatabaseHandler

import config


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



if __name__ == '__main__':
    # run()
    run_full_correction()