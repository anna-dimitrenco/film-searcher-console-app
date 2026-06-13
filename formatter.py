from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_welcome() -> None:
    """Prints the welcome header."""
    console.print(Panel(
        "[bold cyan]🎬  Film-Suchdienst[/bold cyan]",
        expand=False,
    ))


def print_menu() -> None:
    """Prints the main menu."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold yellow")
    table.add_column()
    table.add_row("[1]", "Suche nach Stichwort")
    table.add_row("[2]", "Suche nach Genre und Jahr")
    table.add_row("[3]", "Top-5 der beliebtesten Suchanfragen")
    table.add_row("[0]", "Beenden")
    console.print(Panel(table, title="[bold]Menü[/bold]", expand=False))


def r_print(message: str, style: str, prefix: str = "") -> None:
    console.print(f"[{style}]{prefix} {message}[/{style}]")


def format_film_table(films: list[tuple], offset: int = 0) -> None:
    """Displays a list of films as a table using rich.

    :param films: List of tuples (title, release_year, rating).
    :param offset: Numbering offset (for pagination).
    """
    if not films:
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("№", justify="right", style="dim", width=4)
    table.add_column("Titel")
    table.add_column("Jahr", justify="center", width=6)
    table.add_column("Bewertung", justify="center", width=8)

    for i, (title, year, rating) in enumerate(films, start=offset + 1):
        table.add_row(str(i), title, str(year), str(rating))

    console.print(table)


def format_category_table(categories: tuple) -> None:
    """Displays a list of genres as a table using rich.

    :param categories: Tuple of strings (id, name) from the database.
    """
    if not categories:
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("№", justify="right", style="dim", width=4)
    table.add_column("Genre")

    for cat_id, name in categories:
        table.add_row(str(cat_id), name)

    console.print(table)


def format_search_history_table(
    entries: list[dict],
    show_count: bool = False,
) -> None:
    """Displays the search history as a table using rich.

    :param entries: List of dictionaries with query data from MongoDB.
    :param show_count: If True — shows a column with the number of repetitions.
    """
    if not entries:
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Suchanfrage")
    name_of_column = "Zeitraum" if show_count else "Datum der letzten Suche"

    table.add_column(name_of_column, justify="center")
    if show_count:
        table.add_column("Anzahl der Anfragen", justify="right")

    for entry in entries:
        # Support for get_top_searches format (with _id) and get_recent_searches
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
        if show_count and "_id" in entry:
            first = entry.get("first_searched")
            last = entry.get("last_searched")
            if isinstance(first, datetime) and isinstance(last, datetime):
                days = (last.date() - first.date()).days + 1
                period_str = (
                    f"{first.strftime('%d.%m.%Y')} – {last.strftime('%d.%m.%Y')}"
                    f" ({days} Tg.)"
                )
            else:
                period_str = "—"
            table.add_row(desc, period_str, count)
        else:
            ts_str = ts.strftime("%d.%m.%Y %H:%M") if isinstance(
                ts, datetime) else "—"
            table.add_row(desc, ts_str)

    console.print(table)


def format_desc(search_type: str, params: dict) -> str:
    """Returns a description of the search query."""
    if search_type == "keyword":
        return f'Nach Stichwort: "{params.get("keyword", "")}"'
    return (
        f'Genre: {params.get("genre_name", "?")} '
        f'({params.get("year_from")}–{params.get("year_to")})'
    )
