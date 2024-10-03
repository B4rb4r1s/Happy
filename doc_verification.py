import os
import sys

# Здесь будет проверка файлов на их форматы
#  нужно будет сделать преобразование форматов к одним
#  PDF, DOCX, PNG
def verification(filename):
    infilename, extansion = os.path.splitext(filename)
    
    if extansion != '':
        extansion = extansion.lower()
        print(f'Файл с расширением \'{extansion}\'')

    return extansion