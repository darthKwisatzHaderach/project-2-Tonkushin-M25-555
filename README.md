# Primitive DB

## Управление таблицами

### Доступные команды

- `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` — создать таблицу. Автоматически добавляется столбец `ID:int` в начало списка столбцов. Поддерживаемые типы: `int`, `str`, `bool`.
- `list_tables` — показать список всех таблиц и их структуру.
- `drop_table <имя_таблицы>` — удалить таблицу.
- `help` — вывести справочную информацию.
- `exit` или `quit` — выйти из программы.

## CRUD-операции

### INSERT - Добавление записей

- `insert into <имя_таблицы> values (<значение1>, <значение2>, ...)` — добавить новую запись в таблицу. ID генерируется автоматически.

**Пример:**
```bash
insert into users values ("Иван", "ivan@mail.ru", 30, true)
```

### SELECT - Чтение записей

- `select from <имя_таблицы>` — получить все записи из таблицы.
- `select from <имя_таблицы> where <столбец> = <значение>` — получить записи, соответствующие условию.

**Примеры:**
```bash
select from users
select from users where age = 30
select from users where name = "Иван"
```

Результаты выводятся в виде красивой таблицы с использованием `prettytable`.

### UPDATE - Обновление записей

- `update <имя_таблицы> set <столбец> = <новое_значение> where <столбец_условия> = <значение_условия>` — обновить записи, соответствующие условию.

**Пример:**
```bash
update users set active = false where name = "Иван"
update users set age = 31 where email = "ivan@mail.ru"
```

### DELETE - Удаление записей

- `delete from <имя_таблицы> where <столбец> = <значение>` — удалить записи, соответствующие условию.

**Пример:**
```bash
delete from users where age = 30
delete from users where name = "Иван"
```

**Важно:** Строковые значения в командах должны быть заключены в кавычки (одинарные или двойные).

### Пример использования

```bash
$ database
***Процесс работы с таблицей***

Функции:
  create_table <имя_таблицы> <столбец1:тип> [<столбецN:тип>] - создать таблицу
  list_tables - показать список всех таблиц
  drop_table <имя_таблицы> - удалить таблицу
  insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись
  select from <имя_таблицы> [where <столбец> = <значение>] - прочитать записи
  update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение> - обновить запись
  delete from <имя_таблицы> where <столбец> = <значение> - удалить запись
  help - справочная информация
  exit - выйти из программы

Введите команду:  create_table users name:str email:str age:int active:bool
Таблица 'users' создана.
Введите команду:  insert into users values ("Иван", "ivan@mail.ru", 30, true)
Запись добавлена в таблицу 'users'.
Введите команду:  insert into users values ("Мария", "maria@mail.ru", 25, true)
Запись добавлена в таблицу 'users'.
Введите команду:  select from users
+----+-------+---------------+-----+--------+
| ID | name  |     email     | age | active |
+----+-------+---------------+-----+--------+
|  1 | Иван  | ivan@mail.ru  |  30 |  True  |
|  2 | Мария | maria@mail.ru |  25 |  True  |
+----+-------+---------------+-----+--------+
Введите команду:  select from users where age = 30
+----+------+--------------+-----+--------+
| ID | name |     email    | age | active |
+----+------+--------------+-----+--------+
|  1 | Иван | ivan@mail.ru |  30 |  True  |
+----+------+--------------+-----+--------+
Введите команду:  update users set active = false where name = "Иван"
Записи обновлены в таблице 'users'.
Введите команду:  delete from users where age = 25
Записи удалены из таблицы 'users'.
Введите команду:  exit
```

### Демонстрация работы

[![asciicast](https://asciinema.org/a/1jMZLwEYY73JVr1o7CkDktiow.svg)](https://asciinema.org/a/1jMZLwEYY73JVr1o7CkDktiow)

*Для просмотра локальной записи: `asciinema play docs/demo.cast`.*
