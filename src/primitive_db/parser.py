"""Функции для разбора сложных команд (where, set)."""

from primitive_db.core import type_casting


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

