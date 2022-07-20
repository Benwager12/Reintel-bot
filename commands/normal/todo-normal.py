import time
from datetime import datetime

import disnake
from disnake import Member, Embed
from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import checks, queries

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


def convert_unix(unix_timestamp: int): return f"<t:{unix_timestamp}:T>, <t:{unix_timestamp}:d>"


def convert_unix_now(): return convert_unix(int(datetime.utcnow().timestamp() + 3600))


def todo_embed(items: list, author: Member, description: str = None, crossed: int = None) -> \
        tuple[str, None] | tuple[None, Embed]:
    """
    Returns an embed with all of the todo items for a user.
    :param items: The todo items to include in the embed.
    :param author: The author of the todo items.
    :param description: The description of the embed.
    :param crossed: Which todo items will be crossed out.
    :return: The embed with the todo items.
    """

    if len(items) == 0:
        return "You have no todos!", None

    embed = disnake.Embed()
    embed.set_author(name=f"{author.display_name}'s Todos", icon_url=author.avatar.url)
    embed.description = description

    for x, todo in enumerate(items):
        formatting = number_emoji(x + 1) + ". "
        formatting += f"~~{todo[0]}~~" if crossed is True or crossed == x + 1 else todo[0]
        formatting += f" ({convert_unix(todo[1])})"

        embed.add_field(name="** **", value=formatting, inline=False)

    return None, embed


def todo_embed_from_user(author: Member, server_id: int, description: str = None, crossed: int = None) -> \
        tuple[str, None] | tuple[None, Embed]:
    """
        Returns an embed with all of the todo items for a user.
        :param author: The author of the todo items.
        :param server_id: The id of the server to get the todo items from.
        :param description: The description of the embed.
        :param crossed: Which todo items will be crossed out.
        :return: The embed with the todo items.
        """
    items = queries.todo_items(author.id, server_id)

    return todo_embed(items, author, description, crossed)


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
        message, embed = todo_embed_from_user(ctx.author, ctx.guild.id)

        await ctx.reply(message, embed=embed)

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
            await provide.delete(delay=5)
            return

        msg = msg.replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`")

        todos = queries.todo_items(ctx.author.id, ctx.guild.id)
        todos.append((f"{':boom: ' * 5}", int(time.time())))

        _, embed = todo_embed(todos, ctx.author)

        added = await ctx.reply(f"Added to your todo list. :ok_hand:", embed=embed)
        queries.add_item(ctx.author.id, ctx.guild.id, msg)

        time.sleep(1)

        _, embed = todo_embed_from_user(ctx.author, ctx.guild.id)
        await added.edit(embed=embed)

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
        items = queries.todo_items(ctx.author.id, ctx.guild.id)
        item_number = len(items)

        if item_number == 0:
            return

        queries.clear_items(ctx.author.id, ctx.guild.id)

        _, embed = todo_embed(items, ctx.author, description="Clearing your todolist...", crossed=True)

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

        _, embed = todo_embed(items, ctx.author, crossed=number)

        removed = await ctx.reply(f"Ticked off todo item #{number}! :tada:", embed=embed)

        time.sleep(2)
        new_items = items.copy()
        new_items.pop(number - 1)

        _, embed = todo_embed(new_items, ctx.author)

        print(type(embed))

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

        for i in range(10):
            queries.add_item(member.id, ctx.guild.id, str(i + 1))

        test = await ctx.reply("Added 10 items")
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
