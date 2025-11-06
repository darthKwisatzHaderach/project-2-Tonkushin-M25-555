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
  create_table <имя_таблицы> <столбец1:тип> [<столбецN:тип>] - создать таблицу
  list_tables - показать список всех таблиц
  drop_table <имя_таблицы> - удалить таблицу
  help - справочная информация
  exit - выйти из программы

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

[![asciicast](https://asciinema.org/a/1jMZLwEYY73JVr1o7CkDktiow.svg)](https://asciinema.org/a/1jMZLwEYY73JVr1o7CkDktiow)

*Для просмотра локальной записи: `asciinema play docs/demo.cast`.*
