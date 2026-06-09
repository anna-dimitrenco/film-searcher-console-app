import sys

from config import Config
from formatter import r_print
from library import Library
from mongo_connector import MongoDB
from mysql_connector import DB


def main() -> None:
    try:
        db = DB(Config.dbconfig)
    except Exception as e:
        r_print(f"Не удалось подключиться к MySQL: {e}", "bold red", "✘")
        sys.exit(1)

    try:
        logger = MongoDB(Config.mongoconfig)
    except Exception as e:
        r_print(f"Не удалось подключиться к MongoDB: {e}", "bold red", "✘")
        sys.exit(1)

    library = Library(db, logger)
    library.start_project()


if __name__ == "__main__":
    main()
