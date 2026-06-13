import pymysql

class DB:
    def __init__(self, dbconfig: dict) -> None:
        # Open the MySQL connection when the instance is created
        self.connection = pymysql.connect(**dbconfig)

    def get_categories(self) -> tuple:
        """Returns all genres from the category table."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT category_id, name FROM category")
            return cursor.fetchall()

    def get_year_range(self) -> tuple[int, int]:
        """Returns the minimum and maximum film release years."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT MIN(release_year), MAX(release_year) FROM film")
            return cursor.fetchone()

    def search_by_title(self, film_title: str) -> tuple[int, list[tuple]]:
        """Searches for films by a partial title match.

        :param film_title: Part of the film title.
        :return: Tuple (count of results, list of tuples (title, year, rating)).
        """
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT title, release_year, rating FROM film WHERE title LIKE %s ORDER BY title",
                (f"%{film_title}%",),
            )
            results = cursor.fetchall()
            return len(results), list(results)

    def filter_by_genre_and_year(
        self, category_id: int, year_from: int, year_to: int
    ) -> tuple[int, list[tuple]]:
        """Filters films by genre and release year range.

        :param category_id: Genre ID from the category table.
        :param year_from: Start year of the range.
        :param year_to: End year of the range.
        :return: Tuple (count of results, list of tuples (title, year, rating)).
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
        """Closes the database connection when the object is destroyed."""
        self.connection.close()
