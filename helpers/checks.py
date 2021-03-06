import json
from typing import TypeVar, Callable

from disnake.ext import commands

from exceptions import *

T = TypeVar("T")

owner_id = 104244519838416896


def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """

    async def predicate(context: commands.Context) -> bool:
        if context.author.id != owner_id:
            raise UserNotOwner
        return True

    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is blacklisted.
    """

    async def predicate(context: commands.Context) -> bool:
        with open("blacklist.json") as file:
            data = json.load(file)
        if context.author.id in data["ids"]:
            raise UserBlacklisted
        return True

    return commands.check(predicate)