from DocumentLoader import DocumentLoader


if __name__ == '__main__':
    loader = DocumentLoader(source_directory='Datasets/GRNTI/elibrary/elibrary_full', 
                            db_table='elibrary_dataset')
    loader.elibrary_load()