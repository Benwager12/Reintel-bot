import time

import disnake
from disnake import Member, Embed
from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import checks, queries, embeds


class Todo(commands.Cog, name="todo-normal", description=":notepad_spiral: This is where my commands are stored about "
                                                         "using the todo list."):
    def __init__(self, bot: disnake.ext.commands.bot.Bot):
        self.bot = bot

    @commands.command(
        name="list",
        description="Lists all of your todos",
        aliases=["todos", "todo"],
        usage="list"
    )
    @checks.not_blacklisted()
    async def list(self, ctx: Context, user: Member = None) -> None:
        """"
        Lists all of your todos
        :param ctx: The context for the command
        :param user: The user to list the todos for.
        """

        if user is None:
            user = ctx.author

        if user is not ctx.author and ctx.author.id != checks.owner_id:
            await ctx.send("You can't list someone else's todos!")
            return

        message, embed = embeds.todo_embed_from_user(user, ctx.guild.id)

        if ctx.author.id != user.id and embed is None:
            message = f"`{user.display_name}` has no todos!"

        await ctx.reply(message, embed=embed)

    @commands.command(
        name="add",
        description="Adds to your list of todos",
        aliases=["addtodo"],
        usage="add <todo>"
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

        _, embed = embeds.todo_embed(todos, ctx.author)

        added = await ctx.reply(f"Added to your todo list. :ok_hand:", embed=embed)
        queries.add_item(ctx.author.id, ctx.guild.id, msg)

        time.sleep(1)

        _, embed = embeds.todo_embed_from_user(ctx.author, ctx.guild.id)
        await added.edit(embed=embed)

    @commands.command(
        name="clear",
        description="Adds to your list of todos",
        aliases=["cleartodo"],
        usage="clear [instant]"
    )
    @checks.not_blacklisted()
    async def clear(self, ctx: Context, *args) -> None:
        """"
        Adds a todo to the list
        :param ctx: The context for the command
        """
        items = queries.todo_items(ctx.author.id, ctx.guild.id)
        item_number = len(items)

        if item_number == 0:
            return

        queries.clear_items(ctx.author.id, ctx.guild.id)

        if "instant" in args:
            await ctx.reply(f"Cleared your todo list. :ok_hand:")
            return

        _, embed = embeds.todo_embed(items, ctx.author, description="Clearing your todolist...", crossed=True)

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
    async def remove(self, ctx: Context, number: int = None) -> None:
        if number is None:
            error = await ctx.reply("Please provide a number to tick off!")
            await error.delete(delay=5)
            return

        if number < 1:
            error = await ctx.reply("Please provide a number greater than or equal to 1!")
            await error.delete(delay=5)
            return

        items = queries.todo_items(ctx.author.id, ctx.guild.id)

        if len(items) < number:
            error = await ctx.reply("You don't have that many todos!")
            await error.delete(delay=5)
            return

        queries.remove_item(ctx.author.id, ctx.guild.id, items[number - 1])

        _, embed = embeds.todo_embed(items, ctx.author, crossed=number)

        removed = await ctx.reply(f"Ticked off todo item #{number}! :tada:", embed=embed)

        time.sleep(2)
        new_items = items.copy()
        new_items.pop(number - 1)

        _, embed = embeds.todo_embed(new_items, ctx.author)

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

        queries.add_items(member.id, ctx.guild.id, [str(i + 1) for i in range(10)])

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
