import sys

from config import Config
from formatter import print_error
from library import Library
from mongo_connector import MongoDB
from mysql_connector import DB


def main() -> None:
    try:
        db = DB(Config.dbconfig)
    except Exception as e:
        print_error(f"Не удалось подключиться к MySQL: {e}")
        sys.exit(1)

    try:
        logger = MongoDB(Config.mongoconfig, Config.collection_name)
    except Exception as e:
        print_error(f"Не удалось подключиться к MongoDB: {e}")
        sys.exit(1)

    library = Library(db, logger)
    library.start_project()


if __name__ == "__main__":
    main()
