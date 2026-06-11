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
        """Точка входа: приветствие и запуск главного меню."""
        print_welcome()
        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())

    @staticmethod
    def show_options_messages() -> None:
        """Выводит список доступных опций главного меню."""
        print_menu()

    @staticmethod
    def get_start_answer() -> str:
        """Считывает и возвращает выбор пользователя."""
        return input("Введите номер нужной опции: ").strip()

    def handle_user_input(self, user_input: str) -> None:
        """Маршрутизирует ввод пользователя на нужный обработчик."""
        if user_input == "0":
            r_print("Выход из программы. До свидания!", "bold green", "✔")
            exit()
        elif user_input == "1":
            self.search_by_keyword()
        elif user_input == "2":
            self.filter_by_genre_and_year()
        elif user_input == "3":
            self.show_top_5_queries()
        else:
            r_print("Некорректный ввод. Введите номер из меню.", "bold red", "✘")
            self.show_options_messages()
            self.handle_user_input(self.get_start_answer())


    @staticmethod
    def paginate(titles: list[tuple], count: int) -> None:
        """Выводит результаты постранично по PAGE_SIZE штук."""
        page = 0
        while True:
            batch = titles[page *
                           Library.PAGE_SIZE:(page + 1) * Library.PAGE_SIZE]
            format_film_table(batch, offset=page * Library.PAGE_SIZE)

            # Если вся выборка выведена — выходим из цикла
            if (page + 1) * Library.PAGE_SIZE >= count:
                r_print("Больше результатов нет.", "bold cyan", "ℹ")
                break

            choice = input(
                f"Введите 1 чтобы показать следующие {Library.PAGE_SIZE}, или 0 чтобы вернуться в меню: "
            ).strip()
            if choice == "1":
                page += 1
            else:
                break

    def search_by_keyword(self) -> None:
        """Поиск фильмов по ключевому слову в названии."""
        while True:
            keyword = input("Введите ключевое слово для поиска фильма: ").strip()
            if len(keyword) >= 3:
                break
            r_print("Ключевое слово должно содержать минимум 3 символа.", "bold red", "✘")
        count, titles = self.db.search_by_title(keyword)
        self.logger.log_search("keyword", {"keyword": keyword}, count)
        self.show_results(count, titles)

    def filter_by_genre_and_year(self) -> None:
        """Фильтрация фильмов по жанру и диапазону годов выпуска."""
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
        """Выводит таблицу доступных жанров и возвращает их список."""
        categories = self.db.get_categories()
        r_print("Доступные жанры", "bold cyan", "ℹ")
        format_category_table(categories)
        return categories

    def show_year_range(self) -> tuple[int, int]:
        """Выводит доступный диапазон годов и возвращает (year_min, year_max)."""
        year_min, year_max = self.db.get_year_range()
        r_print(f"Годы выпуска фильмов в базе: {year_min} – {year_max}", "bold cyan", "ℹ")
        return year_min, year_max

    def show_results(self, count: int, titles: list[tuple]) -> None:
        """Выводит результаты поиска и возвращает в главное меню."""
        if count == 0:
            r_print("Фильмы не найдены.", "bold red", "✘")
        else:
            r_print(f"Найдено фильмов: {count}", "bold green", "✔")
            self.paginate(titles, count)
        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())

    def ask_genre(self, categories: tuple) -> tuple[int, str] | None:
        """Запрашивает номер жанра с валидацией.

        :return: (genre_id, genre_name) или None если пользователь вышел в меню.
        """
        valid_ids = {str(c[0]): c[1] for c in categories}
        while True:
            genre_input = input(
                "Введите номер жанра или 0 для выхода в меню: "
            ).strip()
            
            if genre_input == "0":
                self.show_options_messages()
                self.handle_user_input(self.get_start_answer())
                return None
            
            if genre_input in valid_ids:
                return int(genre_input), valid_ids[genre_input]
            r_print("Некорректный ввод. Введите номер из списка или 0 для выхода в меню.", "bold red", "✘")

    @staticmethod
    def ask_year_range(year_min: int, year_max: int) -> tuple[int, int] | None:
        """Запрашивает диапазон лет с валидацией.

        Поддерживается формат "2005" или "2005-2012".
        :return: (year_from, year_to) или None если пользователь вышел в меню.
        """
        while True:
            year_input = input(
                f"Введите год или диапазон через тире({year_min}-{year_max})"
                f" (или 0 для выхода в меню): "
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
                
            r_print(f"Некорректный ввод. Введите год в диапазоне {year_min}–{year_max} или 0 для выхода в меню.", "bold red", "✘")

    def show_top_5_queries(self) -> None:
        """Выводит топ-5 запросов по частоте или по времени последних поисков."""
        r_print("Топ-5 запросов", "bold cyan")
        r_print("1. По частоте (самые популярные)", "bold cyan")
        r_print("2. По последним поискам", "bold cyan")
        r_print("0. Вернуться в меню", "bold cyan")

        choice = input("Введите номер опции: ").strip()

        if choice == "0":
            self.show_options_messages()
            self.handle_user_input(self.get_start_answer())
            return
        elif choice == "1":
            # Агрегация из MongoDB: группировка по запросу, сортировка по количеству
            results = self.logger.get_top_searches(5)
            if not results:
                r_print("История поиска пуста.", "bold cyan", "ℹ")
            else:
                r_print("Топ-5 популярных запросов", "bold cyan", "ℹ")
                format_search_history_table(results, show_count=True)
        elif choice == "2":
            # Последние 5 документов из MongoDB, отсортированные по timestamp
            results = self.logger.get_recent_searches(5)
            if not results:
                r_print("История поиска пуста.", "bold cyan", "ℹ")
            else:
                r_print("Последние 5 поисков", "bold cyan", "ℹ")
                format_search_history_table(results, show_count=False)
        else:
            r_print("Некорректный ввод.", "bold red", "✘")

        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())
