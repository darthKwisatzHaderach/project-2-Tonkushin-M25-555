import prompt

def welcome() -> str:
    command = prompt.string('Введите команду: ')
    return command