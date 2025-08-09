# from DB_Handler import DatabaseHandler
from OmegaSummarizer import Omega_summarizer

import config
import os


def text_extraction():
    '''
    /app/Data/summarization-dataset-main/dataset/**/**/text.txt
    /app/Data/summarization-dataset-main/dataset/**/**/abstract.txt
    ssh://happy_server/home/user/Documents/Projects/Happy/Data/summarization-dataset-main/dataset/medicine/med_1/abstract.txt
    '''
    texts_list = []
    abstracts_list = []
    dir_base = '/app/Data/summarization-dataset-main/dataset'
    for dir_parent in os.listdir(dir_base):
        # print(f'Parent directory - {dir_parent}')
        for dir_child in os.listdir(os.path.join(dir_base, dir_parent)):
            # print(f'\tChild directory - {dir_child}')
            text_file_path = dir_base+'/'+dir_parent+'/'+dir_child+'/text.txt'
            abst_file_path = dir_base+'/'+dir_parent+'/'+dir_child+'/abstract.txt'

            with open(text_file_path, 'r') as text_file:
                texts_list.append(text_file.read())
            with open(abst_file_path, 'r') as abst_file:
                abstracts_list.append(abst_file.read())
            # print(texts_list, abstracts_list)
            # print(len(texts_list), len(abstracts_list))

    return texts_list, abstracts_list


def run():
    texts_list, abstracts_list = text_extraction()
    print(f'extraction complete: {len(texts_list), len(abstracts_list)}')

    summarizers = [Omega_summarizer(model_path, device=config.DEVICE) for model_path in config.SUMMARY_MODELS]
    print(f'summarizators initialization complete')
    
    summary_list = []
    for s, summarizer in enumerate(summarizers):
        for i, text in enumerate(texts_list):
            # summary_list.append(summarizer.summarize_text(text))
            with open(f'/app/datasets/sum/summary-complete-sum-{s+2}-{i}.txt', 'w') as summ_file:
                summ_file.write(summarizer.summarize_text(text))

    return 0

if __name__ == '__main__':
    run()