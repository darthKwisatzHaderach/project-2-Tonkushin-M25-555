"""Исполнение пользовательских команд и работа с метаданными."""

from __future__ import annotations

import shlex
from pathlib import Path

from primitive_db.constants import COMMANDS
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import show_help, load_metadata, save_metadata


METADATA_PATH = Path(__file__).with_name("db_meta.json")


def get_input(prompt: str = "Введите команду:  ") -> str:
    """Безопасное чтение ввода. На Ctrl+C/EOF возвращает 'quit'."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nВыход из игры.")
        return "quit"

def run() -> None:
    while True:
        metadata = load_metadata(str(METADATA_PATH))
        command_line = get_input()
        metadata, should_continue = process_command(metadata, command_line)

        if not should_continue:
            break


def process_command(metadata: dict, command_line: str) -> tuple[dict, bool]:
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
        return handle_create_table(metadata, parts)

    if cmd == "list_tables":
        handle_list_tables(metadata)
        return metadata, True

    if cmd == "drop_table":
        return handle_drop_table(metadata, parts)

    if cmd in {"help", "?"}:
        show_help(COMMANDS)
        return metadata, True

    if cmd in {"exit", "quit"}:
        return metadata, False

    print("Неизвестная команда. Введите 'help' для помощи.")
    return metadata, True


def handle_create_table(metadata: dict, parts: list[str]) -> tuple[dict, bool]:
    """Создаёт таблицу по команде пользователя."""

    if len(parts) < 3:
        print("Нужно указать имя таблицы и хотя бы один столбец вида <имя:тип>.")
        return metadata, True

    table_name = parts[1]
    columns = parts[2:]

    try:
        updated = create_table(metadata, table_name, columns)
    except ValueError as error:
        print(error)
        return metadata, True

    save_metadata(str(METADATA_PATH), updated)
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


def handle_drop_table(metadata: dict, parts: list[str]) -> tuple[dict, bool]:
    """Удаляет таблицу из метаданных по команде пользователя."""

    if len(parts) < 2:
        print("Нужно указать имя таблицы для удаления.")
        return metadata, True

    table_name = parts[1]

    try:
        updated = drop_table(metadata, table_name)
    except ValueError as error:
        print(error)
        return metadata, True

    save_metadata(str(METADATA_PATH), updated)
    print(f"Таблица '{table_name}' удалена.")
    return updated, True