import language_tool_python
import tqdm
import config

import sys
import time
from SpellModels import Omage_corrector
sys.path.append('/task/DocumentAnalysisSystem/Utility')
# print(sys.path)
from DatabaseHandler import DatabaseHandler


class LT_corrector:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('auto')
        self.is_good_rule = lambda rule: \
            rule.ruleId != 'MORFOLOGIK_RULE_RU_RU' and \
            rule.ruleId != 'UPPERCASE_SENTENCE_START' and \
            rule.ruleId != 'Cap_Letters_Name' and \
            len(rule.replacements) and \
            rule.replacements[0][0].isupper()
        # self.good_rules = [
            # rule.ruleId != 'MORFOLOGIK_RULE_RU_RU' and \
            # rule.ruleId != 'UPPERCASE_SENTENCE_START' and \
            # rule.ruleId != 'Cap_Letters_Name' and \
        # ]


    def run_LT_dataset(self, dataset):
        array_matches = []
        for text in tqdm.tqdm(dataset):
            try:
                array_matches.append(self.run_LT(text))
            except Exception as err:
                print(f'[ ERROR ] >>> {err}')
                continue
        return array_matches


    # /root/.cache/language_tool_python
    def run_LT(self, text):
        matches = self.tool.check(config.PROCESSING_HANDLER(text))
        # matches = [rule for rule in matches if self.is_good_rule(rule)]
        # for i, match in enumerate(matches):
        #     yield i, match
        #     print(i, match)
        #     array_matches.append(match)
        return matches



def logger(message, level=0):
    logger_path = 'DocumentAnalysisSystem/Utility/Corrector/logs.txt'
    padding = '\t'*level
    with open(logger_path, 'a') as f:
        f.write(f'{padding}{message}\n')



def LT_with_NN():
    db_handler = DatabaseHandler('docker')
    # db_handler.set_doc_ids(config.SPELL_CORRECTION_TABLE)

    langtool = LT_corrector()
    # corrector = Omage_corrector(config.SPELL_CORRECTION_MODELS[1])
    correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]

    
    logger(f'task: LT_with_NN', 0)
    logger(f'Corrector: {corrector.column}', 1)

    docs_texts = db_handler.get_db_table('elibrary_dataset_spell', 'langtool')
    for doc_id, doc_text in docs_texts[:25]:

        with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as f:
            f.write(f'\t\tDocument: {doc_id}\n')

        doc_para = config.WHITESPACE_HANDLER(doc_text).split('\n')
        doc_para_sent = [para.split('.') for para in doc_para]

        startd = time.time()
        corrected_text = []
        for i, para in enumerate(doc_para):
            corrected_paragraph = []
            start = time.time()

            matches = langtool.run_LT(para)
            if len(matches)>0:
                corrected_sentance = corrector.correct_paragraph(para)
                corrected_paragraph.append(corrected_sentance)
            else:
                corrected_paragraph.append(para)

            stop = time.time() - start

            with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as res:
                res.write(f'\t\t\t{i+1}/{len(doc_para_sent)} Paragraph for {len(para)} charecters proccesed in {stop} sec\n')
            corrected_text.append(corrected_paragraph)

        corrected_text = '\n\t'.join(corrected_text)
        stopd = time.time() - startd

        print(corrected_text)

        # db_handler.upload_data('elibrary_dataset_spell', 'langtool', doc_id, corrected_text)


        with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as res:
            res.write(f'\t\tText: {len(doc_text)} charecters, {len(doc_para)} paragraphs\n\t\t\tproccesed in {stopd} sec\n')


    return True




def simple_exmpl():
    langtool = LT_corrector()
    text = '''В статье представлены результаты исследования профессиональной идентичности молодого преподавателя в условиях трансформации академической среды. Доказано, что современное поколение молодых преподавателей существует в конфликтном социально-культурном и профессиональном пространстве. Одна плоскость анализа трансформация академической среды как меса работы, конфликт двух тпов университетских культур: традиционной, «профессорской», ориентированной на гуманитарные ценности, и корпоративной с базовыми экономическими ценностями. Другая плоскость анализа размытость социальной идентификации современной молодежи, в том числе и «молодых взрослых», современного поколения молодых'''
    # text = '''`В молодежной среде регулярно проводятся соревнования по силовому многоборью, волейболу, футболу и другим видов спорта.'''
    mhs = langtool.run_LT(text)
    print(len(mhs),'\n', mhs)

if __name__ == '__main__':
    LT_with_NN()
    # simple_exmpl()
