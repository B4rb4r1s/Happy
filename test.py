import pytest
import io

from app import app


test_docs = [
    'Data\PDF\text\text2.pdf',
    'Data\PDF\scan\scan2.pdf',
    'Data\DOCX\doc_title.docx'
]

@pytest.fixture
def client():
    # Настройка тестового клиента Flask
    with app.test_client() as client:
        yield client

def test_file_upload(client):
    # Создаем объект файла для загрузки
    data = {
        'file': (io.BytesIO(b'my file contents'), 'test_file.txt')
    }

    # Выполняем POST запрос для загрузки файла
    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Проверяем результат
    assert response.status_code == 200
    assert response.json == {'success': 'File uploaded successfully'}

def test_no_file_upload(client):
    # Пытаемся загрузить без файла
    response = client.post('/upload', data={}, content_type='multipart/form-data')

    # Проверяем результат
    assert response.status_code == 400
    assert response.json == {'error': 'No file part'}
