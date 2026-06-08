import pymysql


class DB:
    def __init__(self, dbconfig: dict) -> None:
        # Открываем соединение с MySQL при создании экземпляра
        self.connection = pymysql.connect(**dbconfig)

    def get_categories(self) -> tuple:
        """Возвращает все жанры из таблицы category."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT category_id, name FROM category")
            return cursor.fetchall()

    def get_year_range(self) -> tuple[int, int]:
        """Возвращает минимальный и максимальный год выпуска фильмов."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT MIN(release_year), MAX(release_year) FROM film")
            return cursor.fetchone()

    def search_by_title(self, film_title: str) -> tuple[int, list[tuple]]:
        """Ищет фильмы по части названия.

        :param film_title: Часть названия фильма.
        :return: Кортеж (количество найденных, список кортежей (title, year, rating)).
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT title, release_year, rating FROM film WHERE title LIKE %s ORDER BY title",
                (f"%{film_title}%",),
            )
            results = cursor.fetchall()
            return len(results), list(results)

    def search_by_genre_and_year(
        self, category_id: int, year_from: int, year_to: int
    ) -> tuple[int, list[tuple]]:
        """Ищет фильмы по жанру и диапазону годов выпуска.

        :param category_id: ID жанра из таблицы category.
        :param year_from: Начальный год диапазона.
        :param year_to: Конечный год диапазона.
        :return: Кортеж (количество найденных, список кортежей (title, year, rating)).
        """
        with self.connection.cursor() as cursor:
            sql = """
                SELECT f.title, f.release_year, f.rating
                FROM film AS f
                JOIN film_category AS fc ON f.film_id = fc.film_id
                WHERE fc.category_id = %s
                  AND f.release_year BETWEEN %s AND %s
                ORDER BY f.title
            """
            cursor.execute(sql, (category_id, year_from, year_to))
            results = cursor.fetchall()
            return len(results), list(results)

    def __del__(self) -> None:
        """Закрывает соединение с базой данных при удалении объекта."""
        self.connection.close()
