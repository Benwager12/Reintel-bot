import time

from disnake import Member, ApplicationCommandInteraction
from disnake.ext import commands

from helpers import checks, queries, embeds


class Todo(commands.Cog, name="todo-slash"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="list",
        description="Lists all of your todos",
        aliases=["todos", "todo"],
        usage="list"
    )
    @checks.not_blacklisted()
    async def list(self, interaction: ApplicationCommandInteraction, user: Member = None) -> None:
        """"
        Lists all of your todos
        :param interaction: The context for the command
        :param user: The user to list the todos for.
        """

        if user is None:
            user = interaction.author

        if user is not interaction.author and interaction.author.id != checks.owner_id:
            await interaction.send("You can't list someone else's todos!")
            return

        message, embed = embeds.todo_embed_from_user(user, interaction.guild.id)

        if interaction.author.id != user.id and embed is None:
            message = f"`{user.display_name}` has no todos!"

        await interaction.reply(message, embed=embed)

    @commands.slash_command(
        name="add",
        description="Adds to your list of todos",
        aliases=["addtodo"],
        usage="add <todo>"
    )
    @checks.not_blacklisted()
    async def add(self, interaction: ApplicationCommandInteraction, *args) -> None:
        """"
        Adds a todo to the list
        :param interaction: The context for the command
        :param args: The message to add to the todo list
        """

        msg = " ".join(args)
        if len(args) == 0:
            provide = await interaction.send("Please provide a message to add to your todo list!")
            await provide.delete(delay=5)
            return

        msg = msg.replace("\"", "\\\"").replace("\'", "\\\'").replace("`", "\\`")

        todos = queries.todo_items(interaction.author.id, interaction.guild.id)
        todos.append((f"{':boom: ' * 5}", int(time.time())))

        _, embed = embeds.todo_embed(todos, interaction.author)

        added = await interaction.reply(f"Added to your todo list. :ok_hand:", embed=embed)
        queries.add_item(interaction.author.id, interaction.guild.id, msg)

        time.sleep(1)

        _, embed = embeds.todo_embed_from_user(interaction.author, interaction.guild.id)
        await added.edit(embed=embed)

    @commands.slash_command(
        name="clear",
        description="Adds to your list of todos",
        aliases=["cleartodo"],
        usage="clear [instant]"
    )
    @checks.not_blacklisted()
    async def clear(self, interaction: ApplicationCommandInteraction, instant: bool = False) -> None:
        """"
        Adds a todo to the list
        :param interaction: The context for the command
        :param instant: Whether to clear the todo list instantly or not
        """
        items = queries.todo_items(interaction.author.id, interaction.guild.id)
        item_number = len(items)

        if item_number == 0:
            return

        queries.clear_items(interaction.author.id, interaction.guild.id)

        if instant:
            await interaction.reply(f"Cleared your todo list. :ok_hand:")
            return

        _, embed = embeds.todo_embed(items, interaction.author, description="Clearing your todolist...", crossed=True)

        delete = await interaction.reply(embed=embed)

        for i in range(item_number):
            time.sleep(.8)
            embed.remove_field(len(embed.fields) - 1)
            await delete.edit(embed=embed)
        await delete.edit(content="Cleared all of your todos! :sparkles:", embed=None)
        await delete.delete(delay=5)

    @commands.slash_command(
        name="remove",
        description="Currently tested item",
        aliases=["deletetodo", "tick"]
    )
    async def remove(self, interaction: ApplicationCommandInteraction, number: int = None) -> None:
        if number is None:
            error = await interaction.reply("Please provide a number to tick off!")
            await error.delete(delay=5)
            return

        if number < 1:
            error = await interaction.reply("Please provide a number greater than or equal to 1!")
            await error.delete(delay=5)
            return

        items = queries.todo_items(interaction.author.id, interaction.guild.id)

        if len(items) < number:
            error = await interaction.reply("You don't have that many todos!")
            await error.delete(delay=5)
            return

        queries.remove_item(interaction.author.id, interaction.guild.id, items[number - 1])

        _, embed = embeds.todo_embed(items, interaction.author, crossed=number)

        removed = await interaction.reply(f"Ticked off todo item #{number}! :tada:", embed=embed)

        time.sleep(2)
        new_items = items.copy()
        new_items.pop(number - 1)

        _, embed = embeds.todo_embed(new_items, interaction.author)

        await removed.edit(embed=embed)

    @commands.slash_command(
        name="add_items",
        description="Add 10 items to the todo list",
        aliases=["add_todos", "additems", "addtodos"]
    )
    @checks.is_owner()
    async def add_items(self, interaction: ApplicationCommandInteraction, member: Member = None) -> None:
        if member is None:
            member = interaction.author

        queries.add_items(member.id, interaction.guild.id, [str(i + 1) for i in range(10)])

        test = await interaction.reply("Added 10 items")
        await test.delete(delay=3)


def setup(bot):
    bot.add_cog(Todo(bot))
