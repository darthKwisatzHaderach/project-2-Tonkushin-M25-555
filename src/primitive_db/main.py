#!/usr/bin/env python3
from primitive_db.constants import COMMANDS
from primitive_db.engine import welcome
from primitive_db.utils import show_help


def main() -> None:
    print("Первая попытка запустить проект!\n")
    print("***")
    show_help(COMMANDS)
    command = welcome()
    match command:
        case 'help':
            show_help(COMMANDS)
        case _:
            print("Неизвестная команда. Введите 'help' для помощи.")

if __name__ == "__main__":
    main()