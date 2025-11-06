def show_help(commands: dict) -> None:
    """Печатает доступные команды с описаниями, выровненными по колонке."""
    for cmd, desc in commands.items():
        print(f"  {cmd:<16} - {desc}")
