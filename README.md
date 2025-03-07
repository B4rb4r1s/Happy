Модели для генерации краткого соденжиния хранятся в корне проекта, в папке `Models`.

Сейчас использвется [MBART](https://huggingface.co/IlyaGusev/mbart_ru_sum_gazeta). (`Models/MBART/`)

## Структура проекта:
```
Happy/
├── app.py              # Точка входа в приложение
├── Models/
│   ├── Summary/        # Локальние модели для генерации краткого содержания
│   └── SpellCheck/     # Локальные модели для исправления ошибок в тексте
├── Source/             
│   ├── Handler.py      
│   ├── run.py          
│   ├── FileOverwiev.py 
│   ├── ExtractMeta.py  
│   ├── DocReader.py    
│   ├── OCR.py          
│   ├── Summarizer.py   
│   └── NERer.py        
```
├── config.py        # Конфигурационные данные
├── models/          # Модели данных
│   ├── __init__.py
│   ├── user.py
│   └── product.py
├── services/        # Бизнес-логика
│   ├── __init__.py
│   ├── auth.py
│   └── payment.py
└── utils/           # Вспомогательные утилиты
    ├── __init__.py
    └── helpers.py