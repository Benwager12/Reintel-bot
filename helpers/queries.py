import time

import psycopg2.errors

from helpers import database, config
from psycopg2 import connect as dbconnect


def check_db_connection() -> None:
    """
    Opens a connection to the database if the URL has been changed.
    """
    if database.DATABASE_URL != config.config['DATABASE_URL']:
        database.DB_URL = database.DATABASE_URL
        print("Database URL changed: " + database.DATABASE_URL)
        print("Reconnecting to database...")
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
    query = f"SELECT MESSAGE, TIME_ADDED FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}' " \
            f"ORDER BY TIME_ADDED"

    try:
        cursor.execute(query)
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{query}")
        return []
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
    try:
        cursor.execute(query)
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{query}")
        return []
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

    query = f"DELETE FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}'" \
            f" AND TIME_ADDED = '{content[1]}' AND MESSAGE = '{content[0]}'"
    try:
        cursor.execute(query)
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{query}")
    database.connection.commit()
    cursor.close()


def add_item(user_id: int, server_id: int, message: str) -> None:
    """
    Adds a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param message: The message to add to the todo list.
    """
    add_items(user_id, server_id, [message])


def add_items(user_id: int, server_id: int, messages: list[str]) -> None:
    """
    Adds a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param messages: The messages to add to the todo list.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    add = f"INSERT INTO USER_TODO (USER_ID, SERVER_ID, MESSAGE, TIME_ADDED) VALUES (%s, %s, %s, %s);"
    multiple_query = add * len(messages)
    multiple_tuple = []

    for message in messages:
        multiple_tuple.append(user_id)
        multiple_tuple.append(server_id)
        multiple_tuple.append(message)
        multiple_tuple.append(int(time.time()))

    try:
        cursor.execute(multiple_query, tuple(multiple_tuple))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{add}")

    database.connection.commit()
    cursor.close()
