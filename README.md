# VFS — Этап 1: REPL

## Описание

На первом этапе реализован минимальный прототип консольного интерфейса
(REPL — Read-Eval-Print Loop), позволяющий пользователю вводить команды
и получать результаты их выполнения. Команды работы с файловой системой являются заглушками.
Они не выполняют реальных операций, а только выводят имя команды и переданные
ей аргументы.

## Команды

### `ls`

Выводит название команды и переданные аргументы.

```text
my_vfs$ ls
ls

my_vfs$ ls -l /home
ls -l /home
```

### `cd`

Выводит название команды и переданные аргументы.

```text
my_vfs$ cd /home
cd /home
```

### `exit`

Завершает работу программы.

```text
my_vfs$ exit
Exiting program
```

Если передать аргументы:

```text
my_vfs$ exit test
ERROR: 'exit' command does not take any arguments!
```

### Неизвестная команда

```text
my_vfs$ mkdir test
ERROR: Unknown command 'mkdir'
```

## Запуск

```bash
python3 cmd_emu.py
```

или:

```bash
python cmd_emu.py
```

## Структура проекта

```text
.
├── src/
│   └── main.py
├── tests/
├── .gitignore
├── Makefile
└── README.md
```
