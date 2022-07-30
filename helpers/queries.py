import time

import disnake
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


def add_item(user_id: int, server_id: int, message: str) -> int:
    """
    Adds a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param message: The message to add to the todo list.
    """
    return add_items(user_id, server_id, [message])[0]


def add_items(user_id: int, server_id: int, messages: list[str]) -> tuple[int]:
    """
    Adds a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param messages: The messages to add to the todo list.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    insert = f"INSERT INTO USER_TODO (USER_ID, SERVER_ID, MESSAGE, TIME_ADDED) VALUES "
    values = ", ".join(["(%s, %s, %s, %s)" for x in range(len(messages))])
    multiple_query = insert + values + " RETURNING ID;"
    multiple_tuple = []

    for message in messages:
        multiple_tuple.append(user_id)
        multiple_tuple.append(server_id)
        multiple_tuple.append(message)
        multiple_tuple.append(int(time.time()))

    print(f"{multiple_query} with {multiple_tuple}")

    try:
        cursor.execute(multiple_query, tuple(multiple_tuple))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{multiple_query}")

    ids = cursor.fetchone()

    database.connection.commit()
    cursor.close()

    return ids


def add_react(user_id, message_id, emoji, role_id, guild_id):
    """
    Adds a reaction to a message.
    :param user_id: The user id to add the reaction for.
    :param message_id: The message id to add the reaction to.
    :param emoji: The emoji to add to the message.
    :param role_id: The role that will be given to the user when the reaction is added.
    :param guild_id: The guild that the message is in.
    """
    react_message = get_react_message(message_id, guild_id)

    if react_message is None:
        add_new_react(user_id, message_id, emoji, role_id, guild_id)
        return

    emoji_ids_str = react_message[4]

    check_db_connection()

    cursor = database.connection.cursor()

    emoji_role = "INSERT INTO REACT_EMOJI_ROLE_MATCH (REACT_EMOJI, ROLE_ID)" \
                 "VALUES (%s, %s) RETURNING ID;"

    try:
        cursor.execute(emoji_role, (emoji, role_id))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{emoji_role}")

    update = "UPDATE REACTIONARIES SET REACT_EMOJI_LINKS = %s WHERE ID = %s;"

    emoji_ids = [x for x in emoji_ids_str.split(',')]
    emoji_ids.append(str(cursor.fetchone()[0]))

    update_tuple = (','.join(emoji_ids), react_message[0])

    try:
        cursor.execute(update, update_tuple)
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{update}")

    database.connection.commit()
    cursor.close()


def add_new_react(user_id, message_id, emoji, role_id, guild_id):
    """
    Adds a reaction to a message.
    :param user_id: The user id to add the reaction for.
    :param message_id: The message id to add the reaction to.
    :param emoji: The emoji to add to the message.
    :param role_id: The role that will be given to the user when the reaction is added.
    :param guild_id: The guild that the message is in.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    emoji_role = "INSERT INTO REACT_EMOJI_ROLE_MATCH (REACT_EMOJI, ROLE_ID)" \
                 "VALUES (%s, %s) RETURNING ID;"

    try:
        cursor.execute(emoji_role, (emoji, role_id))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{emoji_role}")

    emoji_role_id = cursor.fetchone()[0]

    message_emoji = "INSERT INTO REACTIONARIES (MESSAGE_ID, USER_ID, SERVER_ID, REACT_EMOJI_LINKS)" \
                    "VALUES (%s, %s, %s, %s);"

    try:
        cursor.execute(message_emoji, (message_id, user_id, guild_id, emoji_role_id))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{message_emoji}")

    database.connection.commit()
    cursor.close()
    return None


def get_react_message(message_id: int, guild_id) -> tuple:
    """
    Checks if a message is a reaction message.
    :param message_id: The message id to check.
    :param guild_id: The guild id to check.
    :return: True if the message is a reaction message, False otherwise.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    query = "SELECT ID, MESSAGE_ID, USER_ID, SERVER_ID, REACT_EMOJI_LINKS FROM REACTIONARIES " \
            "WHERE MESSAGE_ID = %s AND SERVER_ID = %s;"

    try:
        cursor.execute(query, (message_id, guild_id))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{query}")

    result = cursor.fetchone()

    cursor.close()

    return result


def get_react_roles(message_id, user_id, guild_id) -> dict:
    """
    Gets the roles that a user has for a message.
    :param message_id: The message id to check.
    :param user_id: The user id to check.
    :param guild_id: The guild id to check.
    :return: The roles that are given to the user.
    """
    check_db_connection()

    cursor = database.connection.cursor()

    query = "SELECT REACT_EMOJI_LINKS FROM REACTIONARIES " \
            "WHERE MESSAGE_ID = %s AND USER_ID = %s AND SERVER_ID = %s;"

    try:
        cursor.execute(query, (message_id, user_id, guild_id))
    except psycopg2.errors.InFailedSqlTransaction:
        print(f"Failed to execute query:\n{query}")

    result = cursor.fetchone()[0]

    if result is None:
        return None

    print(result)

    emoji_ids = [x for x in result.split(',')]

    role_matches = dict()

    for emoji_id in emoji_ids:
        query = "SELECT REACT_EMOJI, ROLE_ID FROM REACT_EMOJI_ROLE_MATCH " \
                f"WHERE ID = {emoji_id};"
        try:
            print(emoji_id)
            cursor.execute(query)
        except psycopg2.errors.InFailedSqlTransaction:
            print(f"Failed to execute query:\n{query}")

        item = cursor.fetchone()
        print(item)

        role_matches[item[0]] = item[1]
    cursor.close()

    return role_matches


def get_react_role(message_id, user_id, guild_id, react_emoji):
    """
    Gets the role that is given to a user when a reaction is added.
    :param message_id: The message id to check.
    :param user_id: The user id to check.
    :param guild_id: The guild id to check.
    :param react_emoji: The emoji to check
    :return: The role that is given to a user when a reaction is added.
    """
    return get_react_roles(message_id, user_id, guild_id)[react_emoji]
