#!/usr/bin/env python3
"""Точка входа в приложение Primitive DB."""

from primitive_db.constants import COMMANDS
from primitive_db.engine import run
from primitive_db.utils import show_help


def main() -> None:
    """Запускает интерактивную сессию работы с базой данных."""
    print("***Процесс работы с таблицей***")
    show_help(COMMANDS)
    run()


if __name__ == "__main__":
    main()