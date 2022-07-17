from helpers import database
from disnake import Message


def todo_items(user_id: str, server_id: str) -> list:
    """
    Returns a list of todo items for a user on a server.
    :param user_id: The user id to get the todo items for.
    :param server_id: The server id to get the todo items for.
    :return: A list of todo items.
    """
    cursor = database.connection.cursor()
    query = f"SELECT MESSAGE, TIME_ADDED FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}' "\
            f"ORDER BY TIME_ADDED"
    cursor.execute(query)
    items = cursor.fetchall()
    cursor.close()
    return items


def clear_items(user_id: str, server_id: str) -> None:
    """
    Clears all todo items for a user on a server.
    :param user_id: The user id to clear the todo items for.
    :param server_id: The server id to clear the todo items for.
    """
    cursor = database.connection.cursor()
    query = f"DELETE FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}'"
    cursor.execute(query)
    database.connection.commit()
    cursor.close()


def remove_item(user_id: str, server_id: str, content: (str, int)):
    """
    Removes a todo item for a user on a server.
    :param user_id: The user id to remove the todo item for.
    :param server_id: The server id to remove the todo item for.
    :param content: The content of the todo item to remove.
    """

    cursor = database.connection.cursor()

    destroy = f"DELETE FROM USER_TODO WHERE USER_ID = '{user_id}' AND SERVER_ID = '{server_id}'" \
              f" AND TIME_ADDED = '{content[1]}' AND MESSAGE = '{content[0]}'"
    cursor.execute(destroy)
    database.connection.commit()
    cursor.close()
