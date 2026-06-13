from formatter import (
    format_category_table,
    format_film_table,
    format_search_history_table,
    print_menu,
    r_print,
    print_welcome,
)
from mongo_connector import MongoDB
from mysql_connector import DB


class Library:
    PAGE_SIZE: int = 10  

    def __init__(self, db: DB, logger: MongoDB) -> None:
        self.db = db
        self.logger = logger

    def start_project(self) -> None:
        """Entry point: welcome screen and main menu launch."""
        print_welcome()
        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())

    @staticmethod
    def show_options_messages() -> None:
        """Displays the list of available main menu options."""
        print_menu()

    @staticmethod
    def get_start_answer() -> str:
        """Reads and returns the user's menu choice."""
        return input("Geben Sie die Nummer der gewünschten Option ein: ").strip()

    def handle_user_input(self, user_input: str) -> None:
        """Routes user input to the appropriate handler."""
        if user_input == "0":
            r_print("Programm wird beendet. Auf Wiedersehen!", "bold green", "✔")
            exit()
        elif user_input == "1":
            self.search_by_keyword()
        elif user_input == "2":
            self.filter_by_genre_and_year()
        elif user_input == "3":
            self.show_top_5_queries()
        else:
            r_print("Ungültige Eingabe. Geben Sie eine Nummer aus dem Menü ein.", "bold red", "✘")
            self.show_options_messages()
            self.handle_user_input(self.get_start_answer())


    @staticmethod
    def paginate(titles: list[tuple], count: int) -> None:
        """Displays results page by page in chunks of PAGE_SIZE."""
        page = 0
        while True:
            batch = titles[page *
                           Library.PAGE_SIZE:(page + 1) * Library.PAGE_SIZE]
            format_film_table(batch, offset=page * Library.PAGE_SIZE)

            # If all results have been displayed — exit the loop
            if (page + 1) * Library.PAGE_SIZE >= count:
                r_print("Keine weiteren Ergebnisse.", "bold cyan", "ℹ")
                break

            choice = input(
                f"Geben Sie 1 ein, um die nächsten {Library.PAGE_SIZE} anzuzeigen, oder 0 um ins Menü zurückzukehren: "
            ).strip()
            if choice == "1":
                page += 1
            else:
                break

    def search_by_keyword(self) -> None:
        """Searches for films by keyword in the title."""
        while True:
            keyword = input("Geben Sie ein Stichwort zur Filmsuche ein: ").strip()
            if len(keyword) >= 3:
                break
            r_print("Das Stichwort muss mindestens 3 Zeichen enthalten.", "bold red", "✘")
        count, titles = self.db.search_by_title(keyword)
        self.logger.log_search("keyword", {"keyword": keyword}, count)
        self.show_results(count, titles)

    def filter_by_genre_and_year(self) -> None:
        """Filters films by genre and release year range."""
        categories = self.show_categories()
        year_min, year_max = self.show_year_range()
        genre_result = self.ask_genre(categories)

        if genre_result is None:
            return
        
        genre_id, genre_name = genre_result
        year_result = self.ask_year_range(year_min, year_max)

        if year_result is None:
            return
        
        year_from, year_to = year_result
        count, titles = self.db.filter_by_genre_and_year(
            genre_id, year_from, year_to)
        
        self.logger.log_search(
            "genre_year",
            {"genre_id": genre_id, "genre_name": genre_name,
             "year_from": year_from, "year_to": year_to},
            count,
        )
        
        self.show_results(count, titles)

    def show_categories(self) -> tuple:
        """Displays the table of available genres and returns their list."""
        categories = self.db.get_categories()
        r_print("Verfügbare Genres", "bold cyan", "ℹ")
        format_category_table(categories)
        return categories

    def show_year_range(self) -> tuple[int, int]:
        """Displays the available year range and returns (year_min, year_max)."""
        year_min, year_max = self.db.get_year_range()
        r_print(f"Erscheinungsjahre in der Datenbank: {year_min} – {year_max}", "bold cyan", "ℹ")
        return year_min, year_max

    def show_results(self, count: int, titles: list[tuple]) -> None:
        """Displays search results and returns to the main menu."""
        if count == 0:
            r_print("Keine Filme gefunden.", "bold red", "✘")
        else:
            r_print(f"Gefundene Filme: {count}", "bold green", "✔")
            self.paginate(titles, count)
        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())

    def ask_genre(self, categories: tuple) -> tuple[int, str] | None:
        """Prompts for a genre number with validation.

        :return: (genre_id, genre_name) or None if the user returned to the menu.
        """
        valid_ids = {str(c[0]): c[1] for c in categories}
        while True:
            genre_input = input(
                "Geben Sie die Genre-Nummer ein oder 0 um ins Menü zurückzukehren: "
            ).strip()
            
            if genre_input == "0":
                self.show_options_messages()
                self.handle_user_input(self.get_start_answer())
                return None
            
            if genre_input in valid_ids:
                return int(genre_input), valid_ids[genre_input]
            r_print("Ungültige Eingabe. Geben Sie eine Nummer aus der Liste ein oder 0 um zurückzukehren.", "bold red", "✘")

    @staticmethod
    def ask_year_range(year_min: int, year_max: int) -> tuple[int, int] | None:
        """Prompts for a year range with validation.

        Supported format: "2005" or "2005-2012".
        :return: (year_from, year_to) or None if the user returned to the menu.
        """
        while True:
            year_input = input(
                f"Geben Sie ein Jahr oder einen Bereich mit Bindestrich ein ({year_min}-{year_max})"
                f" (oder 0 um ins Menü zurückzukehren): "
            ).strip()
            
            if year_input == "0":
                return None
            
            parts = year_input.split("-")
            
            if len(parts) == 2:
                a, b = parts[0].strip(), parts[1].strip()
                if (
                    a.isdigit() and b.isdigit()
                    and year_min <= int(a) <= year_max
                    and year_min <= int(b) <= year_max
                    and int(a) <= int(b)
                ):
                    return int(a), int(b)
            elif len(parts) == 1 and parts[0].isdigit():
                y = int(parts[0])
                if year_min <= y <= year_max:
                    return y, y
                
            r_print(f"Ungültige Eingabe. Geben Sie ein Jahr im Bereich {year_min}–{year_max} ein oder 0 um zurückzukehren.", "bold red", "✘")

    def show_top_5_queries(self) -> None:
        """Displays the top-5 queries by frequency or by most recent search time."""
        r_print("Top-5-Suchanfragen", "bold cyan")
        r_print("1. Nach Häufigkeit (beliebteste)", "bold cyan")
        r_print("2. Nach letzten Suchen", "bold cyan")
        r_print("0. Zurück zum Menü", "bold cyan")

        choice = input("Geben Sie die Nummer der Option ein: ").strip()

        if choice == "0":
            self.show_options_messages()
            self.handle_user_input(self.get_start_answer())
            return
        elif choice == "1":
            # MongoDB aggregation: group by query, sort by count
            results = self.logger.get_top_searches(5)
            if not results:
                r_print("Suchverlauf ist leer.", "bold cyan", "ℹ")
            else:
                r_print("Top-5 der beliebtesten Suchanfragen", "bold cyan", "ℹ")
                format_search_history_table(results, show_count=True)
        elif choice == "2":
            # Last 5 documents from MongoDB, sorted by timestamp
            results = self.logger.get_recent_searches(5)
            if not results:
                r_print("Suchverlauf ist leer.", "bold cyan", "ℹ")
            else:
                r_print("Die letzten 5 Suchen", "bold cyan", "ℹ")
                format_search_history_table(results, show_count=False)
        else:
            r_print("Ungültige Eingabe.", "bold red", "✘")

        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())
