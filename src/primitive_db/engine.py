"""Исполнение пользовательских команд и работа с метаданными."""

from __future__ import annotations

import shlex
from pathlib import Path

from prettytable import PrettyTable

from primitive_db.constants import COMMANDS
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    type_casting,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.utils import (
    _load_config,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
    show_help,
)

# Создаем кэшер для результатов select
_select_cache = create_cacher()

def get_metadata_path() -> Path:
    """Получает путь к файлу метаданных из настроек проекта."""
    config = _load_config()
    return Path(config["metadata_path"])


def parse_where_clause(
    parts: list[str], start_idx: int, metadata: dict, table_name: str
) -> dict | None:
    """
    Парсит условие where из списка частей команды.
    
    Превращает строки вида "age = 28" в словари вида {'age': 28}.
    Требует, чтобы строковые значения были в кавычках.
    
    Args:
        parts: Список частей команды
        start_idx: Индекс начала условия where (где находится слово "where")
        metadata: Метаданные таблиц
        table_name: Имя таблицы
        
    Returns:
        Словарь с условиями или None, если условие не найдено
    """
    if start_idx >= len(parts) or parts[start_idx].lower() != "where":
        return None
    
    if len(parts) < start_idx + 4:
        raise ValueError(
            "Неправильный синтаксис where. "
            "Должно быть where <столбец> = <значение>"
        )
    
    if parts[start_idx + 2] != "=":
        raise ValueError(
            "Неправильный синтаксис where. "
            "Должно быть where <столбец> = <значение>"
        )
    
    column_name = parts[start_idx + 1]
    column_value_str = parts[start_idx + 3]
    
    # Получаем типы столбцов
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name!r} не найдена")
    
    columns_list = metadata[table_name]
    column_types = {}
    for col in columns_list:
        col_name, _, col_type = col.partition(':')
        column_types[col_name] = col_type
    
    if column_name not in column_types:
        raise ValueError(f"Столбец {column_name!r} не найден в таблице")
    
    # Преобразуем значение в нужный тип
    typed_value = type_casting(column_types[column_name], column_value_str)
    
    return {column_name: typed_value}


def parse_set_clause(
    parts: list[str], start_idx: int, metadata: dict, table_name: str
) -> dict:
    """
    Парсит условие set из списка частей команды.
    
    Превращает строки вида "age = 28" в словари вида {'age': 28}.
    Требует, чтобы строковые значения были в кавычках.
    
    Args:
        parts: Список частей команды
        start_idx: Индекс начала условия set (где находится слово "set")
        metadata: Метаданные таблиц
        table_name: Имя таблицы
        
    Returns:
        Словарь с полями для обновления
    """
    if start_idx >= len(parts) or parts[start_idx].lower() != "set":
        raise ValueError(
            "Неправильный синтаксис set. "
            "Должно быть set <столбец> = <значение>"
        )
    
    # Ищем where для определения конца set clause
    where_idx = None
    for i in range(start_idx + 1, len(parts)):
        if parts[i].lower() == "where":
            where_idx = i
            break
    
    if where_idx is None:
        raise ValueError("Нужно указать условие where")
    
    if where_idx - start_idx < 4:
        raise ValueError(
            "Неправильный синтаксис set. "
            "Должно быть set <столбец> = <значение>"
        )
    
    if parts[start_idx + 2] != "=":
        raise ValueError(
            "Неправильный синтаксис set. "
            "Должно быть set <столбец> = <значение>"
        )
    
    column_name = parts[start_idx + 1]
    column_value_str = parts[start_idx + 3]
    
    # Получаем типы столбцов
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name!r} не найдена")
    
    columns_list = metadata[table_name]
    column_types = {}
    for col in columns_list:
        col_name, _, col_type = col.partition(':')
        column_types[col_name] = col_type
    
    if column_name not in column_types:
        raise ValueError(f"Столбец {column_name!r} не найден в таблице")
    
    # Преобразуем значение в нужный тип
    typed_value = type_casting(column_types[column_name], column_value_str)
    
    return {column_name: typed_value}


