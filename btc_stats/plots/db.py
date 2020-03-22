from pathlib import Path
import sqlite3


def assert_db_exists(path):
    if not path.exists():
        print(f'path not found: {path}')
        sys.exit(1)


def open_db(name):
    db_path = Path('data', name)
    assert_db_exists(db_path)
    return sqlite3.connect(db_path)
