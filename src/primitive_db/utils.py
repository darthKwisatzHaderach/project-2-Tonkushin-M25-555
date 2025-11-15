"""Вспомогательные функции для работы с CLI и метаданными."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback для старых версий
    except ImportError:
        tomllib = None



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
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        # Если не удалось сохранить, выводим ошибку для отладки
        raise RuntimeError(f"Не удалось сохранить метаданные в {path}: {e}") from e


def _load_config() -> dict[str, str]:
    """
    Загружает настройки из pyproject.toml.
    Возвращает словарь с путями или значения по умолчанию.
    """
    # Сначала проверяем переменную окружения для корня проекта
    project_root_env = os.getenv("PRIMITIVE_DB_PROJECT_ROOT")
    if project_root_env:
        project_root = Path(project_root_env).resolve()
    else:
        # Ищем pyproject.toml, начиная с текущей рабочей директории
        current = Path.cwd().resolve()
        project_root = None
        for _ in range(10):
            pyproject_toml = current / "pyproject.toml"
            if pyproject_toml.exists() and pyproject_toml.is_file():
                project_root = current
                break
            parent = current.parent
            if parent == current:
                break
            current = parent
    
    # Значения по умолчанию (соответствуют pyproject.toml)
    # Используются только если pyproject.toml недоступен
    # (например, при установке пакета через pip)
    DEFAULT_METADATA_PATH = "src/primitive_db/db_meta.json"
    DEFAULT_DATA_DIR = "data"
    
    if not project_root:
        # Fallback: pyproject.toml не найден
        # (запуск не из корня проекта или пакет установлен)
        return {
            "metadata_path": str(Path.cwd() / DEFAULT_METADATA_PATH),
            "data_dir": str(Path.cwd() / DEFAULT_DATA_DIR)
        }
    
    # Читаем настройки из pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    
    if not pyproject_path.exists() or tomllib is None:
        # Fallback: файл не существует или tomllib недоступен
        return {
            "metadata_path": str(project_root / DEFAULT_METADATA_PATH),
            "data_dir": str(project_root / DEFAULT_DATA_DIR)
        }
    
    try:
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)
        
        primitive_db_config = config.get("tool", {}).get("primitive_db", {})
        
        # Получаем пути из конфига или используем значения по умолчанию
        metadata_path = primitive_db_config.get(
            "metadata_path", DEFAULT_METADATA_PATH
        )
        data_dir = primitive_db_config.get("data_dir", DEFAULT_DATA_DIR)
        
        # Если пути относительные, делаем их относительно корня проекта
        if not Path(metadata_path).is_absolute():
            metadata_path = str(project_root / metadata_path)
        if not Path(data_dir).is_absolute():
            data_dir = str(project_root / data_dir)
        
        return {
            "metadata_path": metadata_path,
            "data_dir": data_dir
        }
    except Exception:
        # Fallback: ошибка при чтении/парсинге pyproject.toml
        return {
            "metadata_path": str(project_root / DEFAULT_METADATA_PATH),
            "data_dir": str(project_root / DEFAULT_DATA_DIR)
        }


def load_table_data(table_name: str) -> dict:
    """
    Загружает данные таблицы из JSON-файла в папке data.
    
    Возвращает пустой словарь, если файл не найден.
    """
    config = _load_config()
    data_dir = Path(config["data_dir"])
    filepath = data_dir / f"{table_name}.json"
    try:
        with filepath.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_table_data(table_name: str, data: Any) -> None:
    """Сохраняет данные таблицы в JSON-файл в папке data."""
    config = _load_config()
    data_dir = Path(config["data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / f"{table_name}.json"
    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
