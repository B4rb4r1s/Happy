from docx import Document

# Параметры ГОСТ 2.105-2019
GOST_FONT = 'Times New Roman'
GOST_FONT_SIZE = [12, 14]  # Размер шрифта в пунктах
GOST_ALIGNMENT = 'justified'  # Выравнивание по ширине
GOST_SPACING = 1.5  # Межстрочный интервал
GOST_INDENTATION = 1.25  # Отступы в см

# Параметры полей страницы по ГОСТу
GOST_MARGIN_TOP = 2  # см
GOST_MARGIN_BOTTOM = 2  # см
GOST_MARGIN_LEFT = 3.0  # см
GOST_MARGIN_RIGHT = 1.5  # см

def cm_to_twips(cm):
    """Перевод сантиметров в twips (единицы измерения в Word)"""
    return cm * 567  # 1 cm = 567 twips

def check_docx_format(docx_path):
    # Открываем документ
    doc = Document(docx_path)
    
    # Флаги для проверки
    all_ok = True
    errors = []

    for para in doc.paragraphs:
        # Проверка шрифта
        if para.runs and para.runs[0].font.name != GOST_FONT:
            errors.append(f"Неверный шрифт в абзаце: {para.text}")
            all_ok = False

        # Проверка размера шрифта
        if para.runs and para.runs[0].font.size and para.runs[0].font.size.pt not in  GOST_FONT_SIZE:
            errors.append(f"Неверный размер шрифта в абзаце: {para.text}")
            all_ok = False

        # Проверка выравнивания
        if para.alignment is not None and para.alignment != 3:  # 3 - выравнивание по ширине
            errors.append(f"Неверное выравнивание в абзаце: {para.text}")
            all_ok = False

        # Здесь можно добавить другие проверки: отступы, интервалы и т.д.

    # Проверка полей первой секции (предполагаем, что все секции документа одинаковы)
    section = doc.sections[0]
    if section.top_margin != cm_to_twips(GOST_MARGIN_TOP):
        errors.append(f"Неверный отступ сверху: {section.top_margin / 567:.2f} см (должно быть {GOST_MARGIN_TOP} см)")
        all_ok = False

    if section.bottom_margin != cm_to_twips(GOST_MARGIN_BOTTOM):
        errors.append(f"Неверный отступ снизу: {section.bottom_margin / 567:.2f} см (должно быть {GOST_MARGIN_BOTTOM} см)")
        all_ok = False

    if section.left_margin != cm_to_twips(GOST_MARGIN_LEFT):
        errors.append(f"Неверный отступ слева: {section.left_margin / 567:.2f} см (должно быть {GOST_MARGIN_LEFT} см)")
        all_ok = False

    if section.right_margin != cm_to_twips(GOST_MARGIN_RIGHT):
        errors.append(f"Неверный отступ справа: {section.right_margin / 567:.2f} см (должно быть {GOST_MARGIN_RIGHT} см)")
        all_ok = False


    if all_ok:
        return "Документ соответствует ГОСТ 2.105-2019."
    else:
        return "Ошибки:\n" + "\n".join(errors)



if __name__ == "__main__":
    print(check_docx_format("./Data/DOC/doc1.docx"))
