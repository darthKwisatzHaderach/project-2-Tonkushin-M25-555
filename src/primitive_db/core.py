def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу в метаданных, добавляя обязательный столбец ID:int."""
    if table_name in metadata:
        raise ValueError(f"Таблица {table_name!r} уже существует")

    normalized = []
    has_id = False
    id_column = None

    for column in columns:
        name, _, type_name = column.partition(":")
        if not type_name:
            raise ValueError(f"Колонка {column!r} без типа")
        if type_name not in {"int", "str", "bool"}:
            raise ValueError(f"Тип {type_name!r} не поддерживается")
        if name.upper() == "ID":
            has_id = True
            id_column = f"{name}:{type_name}"
        else:
            normalized.append(f"{name}:{type_name}")

    if has_id:
        normalized.insert(0, id_column)
    else:
        normalized.insert(0, "ID:int")

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


def insert(metadata: dict, table_name: str, values: list) -> dict:
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name!r} не найдена")

    columns_list = metadata[table_name]
    columns = {}
    for column in columns_list:
        column_split = str(column).split(':')
        column_name = column_split[0]
        column_type = column_split[1]
        columns[column_name] = column_type

    if len(columns_list) != len(values):
        raise ValueError(f"Кол-во значений {len(values)} не соответствует кол-ву столбцов {len(columns_list)}.\n"
                         f"Столбцы таблицы {columns_list}")

    record = {}
    for (column_name, column_type), value in zip(columns.items(), values):
        print(f"{column_name}:{column_type} {value}")
        record[column_name] = type_casting(column_type, value)

    return record

def type_casting(column_type: str, value: str) -> None | str | int | bool:
    match column_type:
        case "str":
            try:
                return str(value)
            except:
                raise ValueError(f"Значение {value} должно быть строкой")
        case "int":
            try:
                return int(value)
            except:
                raise ValueError(f"Значение {value} должно быть числом")
        case "bool":
            try:
                if value.strip().lower() == "true":
                    return True
                if value.strip().lower() == "false":
                    return False
            except:
                raise ValueError(f"Значение {value} должно быть true или false")
        case _:
            raise ValueError(f"Неподдерживаемый тип {column_type}")