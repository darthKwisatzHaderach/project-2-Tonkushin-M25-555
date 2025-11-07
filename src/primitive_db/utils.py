"""Вспомогательные функции для работы с CLI и метаданными."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def show_help(commands: dict) -> None:
    """Печатает доступные команды с описаниями, выровненными по колонке."""
    print("\nФункции:")
    for cmd, desc in commands.items():
        print(f"  {cmd:<16} - {desc}")


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из JSON-файла или возвращает пустой словарь."""
    try:
        with Path(filepath).open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: Any) -> None:
    """Сохраняет метаданные в JSON-файл."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_table_data(table_name: str) -> dict:
    """Загружает данные таблицы из JSON-файла в папке data или возвращает пустой словарь."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    filepath = data_dir / f"{table_name}.json"
    try:
        with filepath.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_table_data(table_name: str, data: Any) -> None:
    """Сохраняет данные таблицы в JSON-файл в папке data."""
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / f"{table_name}.json"
    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
