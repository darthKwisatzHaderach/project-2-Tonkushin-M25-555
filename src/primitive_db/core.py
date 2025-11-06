def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу в метаданных, добавляя обязательный столбец ID:int."""
    if table_name in metadata:
        raise ValueError(f"Таблица {table_name!r} уже существует")

    normalized = ["ID:int"]
    for column in columns:
        name, _, type_name = column.partition(":")
        if not type_name:
            raise ValueError(f"Колонка {column!r} без типа")
        if type_name not in {"int", "str", "bool"}:
            raise ValueError(f"Тип {type_name!r} не поддерживается")
        normalized.append(f"{name}:{type_name}")

    metadata = metadata.copy()
    metadata[table_name] = normalized
    return metadata

def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных, если она существует."""
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name!r} не найдена")

    updated = metadata.copy()
    updated.pop(table_name)
    return updated


def list_tables(metadata: dict) -> list[tuple[str, list[str]]]:
    """Возвращает список таблиц и их колонок из метаданных."""

    return [(name, columns.copy()) for name, columns in metadata.items()]