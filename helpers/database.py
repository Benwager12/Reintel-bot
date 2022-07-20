import psycopg2
from helpers.config import config


DATABASE_URL = config['DATABASE_URL']
DB_URL = DATABASE_URL  # Used for checking for changes in the config file.

connection = psycopg2.connect(DATABASE_URL, sslmode="require")

def url_updated() -> bool:
    """
    Checks if the DATABASE_URL has changed.
    :return: True if the DATABASE_URL has changed, False otherwise.
    """
    if DATABASE_URL != DB_URL:
        DB_URL = DATABASE_URL
        return True

def open_db_connection() -> None:
    """
    Opens a connection to the database.
    """
    database.connection = psycopg2.connect(database.DATABASE_URL, sslmode="require")