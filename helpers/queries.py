from helpers import database, config
from datetime import datetime
from psycopg2 import connect as dbconnect


def check_db_connection() -> None:
    """
    Opens a connection to the database if the URL has been changed.
    """
    if database.DATABASE_URL != database.DB_URL:
        database.DB_URL = database.DATABASE_URL
        database.connection = dbconnect(database.DATABASE_URL, sslmode="require")


def todo_items(user_id: int, server_id: int) -> list:
    """
    Returns a list of todo items for a user on a server.
    :param user_id: The user id to get the todo items for.
    :param server_id: The server id to get the todo items for.
    :return: A list of todo items.
    """
    check_db_connection()

    cursor = database.connection.cursor()
    query = f"SELECT MESSAGE, TIME_ADDED FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}' "\
            f"ORDER BY TIME_ADDED"
    cursor.execute(query)
    items = cursor.fetchall()
    cursor.close()
    return items


def clear_items(user_id: int, server_id: int) -> None:
    """
    Clears all todo items for a user on a server.
    :param user_id: The user id to clear the todo items for.
    :param server_id: The server id to clear the todo items for.
    """
    check_db_connection()

    cursor = database.connection.cursor()
    query = f"DELETE FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}'"
    cursor.execute(query)
    database.connection.commit()
    cursor.close()


def remove_item(user_id: int, server_id: int, content: (str, int)) -> None:
    """
    Removes a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param content: The content of the todo item to remove.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    destroy = f"DELETE FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}'" \
              f" AND TIME_ADDED = '{content[1]}' AND MESSAGE = '{content[0]}'"
    cursor.execute(destroy)
    database.connection.commit()
    cursor.close()


def add_item(user_id: int, server_id: int, message: str) -> None:
    """
    Adds a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param message: The content of the todo item to add.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    destroy = f"INSERT INTO USER_TODO (USER_ID, SERVER_ID, MESSAGE, TIME_ADDED) VALUES (%s, %s, %s, %s)"
    cursor.execute(destroy, (user_id, server_id, message, datetime.utcnow().timestamp() + 3600))
    database.connection.commit()
    cursor.close()
