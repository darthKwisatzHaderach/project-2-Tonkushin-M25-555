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


def insert(metadata: dict, table_name: str, values: list, table_data: list | None = None) -> list:
    """
    Добавляет новую запись в таблицу.
    
    Проверяет существование таблицы, валидирует типы данных,
    генерирует новый ID и добавляет запись в данные таблицы.
    Возвращает измененные данные таблицы.
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name!r} не найдена")

    columns_list = metadata[table_name]
    columns = {}
    for column in columns_list:
        column_split = str(column).split(':')
        column_name = column_split[0]
        column_type = column_split[1]
        columns[column_name] = column_type

    # Проверяем количество значений (минус ID, так как ID генерируется автоматически)
    # values не должны включать ID - все поля обязательны
    expected_count = len(columns_list) - 1  # минус ID
    if len(values) != expected_count:
        # Получаем названия столбцов без ID для сообщения об ошибке
        column_names = [col.split(':')[0] for col in columns_list[1:]]  # Пропускаем ID
        raise ValueError(f"Кол-во значений {len(values)} не соответствует кол-ву столбцов (минус ID) {expected_count}.\n"
                         f"Ожидаемые столбцы (без ID): {', '.join(column_names)}\n"
                         f"Все поля обязательны.")

    # Проверяем, что все значения не пустые (все поля обязательны)
    for i, value in enumerate(values):
        if value is None or (isinstance(value, str) and value.strip() == ''):
            column_names = [col.split(':')[0] for col in columns_list[1:]]
            column_name = column_names[i] if i < len(column_names) else f"столбец {i+1}"
            raise ValueError(f"Поле '{column_name}' не может быть пустым. Все поля обязательны.")

    # Генерируем новый ID на основе последней записи
    if table_data is None or len(table_data) == 0:
        new_id = 1
    else:
        # Находим максимальный ID среди всех записей
        ids = [record.get('ID', 0) for record in table_data if isinstance(record, dict) and 'ID' in record]
        new_id = max(ids) + 1 if ids else 1

    # Создаем запись с валидацией типов
    # ID генерируется автоматически и не включается в values
    record = {'ID': new_id}
    # Пропускаем ID при валидации (он первый в columns_list)
    for (column_name, column_type), value in zip(list(columns.items())[1:], values):
        record[column_name] = type_casting(column_type, value)

    # Добавляем запись в данные таблицы
    if table_data is None:
        table_data = []
    table_data.append(record)

    return table_data

def select(table_data: list, where_clause: dict | None = None) -> list:
    """
    Возвращает записи из таблицы.
    
    Если where_clause не задан, возвращает все данные.
    Если задан (например, {'age': 28}), фильтрует и возвращает только подходящие записи.
    """
    if where_clause is None:
        return table_data.copy() if table_data else []
    
    # Фильтруем записи по условию
    result = []
    for record in table_data:
        if not isinstance(record, dict):
            continue
        # Проверяем, что все условия where_clause выполняются
        matches = all(record.get(key) == value for key, value in where_clause.items())
        if matches:
            result.append(record)
    
    return result


def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """
    Обновляет записи в таблице.
    
    Находит записи по where_clause, обновляет в них поля согласно set_clause.
    Возвращает измененные данные.
    """
    if not table_data:
        return []
    
    updated_data = []
    for record in table_data:
        if not isinstance(record, dict):
            updated_data.append(record)
            continue
        
        # Проверяем, соответствует ли запись условию where_clause
        matches = all(record.get(key) == value for key, value in where_clause.items())
        
        if matches:
            # Создаем обновленную копию записи
            updated_record = record.copy()
            # Применяем изменения из set_clause
            updated_record.update(set_clause)
            updated_data.append(updated_record)
        else:
            updated_data.append(record)
    
    return updated_data


def delete(table_data: list, where_clause: dict) -> list:
    """
    Удаляет записи из таблицы.
    
    Находит записи по where_clause и удаляет их.
    Возвращает измененные данные.
    """
    if not table_data:
        return []
    
    result = []
    for record in table_data:
        if not isinstance(record, dict):
            result.append(record)
            continue
        
        # Проверяем, соответствует ли запись условию where_clause
        matches = all(record.get(key) == value for key, value in where_clause.items())
        
        # Добавляем только те записи, которые НЕ соответствуют условию (т.е. не удаляем их)
        if not matches:
            result.append(record)
    
    return result


def type_casting(column_type: str, value: str) -> None | str | int | bool:
    match column_type:
        case "str":
            try:
                return str(value)
            except:
                raise ValueError(f"Значение {value} должно быть строкой")
        case "int":
            try:
                # Удаляем пробелы и невидимые символы перед преобразованием
                cleaned_value = str(value).strip()
                return int(cleaned_value)
            except (ValueError, TypeError):
                raise ValueError(f"Значение {value!r} должно быть числом")
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