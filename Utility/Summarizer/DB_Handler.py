import psycopg2
import tqdm


class DatabaseHandler:
    def __init__(self, host):
        self.host = host
        self.connection = None
        self.get_db_connection()

    def get_db_connection(self):
        if self.host == 'local':
            host = "localhost" 
        elif self.host == 'ssh':
            host = "192.168.1.55"
        elif self.host == 'docker':
            host = "postgre"
        else:
            print(f'[ ERROR ] Unknown type for host')
            return False
        try:
            self.connection = psycopg2.connect(database='happy_db', 
                                               user="happy_user", 
                                               password="happy", 
                                               host=host, 
                                               port="5432")
        except Exception as err:
            print(f'[ ERROR ] Database is unreachable\n>>> {err}')
            return False
        return True
    
    def close_db_connection(self):
        self.connection.close()

    def get_lingvo_table(self, table='elibrary_dataset_summaries'):
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT elibrary_dataset.id, text_dedoc
                FROM elibrary_dataset
                LEFT JOIN {table}
                    ON {table}.doc_id = elibrary_dataset.id
                WHERE {table}.lingvo_summary IS NULL
                ORDER BY elibrary_dataset.id ASC;
            ''')
            dataset = cursor.fetchall()
        return dataset

    def get_db_table(self, table, column, extra_condition=None):
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT elibrary_dataset.id, text_dedoc
                FROM elibrary_dataset
                LEFT JOIN {table}
                    ON {table}.doc_id = elibrary_dataset.id
                WHERE {table}.{column} IS NULL
                    {f"AND {extra_condition}" if extra_condition else ""}
                ORDER BY elibrary_dataset.id ASC;
            ''')
            dataset = cursor.fetchall()
        return dataset

    def upload_summary(self, column, doc_id, text):
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE elibrary_dataset_summaries
                SET {column} = %s
                WHERE elibrary_dataset_summaries.doc_id = {doc_id};
            ''', (text, ))
            self.connection.commit()
        return True

    def set_doc_ids(self, table_for_ids='elibrary_dataset_summaries'):
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT elibrary_dataset.id
                FROM elibrary_dataset
                LEFT JOIN {table_for_ids}
                    ON {table_for_ids}.doc_id = elibrary_dataset.id
                WHERE {table_for_ids}.doc_id IS NULL
                ORDER BY elibrary_dataset.id ASC;
            ''')
            dataset = cursor.fetchall()
            
            for doc_id in tqdm.tqdm(dataset):
                cursor.execute(f'''
                    INSERT INTO {table_for_ids} (doc_id)
                    VALUES ({doc_id[0]})
                ''')
                self.connection.commit()
        return 0