from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def print_welcome() -> None:
    """Выводит приветственный заголовок."""
    console.print(Panel(
        "[bold cyan]🎬  Сервис по поиску фильмов[/bold cyan]",
        expand=False,
    ))


def print_menu() -> None:
    """Выводит главное меню."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold yellow")
    table.add_column()
    table.add_row("[1]", "Поиск по ключевому слову")
    table.add_row("[2]", "Поиск по жанру и году")
    table.add_row("[3]", "Топ-5 популярных запросов")
    table.add_row("[0]", "Выход")
    console.print(Panel(table, title="[bold]Меню[/bold]", expand=False))


def print_success(message: str) -> None:
    """Выводит сообщение об успехе зелёным цветом."""
    console.print(f"[bold green]✔ {message}[/bold green]")


def print_error(message: str) -> None:
    """Выводит сообщение об ошибке красным цветом."""
    console.print(f"[bold red]✘ {message}[/bold red]")


def print_info(message: str) -> None:
    """Выводит информационное сообщение."""
    console.print(f"[bold cyan]{message}[/bold cyan]")


def print_section(title: str) -> None:
    """Выводит заголовок секции."""
    console.rule(f"[bold cyan]{title}[/bold cyan]")


def format_film_table(films: list[tuple], offset: int = 0) -> None:
    """Выводит список фильмов в виде таблицы через rich.

    :param films: Список кортежей (title, release_year, rating).
    :param offset: Смещение нумерации (для пагинации).
    """
    if not films:
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("№", justify="right", style="dim", width=4)
    table.add_column("Название")
    table.add_column("Год", justify="center", width=6)
    table.add_column("Рейтинг", justify="center", width=8)

    for i, (title, year, rating) in enumerate(films, start=offset + 1):
        table.add_row(str(i), title, str(year), str(rating))

    console.print(table)


def format_category_table(categories: tuple) -> None:
    """Выводит список жанров в виде таблицы через rich.

    :param categories: Кортеж строк (id, name) из БД.
    """
    if not categories:
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("№", justify="right", style="dim", width=4)
    table.add_column("Жанр")

    for cat_id, name in categories:
        table.add_row(str(cat_id), name)

    console.print(table)


def format_search_history_table(
    entries: list[dict],
    show_count: bool = False,
) -> None:
    """Выводит историю поисковых запросов в виде таблицы через rich.

    :param entries: Список словарей с данными запросов из MongoDB.
    :param show_count: Если True — показывает столбец с количеством повторений.
    """
    if not entries:
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Запрос")
    table.add_column("Дата/время")
    if show_count:
        table.add_column("Кол-во", justify="right")

    for entry in entries:
        # Поддержка формата get_top_searches (с _id) и get_recent_searches
        if "_id" in entry:
            search_type = entry["_id"]["search_type"]
            params = entry["_id"]["params"]
            count = str(entry.get("count", ""))
            ts = entry.get("last_searched")
        else:
            search_type = entry.get("search_type", "")
            params = entry.get("params", {})
            count = ""
            ts = entry.get("timestamp")

        desc = format_desc(search_type, params)
        ts_str = ts.strftime("%d.%m.%Y %H:%M") if isinstance(
            ts, datetime) else "—"

        if show_count:
            table.add_row(desc, ts_str, count)
        else:
            table.add_row(desc, ts_str)

    console.print(table)


def format_desc(search_type: str, params: dict) -> str:
    """Возвращает описание поискового запроса."""
    if search_type == "keyword":
        return f'По слову: "{params.get("keyword", "")}"'
    return (
        f'Жанр: {params.get("genre_name", "?")} '
        f'({params.get("year_from")}–{params.get("year_to")})'
    )
