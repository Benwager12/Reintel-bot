import time
from datetime import datetime

import disnake
from disnake import Member
from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import checks, database, queries

number_conversion = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine"
}


def number_emoji(number): return "".join(f":{number_conversion[int(str(number)[i])]}:" for i in range(len(str(number))))


def todo_embed(items: list, author: Member, description: str = None, crossed: int = None) -> disnake.Embed:
    """
    Returns an embed with all of the todo items for a user.
    :param items: The todo items to include in the embed.
    :param author: The author of the todo items.
    :param description: The description of the embed.
    :param crossed: Which todo items will be crossed out.
    :return: The embed with the todo items.
    """
    embed = disnake.Embed()
    embed.set_author(name=f"{author.display_name}'s Todos", icon_url=author.avatar.url)
    embed.description = description

    for x, todo in enumerate(items):
        formatting = number_emoji(x + 1) + ". "
        formatting += f"~~{todo[0]}~~" if crossed is True or crossed == x + 1 else todo[0]
        formatting += f" (<t:{todo[1]}:T>, <t:{todo[1]}:d>)"

        embed.add_field(name="** **", value=formatting, inline=False)
    return embed


class Todo(commands.Cog, name="todo-normal"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="list",
        description="Lists all of your todos",
        aliases=["todos", "todo"]
    )
    @checks.not_blacklisted()
    async def list(self, ctx: Context) -> None:
        """"
        Lists all of your todos
        :param ctx: The context for the command
        """
        cursor = database.connection.cursor()
        query = f"SELECT MESSAGE, TIME_ADDED FROM USER_TODO WHERE USER_ID = '{ctx.author.id}' AND " \
                f"SERVER_ID = '{ctx.guild.id}' ORDER BY TIME_ADDED"
        cursor.execute(query)
        returned = cursor.fetchall()

        if len(returned) == 0:
            await ctx.reply("You have no todos!")
            return

        embed = todo_embed(returned, ctx.author)

        cursor.close()

        await ctx.reply(embed=embed)

    @commands.command(
        name="add",
        description="Adds to your list of todos",
        aliases=["addtodo"]
    )
    @checks.not_blacklisted()
    async def add(self, ctx: Context, *args) -> None:
        """"
        Adds a todo to the list
        :param ctx: The context for the command
        :param args: The message to add to the todo list
        """

        msg = " ".join(args)
        if len(args) == 0:
            provide = await ctx.send("Please provide a message to add to your todo list!")
            provide.delete(delay=5)
            return

        msg = msg.replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`")

        cursor = database.connection.cursor()
        query = f"INSERT INTO USER_TODO (USER_ID, SERVER_ID, MESSAGE, TIME_ADDED) VALUES (%s, %s, %s, %s)"
        print(query)
        cursor.execute(query, (ctx.author.id, ctx.guild.id, msg, datetime.utcnow().timestamp()))
        database.connection.commit()
        cursor.close()

        added = await ctx.reply(f"Added `{msg}` to your todo list.")
        await added.delete(delay=5)

    @commands.command(
        name="clear",
        description="Adds to your list of todos",
        aliases=["cleartodo"]
    )
    @checks.not_blacklisted()
    async def clear(self, ctx: Context) -> None:
        """"
        Adds a todo to the list
        :param ctx: The context for the command
        """

        cursor = database.connection.cursor()
        list_query = f"SELECT MESSAGE, TIME_ADDED FROM USER_TODO WHERE USER_ID = '{ctx.author.id}' AND " \
                     f"SERVER_ID = '{ctx.guild.id}' ORDER BY TIME_ADDED"

        delete_query = f"DELETE FROM USER_TODO WHERE USER_ID = '{ctx.author.id}' AND SERVER_ID = '{ctx.guild.id}'"

        cursor.execute(list_query)
        items = cursor.fetchall()
        item_number = len(items)

        if item_number == 0:
            return

        cursor.execute(delete_query)
        database.connection.commit()
        cursor.close()

        embed = todo_embed(items, ctx.author, description="Clearing your todolist...", crossed=True)

        delete = await ctx.reply(embed=embed)

        for i in range(item_number):
            time.sleep(.8)
            embed.remove_field(len(embed.fields) - 1)
            await delete.edit(embed=embed)
        await delete.edit(content="Cleared all of your todos! :sparkles:", embed=None)
        await delete.delete(delay=5)

    @commands.command(
        name="remove",
        description="Currently tested item",
        aliases=["deletetodo", "tick"]
    )
    @checks.is_owner()
    async def remove(self, ctx: Context, number: int = None) -> None:
        if number is None:
            error = await ctx.reply("Please provide a number to tick off!")
            await error.delete(delay=5)
            return

        items = queries.todo_items(ctx.author.id, ctx.guild.id)

        if len(items) < number:
            error = await ctx.reply("You don't have that many todos!")
            await error.delete(delay=5)
            return

        queries.remove_item(ctx.author.id, ctx.guild.id, items[number - 1])

        embed = todo_embed(items, ctx.author, crossed=number, )
        embed.colour = 0xffbf00
        removed = await ctx.reply(f"Ticked off todo item #{number}! :tada:", embed=embed)

        time.sleep(2)
        new_items = items.copy()
        new_items.pop(number - 1)

        embed = todo_embed(new_items, ctx.author)
        embed.colour = 0xffde00
        await removed.edit(embed=embed)

    @commands.command(
        name="add_items",
        description="Add 10 items to the todo list",
        aliases=["add_todos", "additems", "addtodos"]
    )
    @checks.is_owner()
    async def add_items(self, ctx: Context, member: Member = None) -> None:
        if member is None:
            member = ctx.author

        query = f"INSERT INTO USER_TODO (USER_ID, SERVER_ID, MESSAGE, TIME_ADDED) VALUES (%s, %s, %s, %s)"
        cursor = database.connection.cursor()
        for i in range(10):
            cursor.execute(query, (member.id, ctx.guild.id, i + 1, datetime.utcnow().timestamp()))
        database.connection.commit()
        cursor.close()

        test = await ctx.reply("Done")
        await test.delete(delay=3)

    @commands.command(
        name="test",
        description="Currently tested item"
    )
    @checks.is_owner()
    async def test(self, ctx: Context, *args) -> None:
        colour = 0
        embed = disnake.Embed(title="Test", description="Test", colour=colour)
        reply = await ctx.reply(embed=embed)

        for i in range(16):
            time.sleep(.2)
            colour += 16 * 16 * 16
            embed.colour = colour
            await reply.edit(embed=embed)
            print(colour)


def setup(bot):
    bot.add_cog(Todo(bot))
