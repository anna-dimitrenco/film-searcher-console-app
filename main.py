import sys
from config import Config
from formatter import r_print
from library import Library
from mongo_connector import MongoDB
from mysql_connector import DB

def main() -> None:
    try:
        db = DB(Config.db)
    except Exception as e:
        r_print(f"Verbindung zu MySQL fehlgeschlagen: {e}", "bold red", "✘")
        sys.exit(1)
    try:
        logger = MongoDB(Config.mongo)
    except Exception as e:
        r_print(f"Verbindung zu MongoDB fehlgeschlagen: {e}", "bold red", "✘")
        sys.exit(1)
        
    library = Library(db, logger)
    library.start_project()

if __name__ == "__main__":
    main()
