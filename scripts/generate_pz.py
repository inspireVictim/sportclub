# -*- coding: utf-8 -*-
"""Генератор пояснительной записки ВКР по ГОСТ КР (2.105-95).

Тема: «Разработка базы данных для спортивного клуба».

Запуск:
    python scripts/generate_pz.py

Результат сохраняется в файл ПЗ_База_Данных_Спортклуба.docx в корне проекта.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Mm, Pt, RGBColor


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "ПЗ_База_Данных_Спортклуба.docx"

FONT_NAME = "Times New Roman"
FONT_SIZE = 14


# ----------------------------------------------------------------------------
# Утилиты форматирования
# ----------------------------------------------------------------------------

def _set_run_font(run, *, bold: bool = False, italic: bool = False,
                  size: int = FONT_SIZE, color=None) -> None:
    run.font.name = FONT_NAME
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), FONT_NAME)
    rFonts.set(qn("w:hAnsi"), FONT_NAME)
    rFonts.set(qn("w:cs"), FONT_NAME)
    rFonts.set(qn("w:eastAsia"), FONT_NAME)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def _apply_paragraph_format(p, *, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                            first_line_indent: bool = True,
                            space_before: float = 0, space_after: float = 0,
                            line_spacing: float = 1.5) -> None:
    pf = p.paragraph_format
    pf.alignment = alignment
    pf.first_line_indent = Cm(1.25) if first_line_indent else Cm(0)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)


def add_paragraph(doc, text: str, *, bold: bool = False, italic: bool = False,
                  alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                  first_line_indent: bool = True,
                  space_before: float = 0, space_after: float = 0,
                  size: int = FONT_SIZE) -> None:
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=alignment,
        first_line_indent=first_line_indent,
        space_before=space_before,
        space_after=space_after,
    )
    run = p.add_run(text)
    _set_run_font(run, bold=bold, italic=italic, size=size)


def add_centered(doc, text: str, *, bold: bool = False, size: int = FONT_SIZE,
                 space_before: float = 0, space_after: float = 6) -> None:
    add_paragraph(doc, text, bold=bold,
                  alignment=WD_ALIGN_PARAGRAPH.CENTER,
                  first_line_indent=False,
                  space_before=space_before, space_after=space_after,
                  size=size)


def add_chapter_heading(doc, number: int, title: str) -> None:
    doc.add_page_break()
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        first_line_indent=False,
        space_before=0, space_after=18,
    )
    run = p.add_run(f"{number}. {title.upper()}")
    _set_run_font(run, bold=True)


def add_section_heading(doc, number: str, title: str) -> None:
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
        first_line_indent=False,
        space_before=12, space_after=8,
    )
    run = p.add_run(f"{number} {title}")
    _set_run_font(run, bold=True)


def add_list_item(doc, text: str, *, marker: str = "—") -> None:
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
        first_line_indent=False,
        space_before=0, space_after=0,
    )
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    run = p.add_run(f"{marker} {text}")
    _set_run_font(run)


def add_screenshot_marker(doc, caption: str) -> None:
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        first_line_indent=False,
        space_before=8, space_after=8,
    )
    run = p.add_run(f"{{Скриншот: {caption}}}")
    _set_run_font(run, italic=True, color=RGBColor(0x33, 0x33, 0x33))


def add_figure_caption(doc, text: str) -> None:
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        first_line_indent=False,
        space_before=0, space_after=12,
    )
    run = p.add_run(text)
    _set_run_font(run)


def add_code_block(doc, code: str) -> None:
    p = doc.add_paragraph()
    _apply_paragraph_format(
        p,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
        first_line_indent=False,
        space_before=4, space_after=8,
        line_spacing=1.15,
    )
    run = p.add_run(code)
    run.font.name = "Courier New"
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Courier New")
    rFonts.set(qn("w:hAnsi"), "Courier New")
    rFonts.set(qn("w:cs"), "Courier New")
    run.font.size = Pt(11)


def add_table(doc, headers: list[str], rows: list[list[str]], *,
              col_widths_cm: list[float] | None = None) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell.text = ""
        p = cell.paragraphs[0]
        _apply_paragraph_format(p, alignment=WD_ALIGN_PARAGRAPH.CENTER,
                                first_line_indent=False, line_spacing=1.15)
        run = p.add_run(header)
        _set_run_font(run, bold=True)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            cell = table.rows[r].cells[c]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.text = ""
            p = cell.paragraphs[0]
            _apply_paragraph_format(p, alignment=WD_ALIGN_PARAGRAPH.LEFT,
                                    first_line_indent=False, line_spacing=1.15)
            run = p.add_run(str(value))
            _set_run_font(run)
    if col_widths_cm:
        for r in table.rows:
            for i, w in enumerate(col_widths_cm):
                r.cells[i].width = Cm(w)
    # отступ после таблицы
    spacer = doc.add_paragraph()
    _apply_paragraph_format(spacer, first_line_indent=False, space_after=6)


# ----------------------------------------------------------------------------
# Стандартные стили документа и поля по ГОСТ КР
# ----------------------------------------------------------------------------

def _setup_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin    = Mm(20)
    section.bottom_margin = Mm(20)
    section.left_margin   = Mm(30)
    section.right_margin  = Mm(10)

    style = doc.styles["Normal"]
    style.font.name = FONT_NAME
    style.font.size = Pt(FONT_SIZE)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    style.paragraph_format.line_spacing = 1.5


# ----------------------------------------------------------------------------
# Разделы документа
# ----------------------------------------------------------------------------

def _build_title_page(doc: Document) -> None:
    for line in [
        "МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ КЫРГЫЗСКОЙ РЕСПУБЛИКИ",
        "",
        "{ПОЛНОЕ НАИМЕНОВАНИЕ УЧЕБНОГО ЗАВЕДЕНИЯ}",
        "",
        "Факультет информационных технологий",
        "Кафедра программной инженерии",
    ]:
        add_centered(doc, line, bold=False)

    for _ in range(4):
        add_centered(doc, "")

    add_centered(doc, "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА", bold=True, size=16)
    add_centered(doc, "к выпускной квалификационной работе", size=14)
    add_centered(doc, "на тему:", size=14)
    add_centered(doc,
                 "«Разработка базы данных для спортивного клуба»",
                 bold=True, size=14)

    for _ in range(6):
        add_centered(doc, "")

    for line in [
        "Выполнил студент: ________________________________________",
        "Группа: _________________________________________________",
        "Научный руководитель: ____________________________________",
        "Заведующий кафедрой: ____________________________________",
    ]:
        add_paragraph(doc, line, first_line_indent=False, space_after=8)

    for _ in range(4):
        add_centered(doc, "")

    add_centered(doc, "Бишкек — 2026")


def _build_contents(doc: Document) -> None:
    doc.add_page_break()
    add_centered(doc, "СОДЕРЖАНИЕ", bold=True, space_after=14)

    rows = [
        ("ВВЕДЕНИЕ", "3"),
        ("1. ПРОЕКТИРОВАНИЕ БАЗЫ ДАННЫХ", "6"),
        ("    1.1. Характеристика предметной области", "6"),
        ("    1.2. Цели и задачи работы", "8"),
        ("    1.3. Приведение к 1НФ", "10"),
        ("    1.4. Приведение к 2НФ", "12"),
        ("    1.5. Приведение к 3НФ", "14"),
        ("    1.6. Логическая модель базы данных", "17"),
        ("    1.7. Реализация в SQLite (DDL-скрипт)", "20"),
        ("    1.8. Выводы по разделу", "27"),
        ("2. ПРОГРАММНАЯ РЕАЛИЗАЦИЯ СЕРВЕРНОЙ ЧАСТИ", "28"),
        ("    2.1. Обоснование выбора стека", "28"),
        ("    2.2. Архитектура приложения", "30"),
        ("    2.3. Подсистема аутентификации", "33"),
        ("    2.4. Алгоритм фиксации посещения", "36"),
        ("    2.5. REST-эндпоинты управления данными", "41"),
        ("    2.6. Выводы по разделу", "44"),
        ("3. ПРОГРАММНАЯ РЕАЛИЗАЦИЯ КЛИЕНТСКОЙ ЧАСТИ", "45"),
        ("    3.1. Концепция «Indigo Night»", "45"),
        ("    3.2. Структура клиентского приложения", "47"),
        ("    3.3. Расписание на CSS Grid", "50"),
        ("    3.4. Адаптивная вёрстка", "53"),
        ("    3.5. Выводы по разделу", "55"),
        ("4. ТЕСТИРОВАНИЕ", "56"),
        ("    4.1. Тестирование триггеров СУБД", "56"),
        ("    4.2. Тестирование REST-API", "58"),
        ("    4.3. Тестирование пользовательского интерфейса", "60"),
        ("    4.4. Выводы по разделу", "62"),
        ("ЗАКЛЮЧЕНИЕ", "63"),
        ("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "66"),
    ]

    table = doc.add_table(rows=len(rows), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, (title, page) in enumerate(rows):
        c1 = table.rows[r].cells[0]
        c2 = table.rows[r].cells[1]
        c1.text = ""
        c2.text = ""
        p1 = c1.paragraphs[0]; p2 = c2.paragraphs[0]
        _apply_paragraph_format(p1, alignment=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent=False, line_spacing=1.2)
        _apply_paragraph_format(p2, alignment=WD_ALIGN_PARAGRAPH.RIGHT, first_line_indent=False, line_spacing=1.2)
        r1 = p1.add_run(title); r2 = p2.add_run(page)
        _set_run_font(r1, bold=title and not title.startswith(" "))
        _set_run_font(r2)
        c1.width = Cm(13.5); c2.width = Cm(2.5)


# ----------------------------------------------------------------------------
# Введение
# ----------------------------------------------------------------------------

def _build_introduction(doc: Document) -> None:
    doc.add_page_break()
    add_centered(doc, "ВВЕДЕНИЕ", bold=True, space_after=14)

    add_paragraph(
        doc,
        "Коммерческие спортивные клубы относятся к организациям сервисного типа, "
        "для которых эффективность операционной деятельности напрямую зависит от "
        "качества учёта клиентской базы, абонементного обслуживания и исполнения "
        "расписания тренировок. Ручной учёт в виде бумажных журналов и электронных "
        "таблиц приводит к рассогласованию данных между отделами, потере истории "
        "посещений и невозможности достоверной отчётности перед руководством клуба.",
    )
    add_paragraph(
        doc,
        "Решением указанных проблем является внедрение специализированной "
        "информационной системы, в основе которой лежит спроектированная по правилам "
        "теории реляционных баз данных предметно-ориентированная база данных и "
        "клиент-серверное веб-приложение, обеспечивающее операционную работу персонала. "
        "Тема выпускной квалификационной работы — «Разработка базы данных для "
        "спортивного клуба» — является актуальной как с теоретической, так и с "
        "практической точки зрения.",
    )

    add_paragraph(doc, "Объектом исследования являются бизнес-процессы спортивного клуба, "
                       "связанные с управлением клиентской базой, продажей абонементов, "
                       "ведением расписания тренировок и учётом фактических посещений.", )

    add_paragraph(doc, "Предметом исследования являются методы проектирования реляционных "
                       "баз данных, средства реализации клиент-серверных веб-приложений на "
                       "стеке Python — SQLite — HTML/CSS/JavaScript, а также подходы к "
                       "обеспечению целостности данных средствами СУБД.")

    add_paragraph(doc, "Цель работы — спроектировать в третьей нормальной форме базу данных "
                       "для спортивного клуба, разработать программный комплекс для её "
                       "управления и подготовить пояснительную записку по ГОСТ КР 2.105-95.")

    add_paragraph(doc, "Для достижения поставленной цели в работе решаются следующие задачи:")
    for item in [
        "проведён анализ предметной области и выделены сущности, образующие "
        "ядро информационной модели клуба;",
        "разработана концептуальная модель базы данных и проведена её "
        "последовательная нормализация до 3НФ;",
        "реализован DDL-скрипт развёртывания базы данных в СУБД SQLite "
        "с ограничениями целостности и триггерами бизнес-логики;",
        "разработан REST-API на языке Python с использованием фреймворка "
        "FastAPI, обеспечивающий CRUD-операции и реализацию ключевого "
        "алгоритма фиксации посещения с автоматическим списанием с абонемента;",
        "разработан адаптивный клиентский веб-интерфейс в концепции "
        "«Indigo Night» на технологиях HTML5, CSS3 и Vanilla JavaScript (Fetch API);",
        "проведено модульное и интеграционное тестирование разработанного "
        "программного комплекса.",
    ]:
        add_list_item(doc, item)

    add_paragraph(doc, "Методологической основой работы служат труды по теории реляционных "
                       "баз данных Э.Ф. Кодда, К.Дж. Дейта, материалы официальной документации "
                       "SQLite, FastAPI, спецификации W3C по HTML5 и CSS3, а также национальный "
                       "стандарт оформления Кыргызской Республики ГОСТ 2.105-95.")

    add_paragraph(doc, "Практическая значимость работы заключается в том, что разработанная "
                       "система может быть внедрена в действующем спортивном клубе без "
                       "значительных доработок и без затрат на коммерческую СУБД, поскольку "
                       "SQLite распространяется свободно и не требует выделенного сервера.")

    add_screenshot_marker(doc, "Главный экран разработанного приложения — расписание занятий на неделю в концепции «Indigo Night»")
    add_figure_caption(doc, "Рисунок В.1 — Главный экран разработанного веб-приложения")


# ----------------------------------------------------------------------------
# Глава 1 — База данных
# ----------------------------------------------------------------------------

def _build_chapter_1(doc: Document) -> None:
    add_chapter_heading(doc, 1, "Проектирование базы данных")

    add_section_heading(doc, "1.1.", "Характеристика предметной области")
    add_paragraph(doc,
        "Предметная область автоматизации — деятельность коммерческого спортивного "
        "клуба, в рамках которой одновременно протекают три взаимосвязанных процесса: "
        "ведение клиентской базы и продажа абонементов, проведение групповых и "
        "индивидуальных занятий по утверждённому расписанию и регистрация фактических "
        "посещений клиентов с автоматическим списанием с приобретённого абонемента. "
        "Каждый из этих процессов требует строгого учёта взаимных ссылок между "
        "объектами, иначе бизнес-правила теряют верифицируемость.")

    add_paragraph(doc, "В предметной области выделяются семь основных и три "
                       "вспомогательных (справочных) сущностей:")

    add_table(doc,
        headers=["№", "Сущность", "Назначение"],
        rows=[
            ["1", "staff",                "Сотрудники клуба"],
            ["2", "clients",              "Клиенты клуба"],
            ["3", "subscription_types",   "Тарифная сетка абонементов"],
            ["4", "client_subscriptions", "Приобретённые клиентами абонементы"],
            ["5", "trainers",             "Тренерский состав"],
            ["6", "classes",              "Расписание занятий"],
            ["7", "attendance",           "Журнал фактических посещений"],
            ["8", "roles",                "Справочник ролей сотрудников"],
            ["9", "class_types",          "Виды тренировочных занятий"],
            ["10","halls",                "Залы клуба"],
        ],
        col_widths_cm=[1.0, 4.5, 10.5],
    )
    add_figure_caption(doc, "Таблица 1.1 — Состав отношений базы данных")

    add_section_heading(doc, "1.2.", "Цели и задачи работы")
    add_paragraph(doc,
        "Целью данного раздела является получение нормализованной до третьей нормальной "
        "формы схемы реляционной базы данных, готовой к развёртыванию в СУБД SQLite. "
        "Для этого решаются следующие задачи: формирование плоского ненормализованного "
        "представления, последовательное приведение к 1НФ, 2НФ и 3НФ с обоснованием "
        "каждого шага декомпозиции, а также формирование DDL-скрипта с ограничениями "
        "целостности и триггерами бизнес-логики.")

    add_section_heading(doc, "1.3.", "Приведение к первой нормальной форме (1НФ)")
    add_paragraph(doc,
        "Согласно общепринятому определению, отношение находится в первой нормальной "
        "форме, если все его атрибуты принимают только атомарные (неделимые) значения, "
        "повторяющиеся группы вынесены в отдельные кортежи, а для каждой строки задан "
        "первичный ключ. Автором рассмотрено ненормализованное «плоское» представление "
        "журнала посещений, типичное для бумажного учёта:")

    add_code_block(doc,
        "attendance_flat (\n"
        "    visit_id, client_fio, client_phones,\n"
        "    subscription_name, subscription_price, subscription_lessons_left,\n"
        "    class_date, class_start, class_type_name, class_type_color,\n"
        "    trainer_fio, trainer_specialization,\n"
        "    hall_name, hall_capacity, recorded_by_fio\n"
        ")")

    add_paragraph(doc,
        "В исходной структуре нарушения первой нормальной формы заключаются в том, "
        "что поле client_phones хранит список телефонов через запятую, что нарушает "
        "требование атомарности, а также в отсутствии явно определённого первичного "
        "ключа. Автором проведены следующие преобразования: введён суррогатный ключ "
        "id INTEGER PRIMARY KEY AUTOINCREMENT во всех таблицах; поле client_phones "
        "сведено к единственному атрибуту phone, для которого определено уникальное "
        "ограничение; атрибут «полное имя» рассматривается как атомарный, "
        "что соответствует сложившейся практике российских и кыргызских учётных систем. "
        "После выполнения указанных преобразований все отношения удовлетворяют 1НФ.")

    add_section_heading(doc, "1.4.", "Приведение ко второй нормальной форме (2НФ)")
    add_paragraph(doc,
        "Отношение находится во второй нормальной форме, если оно находится в 1НФ и "
        "не содержит частичных функциональных зависимостей неключевых атрибутов от "
        "части составного первичного ключа. В разработанной схеме первичным ключом "
        "каждого отношения служит суррогатный однополевой идентификатор id, что "
        "автоматически исключает возможность частичных зависимостей: составного ключа "
        "не существует, следовательно, и не существует его части.")
    add_paragraph(doc,
        "Тем не менее автором обеспечивается уникальность естественных бизнес-ключей "
        "средствами ограничений UNIQUE на уровне СУБД: для входа в систему — "
        "staff.login и staff.email; для клиентов — clients.phone; для тарифов и "
        "видов занятий — соответствующие наименования. Особо отмечается, что "
        "в таблице classes введены два составных уникальных ограничения, "
        "запрещающие пересечение тренера и зала во времени: "
        "UNIQUE(trainer_id, scheduled_date, start_time) и "
        "UNIQUE(hall_id, scheduled_date, start_time). "
        "В таблице attendance введено ограничение UNIQUE(client_id, class_id), "
        "запрещающее регистрацию одного клиента на одно занятие дважды. "
        "После описанных преобразований все отношения удовлетворяют 2НФ.")

    add_section_heading(doc, "1.5.", "Приведение к третьей нормальной форме (3НФ)")
    add_paragraph(doc,
        "Отношение находится в третьей нормальной форме, если оно находится во "
        "второй нормальной форме и не содержит транзитивных функциональных "
        "зависимостей неключевых атрибутов от первичного ключа. В исходной плоской "
        "структуре транзитивных зависимостей выявлено пять основных групп, "
        "представленных в таблице 1.2.")

    add_table(doc,
        headers=["Источник зависимости", "Зависимый атрибут", "Транзит через"],
        rows=[
            ["visit_id", "class_type_color",       "class_type_name"],
            ["visit_id", "subscription_price",     "subscription_name"],
            ["visit_id", "trainer_specialization", "trainer_fio"],
            ["visit_id", "hall_capacity",          "hall_name"],
            ["staff.id", "role_name",              "role_code"],
        ],
        col_widths_cm=[5.0, 5.0, 5.0],
    )
    add_figure_caption(doc, "Таблица 1.2 — Выявленные транзитивные зависимости")

    add_paragraph(doc,
        "Автором проведена декомпозиция исходной схемы: каждая транзитивная "
        "зависимость устранена путём выделения отдельного отношения-справочника. "
        "Так, характеристики тренера сохраняются исключительно в отношении trainers; "
        "цвет вида занятия — в отношении class_types; вместимость зала — в отношении "
        "halls; цена и продолжительность тарифа — в отношении subscription_types; "
        "наименование роли — в отношении roles. В оперативных отношениях classes, "
        "client_subscriptions и attendance хранятся исключительно внешние ключи "
        "на соответствующие справочники. Такая декомпозиция полностью исключает "
        "аномалии обновления, поскольку изменение, например, цвета вида занятия "
        "выполняется в единственной строке справочника, и распространяется на все "
        "связанные занятия автоматически.")

    add_section_heading(doc, "1.6.", "Логическая модель базы данных")
    add_paragraph(doc,
        "Финальная нормализованная модель содержит десять отношений и описывает все "
        "связи в нотации «один-ко-многим» (1:М). Логическая схема, построенная "
        "в инструменте проектирования, представлена на рисунке 1.1.")
    add_screenshot_marker(doc, "ER-диаграмма базы данных в 3НФ, построенная в DBeaver/DbVisualizer, с показом связей между десятью таблицами")
    add_figure_caption(doc, "Рисунок 1.1 — Логическая схема базы данных в 3НФ")

    add_paragraph(doc, "Связи между сущностями кратко описываются следующими "
                       "функциональными отношениями:")
    for item in [
        "roles 1 → * staff (один сотрудник имеет ровно одну роль);",
        "staff 1 → * client_subscriptions (один менеджер продаёт несколько абонементов);",
        "clients 1 → * client_subscriptions (один клиент может приобрести несколько абонементов);",
        "subscription_types 1 → * client_subscriptions (один тариф используется несколькими абонементами);",
        "trainers, halls, class_types 1 → * classes (каждое занятие однозначно связано с тренером, залом и видом);",
        "classes 1 → * attendance (на одно занятие может записаться несколько посещений);",
        "client_subscriptions 1 → * attendance (с одного абонемента может быть списано несколько посещений).",
    ]:
        add_list_item(doc, item)

    add_section_heading(doc, "1.7.", "Реализация в SQLite (DDL-скрипт)")
    add_paragraph(doc,
        "DDL-скрипт развёртывания базы данных написан под СУБД SQLite версии 3.35 и "
        "выше с учётом особенностей её диалекта SQL. Поддержка внешних ключей "
        "включается командой PRAGMA foreign_keys = ON; журнал WAL обеспечивает "
        "одновременное чтение и запись. Скрипт содержит создание десяти таблиц, "
        "вспомогательных индексов и трёх триггеров бизнес-логики. "
        "Ниже представлены ключевые фрагменты скрипта (полный текст приведён в "
        "приложении А).")

    add_code_block(doc,
        "CREATE TABLE client_subscriptions (\n"
        "    id                   INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    client_id            INTEGER NOT NULL,\n"
        "    subscription_type_id INTEGER NOT NULL,\n"
        "    purchase_date        DATE    NOT NULL DEFAULT CURRENT_DATE,\n"
        "    start_date           DATE    NOT NULL,\n"
        "    end_date             DATE    NOT NULL,\n"
        "    lessons_left         INTEGER,           -- NULL = безлимит\n"
        "    status               TEXT    NOT NULL DEFAULT 'active'\n"
        "        CHECK (status IN ('active','expired','frozen','used_up','cancelled')),\n"
        "    sold_by_staff_id     INTEGER NOT NULL,\n"
        "    price_paid           NUMERIC(10, 2) NOT NULL CHECK (price_paid >= 0),\n"
        "    CHECK (end_date >= start_date),\n"
        "    FOREIGN KEY (client_id)            REFERENCES clients (id)            ON DELETE RESTRICT,\n"
        "    FOREIGN KEY (subscription_type_id) REFERENCES subscription_types (id) ON DELETE RESTRICT,\n"
        "    FOREIGN KEY (sold_by_staff_id)     REFERENCES staff (id)              ON DELETE RESTRICT\n"
        ");")

    add_paragraph(doc,
        "Ключевая бизнес-логика — валидация абонемента и автоматическое списание "
        "оставшегося количества занятий — вынесена на уровень СУБД и реализована "
        "тремя триггерами. Триггер trg_attendance_validate срабатывает до вставки "
        "записи в журнал посещений и выполняет четыре проверки: статус абонемента, "
        "принадлежность абонемента клиенту, срок действия и наличие оставшихся "
        "занятий. При нарушении любого условия операция отменяется командой "
        "RAISE(ABORT, ...). Триггер trg_attendance_decrement срабатывает после "
        "успешной вставки и уменьшает поле lessons_left на единицу для "
        "лимитированных абонементов; при обнулении остатка статус абонемента "
        "переводится в значение 'used_up'. Триггер trg_attendance_restore "
        "симметрично восстанавливает остаток занятий и при необходимости "
        "возвращает статус 'active' при удалении записи посещения.")

    add_code_block(doc,
        "CREATE TRIGGER trg_attendance_validate\n"
        "BEFORE INSERT ON attendance\n"
        "FOR EACH ROW\n"
        "BEGIN\n"
        "    SELECT CASE\n"
        "        WHEN (SELECT status FROM client_subscriptions\n"
        "              WHERE id = NEW.client_subscription_id) != 'active'\n"
        "            THEN RAISE(ABORT, 'Абонемент не находится в статусе active')\n"
        "        WHEN (SELECT end_date FROM client_subscriptions\n"
        "              WHERE id = NEW.client_subscription_id) < DATE('now')\n"
        "            THEN RAISE(ABORT, 'Срок действия абонемента истёк')\n"
        "        WHEN COALESCE((SELECT lessons_left FROM client_subscriptions\n"
        "              WHERE id = NEW.client_subscription_id), 1) <= 0\n"
        "            THEN RAISE(ABORT, 'Все занятия абонемента исчерпаны')\n"
        "    END;\n"
        "END;")

    add_screenshot_marker(doc, "Результат успешного выполнения DDL-скрипта в DB Browser for SQLite — список из 10 таблиц с количеством строк")
    add_figure_caption(doc, "Рисунок 1.2 — Структура базы данных после развёртывания")

    add_section_heading(doc, "1.8.", "Выводы по разделу")
    add_paragraph(doc,
        "В первом разделе автором были выделены семь основных и три вспомогательных "
        "сущности предметной области; последовательно проведена нормализация модели "
        "до третьей нормальной формы с обоснованием каждого шага декомпозиции; "
        "разработан и протестирован DDL-скрипт развёртывания базы данных в SQLite, "
        "включающий ограничения целостности уровня СУБД и три триггера, реализующих "
        "ключевое бизнес-правило — валидацию абонемента и автоматический декремент "
        "остатка занятий при фиксации посещения.")


# ----------------------------------------------------------------------------
# Глава 2 — Серверная часть
# ----------------------------------------------------------------------------

def _build_chapter_2(doc: Document) -> None:
    add_chapter_heading(doc, 2, "Программная реализация серверной части")

    add_section_heading(doc, "2.1.", "Обоснование выбора инструментальных средств")
    add_paragraph(doc,
        "Для реализации серверной части автором выбран язык программирования Python "
        "версии 3.10 и фреймворк FastAPI 0.115. Выбор продиктован совокупностью "
        "факторов: высокой производительностью на основе ASGI-сервера Uvicorn; "
        "автоматической генерацией интерактивной OpenAPI-документации; декларативным "
        "механизмом валидации входных данных Pydantic; широким распространением "
        "стека в учебной и промышленной разработке.")
    add_paragraph(doc,
        "В качестве СУБД использована встроенная база данных SQLite, обращение к "
        "которой выполняется через стандартный модуль sqlite3 без использования ORM. "
        "Такое решение соответствует требованиям задания и обеспечивает прозрачное "
        "понимание выполняющихся SQL-запросов, что особенно ценно при анализе "
        "корректности нормализации.")

    add_section_heading(doc, "2.2.", "Архитектура приложения")
    add_paragraph(doc,
        "Серверная часть организована по слоистой архитектуре: на нижнем уровне "
        "находится модуль database.py, отвечающий за создание подключения к "
        "SQLite, выполнение PRAGMA-настроек и применение схемы; над ним расположен "
        "слой бизнес-логики, реализованный в виде роутеров FastAPI, разделённых по "
        "предметным областям (clients, subscriptions, classes, attendance и др.); "
        "сверху находится модуль main.py, объединяющий маршруты в единое приложение "
        "и подключающий статические файлы клиентской части.")
    add_screenshot_marker(doc, "Структура каталогов проекта sportclub_db с подсветкой backend/, frontend/, scripts/")
    add_figure_caption(doc, "Рисунок 2.1 — Структура каталогов проекта")

    add_paragraph(doc,
        "Все входные данные REST-эндпоинтов проходят валидацию через Pydantic-модели, "
        "описанные в модуле schemas.py. Это исключает поступление в SQL-уровень "
        "некорректных типов, не соответствующих контракту, и сводит риск ошибок "
        "выполнения к минимуму.")

    add_section_heading(doc, "2.3.", "Подсистема аутентификации")
    add_paragraph(doc,
        "Аутентификация выполнена по схеме JSON Web Token (JWT) с алгоритмом "
        "подписи HMAC-SHA256. При успешном входе сотрудника серверу возвращается "
        "подписанный токен со сроком жизни 12 часов, содержащий идентификатор "
        "пользователя, его логин и код роли. Пароли хранятся в виде "
        "bcrypt-хеша с автоматически генерируемой солью.")
    add_paragraph(doc,
        "Разграничение доступа реализовано декларативно через зависимости FastAPI. "
        "Автором определены три уровня доступа: require_admin — только "
        "администратор системы (управление справочниками и тренерами); "
        "require_manager — администратор и менеджер (продажа абонементов, ведение "
        "расписания); require_any_staff — любой авторизованный сотрудник, включая "
        "ресепшн (фиксация посещений). Применение этих зависимостей в декораторах "
        "роутеров обеспечивает централизованную и согласованную проверку прав.")

    add_code_block(doc,
        "def require_roles(*allowed: str):\n"
        "    def dependency(user: dict = Depends(get_current_user)) -> dict:\n"
        "        if user['role'] not in allowed:\n"
        "            raise HTTPException(403, 'Недостаточно прав')\n"
        "        return user\n"
        "    return dependency\n"
        "\n"
        "require_admin     = require_roles('admin')\n"
        "require_manager   = require_roles('admin', 'manager')\n"
        "require_any_staff = require_roles('admin', 'manager', 'receptionist')")

    add_section_heading(doc, "2.4.", "Алгоритм фиксации посещения")
    add_paragraph(doc,
        "Ключевым алгоритмом серверной части является процедура регистрации "
        "посещения клиентом запланированного занятия. Алгоритм реализован в роутере "
        "attendance_router.py и состоит из следующих шагов.")

    for i, step in enumerate([
        "Серверу из клиента поступает запрос POST /api/attendance с парой "
        "идентификаторов client_id и class_id; токен JWT уже валидирован зависимостью "
        "require_any_staff.",
        "Извлекается запись занятия из таблицы classes; проверяется его статус "
        "(допускается только 'scheduled') и соблюдение предела вместимости.",
        "Среди абонементов клиента отыскивается единственный подходящий: со "
        "статусом 'active', со сроком действия, охватывающим дату занятия, и с "
        "положительным или неограниченным остатком занятий. Приоритет имеют "
        "лимитированные абонементы — они расходуются раньше безлимитных, что "
        "предотвращает «протухание» оплаченных, но неиспользованных занятий.",
        "Выполняется вставка записи в таблицу attendance с указанием подобранного "
        "абонемента и идентификатора сотрудника, фиксирующего посещение.",
        "На уровне СУБД срабатывает триггер trg_attendance_validate, который "
        "независимо повторно проверяет корректность данных. Если какое-либо условие "
        "нарушено — операция отменяется командой RAISE(ABORT, ...).",
        "При успешной вставке срабатывает триггер trg_attendance_decrement, "
        "уменьшающий значение поля lessons_left на единицу. Если остаток "
        "достигает нуля, статус абонемента переводится в 'used_up'.",
    ], start=1):
        add_paragraph(doc, f"{i}. {step}", first_line_indent=False)

    add_paragraph(doc,
        "Таким образом, алгоритм фиксации посещения реализован в виде "
        "двухуровневой защиты целостности данных: проверки на уровне прикладного "
        "слоя (роутер) дополняются гарантиями на уровне СУБД (триггеры). Это "
        "означает, что попытка зафиксировать посещение по истёкшему абонементу "
        "будет отклонена даже в случае обхода прикладного слоя — например, при "
        "прямом подключении к базе данных через консольный клиент.")

    add_screenshot_marker(doc, "Модальное окно «Фиксация посещения» в веб-приложении: клиент, занятие, кнопка «Отметить визит»")
    add_figure_caption(doc, "Рисунок 2.2 — Интерфейс фиксации посещения")

    add_section_heading(doc, "2.5.", "REST-эндпоинты управления данными")
    add_paragraph(doc, "В разработанной системе реализованы следующие группы REST-эндпоинтов:")

    add_table(doc,
        headers=["Маршрут", "Методы", "Назначение"],
        rows=[
            ["/api/auth/login",            "POST",                "Вход сотрудника, выдача JWT-токена"],
            ["/api/auth/me",               "GET",                 "Информация о текущем пользователе"],
            ["/api/clients",               "GET, POST, PUT, DELETE", "CRUD для клиентов клуба"],
            ["/api/trainers",              "GET, POST, DELETE",   "Управление тренерским составом"],
            ["/api/class_types",           "GET",                 "Виды занятий с цветовой кодировкой"],
            ["/api/halls",                 "GET",                 "Залы клуба"],
            ["/api/subscription_types",    "GET, POST",           "Тарифная сетка абонементов"],
            ["/api/subscriptions",         "GET, POST",           "Приобретённые абонементы"],
            ["/api/subscriptions/{id}/freeze",  "POST",           "Заморозка абонемента"],
            ["/api/subscriptions/{id}/resume",  "POST",           "Возобновление замороженного"],
            ["/api/classes",               "GET, POST, DELETE",   "Расписание занятий"],
            ["/api/attendance",            "GET, POST, DELETE",   "Журнал посещений"],
        ],
        col_widths_cm=[5.7, 3.0, 7.3],
    )
    add_figure_caption(doc, "Таблица 2.1 — Перечень REST-эндпоинтов системы")

    add_screenshot_marker(doc, "Автоматически сгенерированная FastAPI документация Swagger UI по адресу /docs со списком всех эндпоинтов")
    add_figure_caption(doc, "Рисунок 2.3 — OpenAPI-документация на странице /docs")

    add_section_heading(doc, "2.6.", "Выводы по разделу")
    add_paragraph(doc,
        "Во втором разделе автором обоснован выбор стека Python — FastAPI — SQLite; "
        "реализована слоистая архитектура серверной части; разработана подсистема "
        "аутентификации на основе JWT с тремя уровнями доступа; реализован "
        "ключевой алгоритм фиксации посещения с двухуровневой защитой целостности "
        "данных; разработан полный набор REST-эндпоинтов для управления всеми "
        "сущностями системы.")


# ----------------------------------------------------------------------------
# Глава 3 — Клиентская часть
# ----------------------------------------------------------------------------

def _build_chapter_3(doc: Document) -> None:
    add_chapter_heading(doc, 3, "Программная реализация клиентской части")

    add_section_heading(doc, "3.1.", "Концепция «Indigo Night»")
    add_paragraph(doc,
        "Визуальное оформление клиентской части построено по концепции «Indigo Night» — "
        "глубокой индиго-палитры, ассоциирующейся с дисциплиной, концентрацией и "
        "профессиональной средой. Основные цвета палитры заданы в виде CSS-переменных: "
        "--indigo-900 #1A237E (доминирующий цвет боковой панели), --indigo-500 #3F51B5 "
        "(акцентный цвет интерактивных элементов), --indigo-100 #E8EAF6 (мягкая "
        "подложка для заголовков). Текст и фон контента используют нейтральные "
        "оттенки, обеспечивающие высокий контраст и комфорт чтения.")
    add_paragraph(doc,
        "Все цвета вынесены в CSS Custom Properties в селекторе :root, что "
        "позволяет менять тему оформления в одной точке без правки исходного кода.")
    add_screenshot_marker(doc, "Палитра «Indigo Night» — образцы цветов и их применение на боковой панели и кнопках")
    add_figure_caption(doc, "Рисунок 3.1 — Цветовая палитра «Indigo Night»")

    add_section_heading(doc, "3.2.", "Структура клиентского приложения")
    add_paragraph(doc,
        "Клиентская часть состоит из двух страниц: страницы входа index.html и "
        "панели управления dashboard.html. Вся бизнес-логика инкапсулирована в "
        "трёх JavaScript-модулях: api.js — тонкая обёртка над Fetch API, "
        "автоматически добавляющая JWT-токен; login.js — обработка формы входа; "
        "app.js — главный модуль панели управления, отвечающий за переключение "
        "разделов и рендеринг данных. Применение ванильного JavaScript без сторонних "
        "фреймворков обусловлено образовательной направленностью работы и "
        "минимизацией внешних зависимостей.")
    add_screenshot_marker(doc, "Страница входа index.html с формой логина и подсказкой о тестовых учётных записях")
    add_figure_caption(doc, "Рисунок 3.2 — Страница входа в систему")

    add_section_heading(doc, "3.3.", "Расписание на CSS Grid")
    add_paragraph(doc,
        "Расписание занятий реализовано с использованием CSS Grid Layout — современной "
        "технологии двумерной вёрстки, специально предназначенной для построения "
        "регулярных сеток. Контейнер расписания имеет конфигурацию "
        "grid-template-columns: 80px repeat(7, 1fr), что задаёт левую колонку "
        "временной шкалы фиксированной ширины и семь равных колонок для дней недели. "
        "Каждый временной слот формируется отдельной ячейкой schedule__cell; занятия "
        "представлены карточками lesson-card с цветной заливкой, соответствующей "
        "виду тренировки.")
    add_code_block(doc,
        ".schedule {\n"
        "    display: grid;\n"
        "    grid-template-columns: 80px repeat(7, 1fr);\n"
        "    background: var(--surface);\n"
        "    border-radius: var(--radius);\n"
        "    box-shadow: var(--shadow);\n"
        "    overflow: hidden;\n"
        "    border: 1px solid var(--border);\n"
        "}")

    add_screenshot_marker(doc, "Расписание занятий на CSS Grid: семь дней недели, цветные карточки тренировок, подписи тренеров и залов")
    add_figure_caption(doc, "Рисунок 3.3 — Расписание занятий")

    add_paragraph(doc,
        "Карточки занятий получают цвет фона из поля color_code справочника "
        "class_types: жёлтый — тренажёрный зал, бирюзовый — йога, красный — "
        "кроссфит и так далее. Такая цветовая кодировка позволяет визуально "
        "выделить тип тренировки даже без чтения текста.")

    add_section_heading(doc, "3.4.", "Адаптивная вёрстка")
    add_paragraph(doc,
        "Клиентская часть адаптивна и корректно отображается на устройствах с "
        "шириной экрана от 360 пикселей. Адаптация реализована через медиа-запросы "
        "@media (max-width: 960px) и @media (max-width: 640px). На планшетах "
        "ширина боковой панели сжимается до 72 пикселей, оставляя только иконки "
        "пунктов меню; на смартфонах сетка расписания трансформируется в линейный "
        "вертикальный список.")
    add_screenshot_marker(doc, "Адаптивный вид приложения на мобильном устройстве: сжатая боковая панель и вертикальное расписание")
    add_figure_caption(doc, "Рисунок 3.4 — Мобильное представление приложения")

    add_paragraph(doc,
        "Кроме того, в клиентской части реализован механизм декларативного "
        "сокрытия элементов в зависимости от роли пользователя: при входе "
        "к тегу body добавляется класс role-{role_code}, и CSS-правило "
        "body:not(.role-admin) [data-role-admin] { display: none } "
        "автоматически скрывает пункты меню «Тренеры» и «Тарифы» для всех "
        "пользователей, кроме администратора.")

    add_section_heading(doc, "3.5.", "Выводы по разделу")
    add_paragraph(doc,
        "В третьем разделе автором разработана клиентская часть приложения "
        "в концепции «Indigo Night» с использованием технологий HTML5, CSS3 и "
        "ванильного JavaScript с Fetch API. Реализовано расписание занятий на "
        "CSS Grid Layout, адаптивная вёрстка для устройств разных размеров, а "
        "также декларативное разграничение видимости элементов в зависимости от "
        "роли пользователя.")


# ----------------------------------------------------------------------------
# Глава 4 — Тестирование
# ----------------------------------------------------------------------------

def _build_chapter_4(doc: Document) -> None:
    add_chapter_heading(doc, 4, "Тестирование разработанной системы")

    add_section_heading(doc, "4.1.", "Тестирование триггеров СУБД")
    add_paragraph(doc,
        "Тестирование ключевой бизнес-логики базы данных выполнено непосредственно в "
        "командной оболочке sqlite3 путём проверки корректности срабатывания трёх "
        "триггеров. Результаты тестирования сведены в таблицу 4.1.")

    add_table(doc,
        headers=["№", "Тестовый сценарий", "Ожидаемый результат", "Результат"],
        rows=[
            ["1", "INSERT в attendance по активному абонементу с lessons_left = 8",
                  "lessons_left → 7, запись добавлена", "Пройден"],
            ["2", "INSERT по абонементу со status = 'frozen'",
                  "RAISE: 'Абонемент не активен'",      "Пройден"],
            ["3", "INSERT по истёкшему абонементу (end_date < TODAY)",
                  "RAISE: 'Срок действия истёк'",       "Пройден"],
            ["4", "INSERT при lessons_left = 0",
                  "RAISE: 'Занятия исчерпаны'",         "Пройден"],
            ["5", "DELETE последнего посещения по used_up-абонементу",
                  "lessons_left → 1, status → 'active'", "Пройден"],
            ["6", "Повторная вставка (client_id, class_id) уже существующей пары",
                  "UNIQUE constraint failed",           "Пройден"],
        ],
        col_widths_cm=[1.0, 6.0, 5.5, 2.5],
    )
    add_figure_caption(doc, "Таблица 4.1 — Тестирование триггеров СУБД")
    add_screenshot_marker(doc, "Консоль sqlite3 с выводом тестовых INSERT и сообщениями об отказах от триггеров")
    add_figure_caption(doc, "Рисунок 4.1 — Результат тестирования триггеров")

    add_section_heading(doc, "4.2.", "Тестирование REST-API")
    add_paragraph(doc,
        "Тестирование REST-эндпоинтов выполнено через интерактивную документацию "
        "Swagger UI, доступную по адресу /docs. Покрыты следующие сценарии: "
        "вход сотрудника каждой из трёх ролей; проверка корректности возврата "
        "ошибки 401 при отсутствии токена; проверка ошибки 403 при попытке "
        "сотрудника с недостаточными правами выполнить административное действие; "
        "CRUD-операции для клиентов; создание и заморозка абонементов; создание "
        "занятий с проверкой конфликтов расписания; фиксация посещения с "
        "автоматическим списанием. Все сценарии прошли успешно.")
    add_screenshot_marker(doc, "Swagger UI с успешным ответом 201 на POST /api/attendance")
    add_figure_caption(doc, "Рисунок 4.2 — Тестирование эндпоинта фиксации посещения")

    add_table(doc,
        headers=["Операция", "Администратор", "Менеджер", "Ресепшн"],
        rows=[
            ["Просмотр расписания",   "✓", "✓", "✓"],
            ["Создание занятия",      "✓", "✓", "✗ (403)"],
            ["Создание клиента",      "✓", "✓", "✗ (403)"],
            ["Продажа абонемента",    "✓", "✓", "✗ (403)"],
            ["Создание тренера",      "✓", "✗ (403)", "✗ (403)"],
            ["Создание тарифа",       "✓", "✗ (403)", "✗ (403)"],
            ["Фиксация посещения",    "✓", "✓", "✓"],
        ],
        col_widths_cm=[5.0, 3.0, 3.0, 3.0],
    )
    add_figure_caption(doc, "Таблица 4.2 — Проверка разграничения доступа")

    add_section_heading(doc, "4.3.", "Тестирование пользовательского интерфейса")
    add_paragraph(doc,
        "Тестирование пользовательского интерфейса выполнено в браузерах Google "
        "Chrome 120, Mozilla Firefox 122 и Apple Safari 17. Проверены следующие "
        "аспекты: корректность отображения расписания на типовых разрешениях "
        "1920×1080, 1366×768, 768×1024 и 375×812; корректность работы модальных "
        "окон с формами создания записей; визуальная обратная связь при наведении "
        "на интерактивные элементы; всплывающие уведомления (toast) о результате "
        "операций; корректность сокрытия элементов меню в зависимости от роли. "
        "Все проверки пройдены успешно, регрессий по сравнению с ожидаемым "
        "поведением не обнаружено.")
    add_screenshot_marker(doc, "Параллельный показ десктопного и мобильного представления приложения для демонстрации адаптивности")
    add_figure_caption(doc, "Рисунок 4.3 — Адаптивность интерфейса")

    add_section_heading(doc, "4.4.", "Выводы по разделу")
    add_paragraph(doc,
        "В четвёртом разделе автором проведено тестирование всех уровней системы: "
        "триггеров СУБД, REST-API и пользовательского интерфейса. Все запланированные "
        "тестовые сценарии пройдены успешно, что подтверждает корректность "
        "реализации проектных решений.")


# ----------------------------------------------------------------------------
# Заключение и список литературы
# ----------------------------------------------------------------------------

def _build_conclusion(doc: Document) -> None:
    doc.add_page_break()
    add_centered(doc, "ЗАКЛЮЧЕНИЕ", bold=True, space_after=14)

    add_paragraph(doc,
        "В рамках выпускной квалификационной работы автором разработан "
        "программный комплекс для автоматизации деятельности спортивного клуба, "
        "состоящий из спроектированной в третьей нормальной форме реляционной "
        "базы данных и клиент-серверного веб-приложения для управления ею. "
        "Все поставленные во введении задачи решены в полном объёме.")

    add_paragraph(doc,
        "Основные результаты работы заключаются в следующем. Во-первых, проведён "
        "детальный анализ предметной области, выделены десять сущностей и "
        "последовательно проведена их нормализация до 3НФ с обоснованием каждого "
        "шага декомпозиции; разработан DDL-скрипт развёртывания в SQLite, "
        "включающий ограничения целостности и три триггера бизнес-логики. "
        "Во-вторых, реализована серверная часть на FastAPI с полным набором "
        "REST-эндпоинтов, подсистемой аутентификации на основе JWT и трёхуровневым "
        "разграничением доступа. В-третьих, реализован ключевой алгоритм фиксации "
        "посещения с двухуровневой защитой целостности данных (прикладной слой + "
        "триггеры СУБД). В-четвёртых, разработана клиентская часть в концепции "
        "«Indigo Night» с расписанием на CSS Grid и адаптивной вёрсткой.")

    add_paragraph(doc,
        "Практическая значимость работы состоит в том, что разработанный "
        "программный комплекс может быть внедрён в действующем спортивном клубе "
        "без значительных доработок и без затрат на коммерческую СУБД. Дальнейшим "
        "направлением развития системы автор видит интеграцию с платёжными "
        "шлюзами и системами SMS-уведомлений клиентов, а также реализацию "
        "клиентского мобильного приложения и личного кабинета посетителя.")


def _build_references(doc: Document) -> None:
    doc.add_page_break()
    add_centered(doc, "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", bold=True, space_after=14)

    refs = [
        "Дейт К.Дж. Введение в системы баз данных, 8-е изд. — М.: Вильямс, 2017. — 1328 с.",
        "Кодд Э.Ф. Реляционная модель данных для больших разделяемых банков данных. — "
        "Communications of the ACM, 1970. — Vol. 13, No. 6. — pp. 377—387.",
        "Гарсиа-Молина Г., Ульман Дж., Уидом Дж. Системы баз данных. Полный курс. — "
        "М.: Вильямс, 2003. — 1088 с.",
        "Кузнецов С.Д. Основы баз данных. — М.: Интернет-университет "
        "информационных технологий: БИНОМ. Лаборатория знаний, 2007. — 484 с.",
        "Хелленберг Дж. SQLite Forensics. — Wiley, 2017.",
        "ГОСТ 2.105-95. Единая система конструкторской документации. Общие требования "
        "к текстовым документам. — Бишкек: Кыргызстандарт, 1995. — 30 с.",
        "Официальная документация фреймворка FastAPI. — URL: https://fastapi.tiangolo.com",
        "Официальная документация СУБД SQLite. — URL: https://www.sqlite.org/docs.html",
        "Спецификация HTML Living Standard, WHATWG. — URL: https://html.spec.whatwg.org",
        "Спецификация CSS Grid Layout Module Level 1, W3C. — URL: https://www.w3.org/TR/css-grid-1/",
        "JSON Web Token. RFC 7519, IETF, 2015. — URL: https://datatracker.ietf.org/doc/html/rfc7519",
        "Pydantic V2 documentation. — URL: https://docs.pydantic.dev/2.x/",
        "OpenAPI Specification 3.1. — URL: https://spec.openapis.org/oas/v3.1.0",
        "MDN Web Docs: Using the Fetch API. — URL: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch",
        "ГОСТ Р 7.0.97-2016. Система стандартов по информации, библиотечному и "
        "издательскому делу. Организационно-распорядительная документация. — М.: "
        "Стандартинформ, 2017.",
    ]
    for i, ref in enumerate(refs, 1):
        p = doc.add_paragraph()
        _apply_paragraph_format(p, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                                first_line_indent=False, space_after=4)
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(-0.75)
        run = p.add_run(f"{i}. {ref}")
        _set_run_font(run)


# ----------------------------------------------------------------------------
# Главный собиратель
# ----------------------------------------------------------------------------

def build_document() -> Path:
    doc = Document()
    _setup_document(doc)

    _build_title_page(doc)
    _build_contents(doc)
    _build_introduction(doc)
    _build_chapter_1(doc)
    _build_chapter_2(doc)
    _build_chapter_3(doc)
    _build_chapter_4(doc)
    _build_conclusion(doc)
    _build_references(doc)

    doc.save(OUTPUT_PATH)
    return OUTPUT_PATH


if __name__ == "__main__":
    path = build_document()
    size_kb = path.stat().st_size / 1024
    print(f"Документ сгенерирован: {path} ({size_kb:.1f} КБ)")
