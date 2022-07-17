import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction

from helpers import checks, database

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


class Todo(commands.Cog, name="todo-slash"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="list",
        description="Lists all of your todos",
        aliases=["todos", "todo"]
    )
    @checks.not_blacklisted()
    async def add(self, interaction: ApplicationCommandInteraction) -> None:
        """"
        Adds a todo to the list
        :param interaction: The application command interaction
        """
        cursor = database.connection.cursor()
        query = f"SELECT MESSAGE, TIME_ADDED FROM USER_TODO WHERE USER_ID = '{interaction.author.id}' AND " \
                f"SERVER_ID = '{interaction.guild_id}' ORDER BY TIME_ADDED"
        cursor.execute(query)
        returned = cursor.fetchall()

        embed = disnake.Embed()
        embed.set_author(name=f"{interaction.author.display_name}'s Todos", icon_url=interaction.author.avatar.url)

        for x, todo in enumerate(returned):
            number_emoji = ""
            for i in range(len(str(x + 1))):
                number_emoji += f":{number_conversion[int(str(x + 1)[i])]}:"
            embed.add_field(name="** **", value=f"{number_emoji}. {todo[0]} (<t:{todo[1]}:R>)", inline=False)
        cursor.close()

        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Todo(bot))
