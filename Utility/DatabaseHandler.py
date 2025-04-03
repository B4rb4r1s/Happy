import tqdm
import psycopg2


class DatabaseHandler:
    def __init__(self, host):
        self.host = host
        self.connection = None
        self.get_db_connection()

    def get_db_connection(self):
        port = "5432"
        if self.host == 'local':
            host = "localhost"
        elif self.host == 'ssh_27':
            host = "192.168.1.55"
        elif self.host == 'ssh_dgx':
            host = "195.19.43.12"
            port = "5533"
        elif self.host == 'docker':
            host = "postgre"
        else:
            print(f'[ ERROR ] Unknown type for host')
            return False
        try:
            print(f'[ DEBUG ] Trying to connect to {host}:{port}')
            self.connection = psycopg2.connect(database='happy_db', 
                                               user="happy_user", 
                                               password="happy", 
                                               host=host, 
                                               port=port)
            print(f'[ DEBUG ] Connected to {host}:{port}')
        except Exception as err:
            print(f'[ ERROR ] Database is unreachable\n>>> {err}')
            return False
        return True
    
    def close_db_connection(self):
        self.connection.close()


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

    def upload_data(self, table, column, doc_id, text):
        with self.connection.cursor() as cursor:
            cursor.execute(f'''
                UPDATE {table}
                SET {column} = %s
                WHERE {table}.doc_id = {doc_id};
            ''', (text, ))
            self.connection.commit()
        return True

    def set_doc_ids(self, table_for_ids):
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
    


if __name__ == '__main__':
    db = DatabaseHandler('docker')
    db.get_db_connection()
    table = db.get_db_table('elibrary_dataset_summaries', 'lingvo_summary')
    print(table[:2])
    table = db.get_db_table('elibrary_dataset_spell', 'sage_m2m100')
    print(table[:2])
    db.close_db_connection()