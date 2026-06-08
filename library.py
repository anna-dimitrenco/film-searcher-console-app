from formatter import (
    format_category_table,
    format_film_table,
    format_search_history_table,
    print_error,
    print_info,
    print_menu,
    print_section,
    print_success,
    print_welcome,
)
from mongo_connector import MongoDB
from mysql_connector import DB


class Library:
    PAGE_SIZE: int = 10  # Количество результатов на одну страницу

    def __init__(self, db: DB, logger: MongoDB) -> None:
        self.db = db
        self.logger = logger

    # --- Главное меню ---

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
            print_success("Выход из программы. До свидания!")
            exit()
        elif user_input == "1":
            self.search_by_keyword()
        elif user_input == "2":
            self.search_by_genre_and_year()
        elif user_input == "3":
            self.show_top_5_queries()
        else:
            print_error("Некорректный ввод. Введите номер из меню.")
            self.show_options_messages()
            self.handle_user_input(self.get_start_answer())

    # --- Вспомогательный метод пагинации ---

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
                print_info("Больше результатов нет.")
                break

            choice = input(
                f"Введите 1 чтобы показать следующие {Library.PAGE_SIZE}, или 0 чтобы вернуться в меню: "
            ).strip()
            if choice == "1":
                page += 1
            else:
                break

    # --- Поиск по ключевому слову ---

    def search_by_keyword(self) -> None:
        """Поиск фильмов по ключевому слову в названии."""
        keyword = input("Введите ключевое слово для поиска фильма: ").strip()
        count, titles = self.db.search_by_title(keyword)
        self.logger.log_search("keyword", {"keyword": keyword}, count)
        self.show_results(count, titles)

    # --- Поиск по жанру и диапазону годов ---

    def search_by_genre_and_year(self) -> None:
        """Поиск фильмов по жанру и диапазону годов выпуска."""
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

        count, titles = self.db.search_by_genre_and_year(
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
        print_section("Доступные жанры")
        format_category_table(categories)
        return categories

    def show_year_range(self) -> tuple[int, int]:
        """Выводит доступный диапазон годов и возвращает (year_min, year_max)."""
        year_min, year_max = self.db.get_year_range()
        print_info(f"Годы выпуска фильмов в базе: {year_min} – {year_max}")
        return year_min, year_max

    def show_results(self, count: int, titles: list[tuple]) -> None:
        """Выводит результаты поиска и возвращает в главное меню."""
        if count == 0:
            print_error("Фильмы не найдены.")
        else:
            print_success(f"Найдено фильмов: {count}")
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
            print_error(
                "Некорректный ввод. Введите номер из списка или 0 для выхода в меню.")

    @staticmethod
    def ask_year_range(year_min: int, year_max: int) -> tuple[int, int] | None:
        """Запрашивает диапазон лет с валидацией.

        Поддерживается формат "2005" или "2005-2012".
        :return: (year_from, year_to) или None если пользователь вышел в меню.
        """
        while True:
            year_input = input(
                f"Введите год или диапазон через тире, например {year_min}-{year_max}"
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
            print_error(
                f"Некорректный ввод. Введите год в диапазоне {year_min}–{year_max}"
                f" или 0 для выхода в меню."
            )

    # --- Топ-5 популярных запросов ---

    def show_top_5_queries(self) -> None:
        """Выводит топ-5 запросов по частоте или по времени последних поисков."""

        print_section("Топ-5 запросов")
        print_info("1. По частоте (самые популярные)")
        print_info("2. По последним поискам")
        print_info("0. Вернуться в меню")

        choice = input("Введите номер опции: ").strip()

        if choice == "0":
            self.show_options_messages()
            self.handle_user_input(self.get_start_answer())
            return

        elif choice == "1":
            # Агрегация из MongoDB: группировка по запросу, сортировка по количеству
            results = self.logger.get_top_searches(5)
            if not results:
                print_info("История поиска пуста.")
            else:
                print_section("Топ-5 популярных запросов")
                format_search_history_table(results, show_count=True)

        elif choice == "2":
            # Последние 5 документов из MongoDB, отсортированные по timestamp
            results = self.logger.get_recent_searches(5)
            if not results:
                print_info("История поиска пуста.")
            else:
                print_section("Последние 5 поисков")
                format_search_history_table(results, show_count=False)

        else:
            print_error("Некорректный ввод.")

        self.show_options_messages()
        self.handle_user_input(self.get_start_answer())