def get_input(prompt: str = "Введите команду:  ") -> str:
    """Безопасное чтение ввода. На Ctrl+C/EOF возвращает 'quit'."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"

def run() -> None:
    while True:
        # Загружаем метаданные каждый раз, чтобы получить актуальные данные
        # Путь также загружаем каждый раз, чтобы он всегда был актуальным
        metadata_path = get_metadata_path()
        metadata = load_metadata(str(metadata_path))
        command_line = get_input()
        metadata, should_continue = process_command(
            metadata, command_line, metadata_path
        )

        if not should_continue:
            break


def process_command(
    metadata: dict, command_line: str, metadata_path: Path
) -> tuple[dict, bool]:
    """Разбирает введенную строку и исполняет соответствующую команду."""

    command_line = command_line.strip()
    if not command_line:
        return metadata, True

    try:
        parts = shlex.split(command_line)
    except ValueError as error:
        print(f"Ошибка разбора команды: {error}")
        return metadata, True

    if not parts:
        return metadata, True

    cmd = parts[0].lower()

    if cmd == "create_table":
        return handle_create_table(metadata, parts, metadata_path)

    if cmd == "list_tables":
        handle_list_tables(metadata)
        return metadata, True

    if cmd == "drop_table":
        return handle_drop_table(metadata, parts, metadata_path)

    if cmd == "insert":
        return handle_insert(metadata, parts)

    if cmd == "select":
        return handle_select(metadata, parts)

    if cmd == "update":
        return handle_update(metadata, parts)

    if cmd == "delete":
        return handle_delete(metadata, parts)

    if cmd in {"help", "?"}:
        show_help(COMMANDS)
        return metadata, True

    if cmd in {"exit", "quit"}:
        return metadata, False

    print("Неизвестная команда. Введите 'help' для помощи.")
    return metadata, True


def handle_create_table(
    metadata: dict, parts: list[str], metadata_path: Path
) -> tuple[dict, bool]:
    """Создаёт таблицу по команде пользователя."""

    if len(parts) < 3:
        print("Нужно указать имя таблицы и хотя бы один столбец вида <имя:тип>.")
        return metadata, True

    table_name = parts[1]
    columns = parts[2:]

    updated = create_table(metadata, table_name, columns)
    
    if updated is None:
        return metadata, True
    
    metadata_path_str = str(metadata_path.resolve())
    save_metadata(metadata_path_str, updated)
    print(f"Таблица '{table_name}' создана.")
    
    return updated, True


def handle_list_tables(metadata: dict) -> None:
    """Печатает список таблиц с их колонками."""

    tables = list_tables(metadata)

    if not tables:
        print("Таблицы не найдены.")
        return

    print("Список таблиц:")
    for name, columns in tables:
        cols = ", ".join(columns)
        print(f"  - {name}: {cols}")


def handle_drop_table(
    metadata: dict, parts: list[str], metadata_path: Path
) -> tuple[dict, bool]:
    """Удаляет таблицу из метаданных по команде пользователя."""

    if len(parts) < 2:
        print("Нужно указать имя таблицы для удаления.")
        return metadata, True

    table_name = parts[1]

    updated = drop_table(metadata, table_name)
    
    if updated is None:
        return metadata, True
    
    metadata_path_str = str(metadata_path.resolve())
    save_metadata(metadata_path_str, updated)
    print(f"Таблица '{table_name}' удалена.")
    # Очищаем кэш после удаления таблицы
    _select_cache.clear()  # type: ignore
    
    return updated, True

def handle_insert(metadata: dict, parts: list[str]) -> tuple[dict, bool]:
    """Создаёт запись в таблице по команде пользователя."""

    if len(parts) < 4:
        print("Нужно указать имя таблицы и хотя бы одно значение столбца.")
        return metadata, True

    into_keyword = parts[1]

    if into_keyword != "into":
        raise ValueError(
            "Неправильный синтаксис команды. "
            "Должно быть insert into <имя_таблицы> values (<значение1>, ...)"
        )

    table_name = parts[2]
    values_keyword = parts[3]

    if values_keyword != "values":
        raise ValueError(
            "Неправильный синтаксис команды. "
            "Должно быть insert into <имя_таблицы> values (<значение1>, ...)"
        )

    values = parts[4:]
    
    # Очищаем значения от возможных скобок, запятых и пробелов по краям
    cleaned_values = []
    for value in values:
        cleaned = value.strip().lstrip('(').rstrip(')').strip(',').strip()
        cleaned_values.append(cleaned)

    # Загружаем существующие данные таблицы
    table_data = load_table_data(table_name)
    # Преобразуем в список, если это словарь
    if isinstance(table_data, dict):
        table_data = list(table_data.values()) if table_data else []
    elif not isinstance(table_data, list):
        table_data = []

    # insert теперь генерирует ID, валидирует типы и добавляет запись
    # Возвращает измененные данные таблицы
    updated_table_data = insert(metadata, table_name, cleaned_values, table_data)
    
    if updated_table_data is not None:
        save_table_data(table_name, updated_table_data)
        print(f"Запись добавлена в таблицу '{table_name}'.")
        # Очищаем кэш после вставки
        _select_cache.clear()  # type: ignore
    else:
        return metadata, True

    return metadata, True


def handle_select(metadata: dict, parts: list[str]) -> tuple[dict, bool]:
    """Читает записи из таблицы по команде пользователя."""
    
    if len(parts) < 3:
        print("Нужно указать имя таблицы.")
        return metadata, True
    
    from_keyword = parts[1]
    if from_keyword != "from":
        print(
            "Неправильный синтаксис команды. "
            "Должно быть select from <имя_таблицы> [where <столбец> = <значение>]"
        )
        return metadata, True
    
    table_name = parts[2]
    
    # Проверяем существование таблицы
    if table_name not in metadata:
        print(f"Таблица {table_name!r} не найдена")
        return metadata, True
    
    # Загружаем данные таблицы
    table_data = load_table_data(table_name)
    if isinstance(table_data, dict):
        table_data = list(table_data.values()) if table_data else []
    elif not isinstance(table_data, list):
        table_data = []
    
    # Парсим условие where, если есть
    where_clause = None
    if len(parts) > 3:
        try:
            where_clause = parse_where_clause(parts, 3, metadata, table_name)
        except ValueError as error:
            print(error)
            return metadata, True
    
    # Создаем ключ для кэша на основе имени таблицы и условия where
    cache_key = f"{table_name}:{where_clause}"
    
    # Используем кэширование для select
    def perform_select():
        return select(table_data, where_clause)
    
    results = _select_cache(cache_key, perform_select)
    
    if results is None:
        return metadata, True
    
    if not results:
        print("Записи не найдены.")
    else:
        # Используем prettytable для красивого вывода
        # Получаем названия столбцов из первой записи
        columns = list(results[0].keys())
        # Убеждаемся, что ID идет первым
        if 'ID' in columns:
            columns.remove('ID')
            columns.insert(0, 'ID')
        
        table = PrettyTable(columns)
        table.align = "l"  # Выравнивание по левому краю
        table.padding_width = 1  # Отступы
        
        # Добавляем данные
        for record in results:
            row = [record.get(col, '') for col in columns]
            table.add_row(row)
        
        print(table)
    
    return metadata, True


def handle_update(metadata: dict, parts: list[str]) -> tuple[dict, bool]:
    """Обновляет записи в таблице по команде пользователя."""
    
    if len(parts) < 6:
        print("Нужно указать имя таблицы, set и where условия.")
        return metadata, True
    
    table_name = parts[1]
    
    # Проверяем существование таблицы
    if table_name not in metadata:
        print(f"Таблица {table_name!r} не найдена")
        return metadata, True
    
    # Находим индексы set и where
    set_keyword_idx = None
    where_keyword_idx = None
    for i, part in enumerate(parts):
        if part.lower() == "set":
            set_keyword_idx = i
        elif part.lower() == "where":
            where_keyword_idx = i
    
    if set_keyword_idx is None or where_keyword_idx is None:
        print(
            "Неправильный синтаксис команды. "
            "Должно быть update <имя_таблицы> set <столбец> = <значение> "
            "where <столбец> = <значение>"
        )
        return metadata, True
    
    # Загружаем данные таблицы
    table_data = load_table_data(table_name)
    if isinstance(table_data, dict):
        table_data = list(table_data.values()) if table_data else []
    elif not isinstance(table_data, list):
        table_data = []
    
    # Парсим set и where условия используя парсеры
    try:
        set_clause = parse_set_clause(
            parts, set_keyword_idx, metadata, table_name
        )
        where_clause = parse_where_clause(
            parts, where_keyword_idx, metadata, table_name
        )
        
        if where_clause is None:
            print("Нужно указать условие where.")
            return metadata, True
    except ValueError as error:
        print(error)
        return metadata, True
    
    # Выполняем update
    updated_data = update(table_data, set_clause, where_clause)
    
    if updated_data is not None:
        save_table_data(table_name, updated_data)
        print(f"Записи обновлены в таблице '{table_name}'.")
        # Очищаем кэш после обновления
        _select_cache.clear()  # type: ignore
    else:
        return metadata, True
    
    return metadata, True


def handle_delete(metadata: dict, parts: list[str]) -> tuple[dict, bool]:
    """Удаляет записи из таблицы по команде пользователя."""
    
    if len(parts) < 6:
        print("Нужно указать имя таблицы и условие where.")
        return metadata, True
    
    from_keyword = parts[1]
    if from_keyword != "from":
        print(
            "Неправильный синтаксис команды. "
            "Должно быть delete from <имя_таблицы> where <столбец> = <значение>"
        )
        return metadata, True
    
    table_name = parts[2]
    
    # Проверяем существование таблицы
    if table_name not in metadata:
        print(f"Таблица {table_name!r} не найдена")
        return metadata, True
    
    # Загружаем данные таблицы
    table_data = load_table_data(table_name)
    if isinstance(table_data, dict):
        table_data = list(table_data.values()) if table_data else []
    elif not isinstance(table_data, list):
        table_data = []
    
    # Парсим where условие используя парсер
    try:
        if len(parts) < 4 or parts[3].lower() != "where":
            print(
                "Неправильный синтаксис команды. "
                "Должно быть delete from <имя_таблицы> where <столбец> = <значение>"
            )
            return metadata, True
        
        where_clause = parse_where_clause(parts, 3, metadata, table_name)
        
        if where_clause is None:
            print(
                "Неправильный синтаксис where. "
                "Должно быть where <столбец> = <значение>"
            )
            return metadata, True
    except ValueError as error:
        print(error)
        return metadata, True
    
    # Выполняем delete
    updated_data = delete(table_data, where_clause)
    
    if updated_data is not None:
        save_table_data(table_name, updated_data)
        print(f"Записи удалены из таблицы '{table_name}'.")
        # Очищаем кэш после удаления
        _select_cache.clear()  # type: ignore
    else:
        return metadata, True
    
    return metadata, True