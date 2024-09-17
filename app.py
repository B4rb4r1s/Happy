from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

from run import Chain

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Секретный ключ для защиты сессий и сообщений
app.secret_key = 'your_secret_key'

# Папка для загрузки файлов
UPLOAD_FOLDER = 'Uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Главная страница с формой для загрузки файлов
@app.route('/')
def index():
    return render_template('index.html')

# Обработка загрузки файла
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Нет файла для загрузки')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Не выбран файл для загрузки')
        return redirect(request.url)
    
    if file:
        # Сохраняем файл в папку uploads
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Здесь можно вызвать функцию для обработки файла
        # Например: process_document(file_path)
        chain = Chain()
        req = {'task': 'extract_meta',
                'path': file_path}
        chain.handle_request(req)

        # Сохраняем результаты в сессии
        session['metadata'] = req['meta']
        session['extracted_text'] = req['text']
        session['summary'] = req['summary']
        session['entities'] = req['entities']
        
        flash(f'Файл {file.filename} успешно загружен и обработан')
        return redirect(url_for('index'))

# Страница для просмотра результатов обработки (например, список сущностей)
@app.route('/results')
def results():
    # Здесь должны быть данные, полученные после обработки документа
    # Например, из базы данных или глобальной переменной
    
    # extracted_text = req['text']
    # summary = req['summary']
    # entities = [
    #     ("Barack Obama", "PERSON"),
    #     ("United States", "GPE"),
    #     ("Washington", "GPE")
    # ]
    
    # Передаем данные в шаблон для отображения
    return render_template('results.html', 
                           extracted_text = session.get('extracted_text', 'Нет данных'), 
                           summary = session.get('summary', 'Нет данных'), 
                           entities = session.get('entities', []),
                           metadata = session.get('metadata', 'Нет данных'))

if __name__ == '__main__':
    # Запускаем приложение Flask
    app.run(debug=True, host="0.0.0.0", port=5000)
