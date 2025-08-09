from DocumentLoader import DocumentLoader
import os


def run():
    loader = DocumentLoader()
    loader.set_dbtable(table='elibrary_dataset')

    # dataset_path  = 'Datasets/GRNTI/DiplomaParser/tech'
    dataset_path  = 'Datasets/Summarization/summarization-dataset-main/dataset'

    for dir_tag in os.listdir(dataset_path):
        # for target_dir in os.listdir(f'{dataset_path}/{dir_tag}'):
        loader.set_directory(directory=f'{dataset_path}/{dir_tag}')
        loader.multidirs_load_txt()
        # loader.elibrary_load()
    # for dir_tag in os.listdir(dataset_path):
    #     # for target_dir in os.listdir(f'{dataset_path}/{dir_tag}'):
    #     loader.set_directory(directory=f'{dataset_path}/{dir_tag}')
    #     loader.elibrary_load()


if __name__ == '__main__':
    # loader = DocumentLoader(source_directory='Datasets/GRNTI/elibrary/elibrary044100', 
    #                         db_table='elibrary_dataset')
    # loader = DocumentLoader(source_directory='Datasets/GRNTI/elibrary/elibrary490000', 
    #                         db_table='elibrary_dataset')

    run()