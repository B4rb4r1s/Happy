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





def LT_with_NN():
    db_handler = DatabaseHandler('docker')
    # db_handler.set_doc_ids(config.SPELL_CORRECTION_TABLE)

    langtool = LT_corrector()
    corrector = Omage_corrector(config.SPELL_CORRECTION_MODELS[1])
    # correctors = [Omage_corrector(model_path) for model_path in config.SPELL_CORRECTION_MODELS]

    with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as f:
        f.write('task: LT_with_NN\n')
        f.write(f'\tCorrector: {corrector.column}\n')

    docs_texts = db_handler.get_db_table('elibrary_dataset_spell', 'langtool')
    for doc_id, doc_text in docs_texts[:25]:

        with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as f:
            f.write(f'\t\tDocument: {doc_id}\n')

        doc_para = config.WHITESPACE_HANDLER(doc_text).split('\n')
        doc_para_sent = [para.split('.') for para in doc_para]

        start = time.time()
        corrected_text = []
        for i, para in enumerate(doc_para_sent):
            corrected_paragraph = []
            for j, sent in enumerate(para):
                start = time.time()
                
                matches = langtool.run_LT(sent)
                if matches:
                    # print(f'In {i+1}/{len(doc_para_sent)} paragraph\nIn {j+1}/{len(para)} sentance\n{len(matches)} possible misstakes found')
                    # for match in matches:
                    #     print(f'\t{match};')
                    corrected_sentance = corrector.correct_paragraph(sent)
                    corrected_paragraph.append(corrected_sentance)
                else:
                    corrected_paragraph.append(sent)

                stop = time.time() - start

                with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as res:
                    res.write(f'\t\t\t{i}/{len(doc_para_sent)} Paragraph, {j}/{len(para)} Sentence:\n\t\t\t\t{len(sent)} charecters proccesed in {stop} sec\n')

            corrected_paragraph = '.'.join(corrected_paragraph)

        corrected_text = '\n'.join(corrected_paragraph)
        stop = time.time() - start

        print(corrected_text)

        # db_handler.upload_data('elibrary_dataset_spell', 'langtool', doc_id, corrected_text)


        with open('DocumentAnalysisSystem/Utility/Corrector/logs.txt', 'a') as res:
            res.write(f'\t\tText: {len(doc_text)} charecters, {len(doc_para)} paragraphs\n\t\t\tproccesed in {stop} sec\n')


    return True




def simple_exmpl():
    langtool = LT_corrector()
    text = '''`В молодежной среде регулярно проводятся соревнования по силовому многоборью, волейболу, футболу и другим видов спорта.'''
    print(langtool.run_LT(text))

if __name__ == '__main__':
    LT_with_NN()
    # simple_exmpl()
