#!/usr/bin/env python3
from primitive_db.constants import COMMANDS
from primitive_db.engine import run
from primitive_db.utils import show_help


def main() -> None:
    print("***Процесс работы с таблицей***")
    show_help(COMMANDS)
    run()


if __name__ == "__main__":
    main()

#insert into users values (1, 2, 3, 4)