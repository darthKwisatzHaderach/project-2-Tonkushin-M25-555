# Primitive DB

## Управление таблицами

### Доступные команды

- `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` — создать таблицу. Автоматически добавляется столбец `ID:int` в начало списка столбцов. Поддерживаемые типы: `int`, `str`, `bool`.
- `list_tables` — показать список всех таблиц и их структуру.
- `drop_table <имя_таблицы>` — удалить таблицу.
- `help` — вывести справочную информацию.
- `exit` или `quit` — выйти из программы.

### Пример использования

```bash
$ database
***Процесс работы с таблицей***

Функции:
  database create_table <имя_таблицы> <столбец1:тип> [<столбецN:тип>] - создать таблицу
  database list_tables       - показать список всех таблиц
  database drop_table <имя_таблицы> - удалить таблицу
  database help             - справочная информация
  database exit             - выйти из программы (также работает quit)
Введите команду:  create_table users name:str email:str active:bool
Таблица 'users' создана.
Введите команду:  list_tables
Список таблиц:
  - users: ID:int, name:str, email:str, active:bool
Введите команду:  drop_table users
Таблица 'users' удалена.
Введите команду:  exit
```

### Демонстрация работы

[![asciicast](https://asciinema.org/a/6wrosLYPgu27MthzH1Hi7IafY.svg)](https://asciinema.org/a/6wrosLYPgu27MthzH1Hi7IafY)

*Для просмотра локальной записи: `asciinema play docs/demo.cast`.*

