import disnake
from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import embeds, checks, queries


class Utilities(commands.Cog, name="utilities-normal", description=":star: This is the essential commands that give "
                                                                   "information about the bot or do a generic feature"):
    def __init__(self, bot: disnake.ext.commands.bot.Bot):
        self.bot = bot

    @commands.command(
        name="ping",
        description="Gets the bot latency!",
        aliases=["pong"],
        usage="ping"
    )
    async def ping(self, ctx: Context) -> None:
        embed = disnake.Embed(title="Pong!", description=f"The current bot latency is {ctx.bot.latency * 1000:.0f}ms")
        await ctx.send(embed=embed)

    @commands.command(
        name="info",
        description="Get information about the bot!",
        aliases=["about"],
        usage="info"
    )
    async def info(self, ctx: Context):
        await ctx.send(embed=embeds.bot_information_embed())

    @commands.command(
        name="help",
        description="Get help about a command!",
        aliases=["commands"],
        usage="help <category|command> <category name | command name>"
    )
    async def help(self, ctx: Context, option_view: str = None, item_view: str = None) -> None:
        if option_view is None:
            await ctx.send(embed=embeds.help_embed_categories())
            return

        if option_view.lower() == "category":
            await ctx.send(embed=embeds.help_embed_category(item_view))
            return

        if option_view.lower() == "command":
            await ctx.send(embed=embeds.help_embed_command(item_view))
            return

        error = embeds.command_error_embed(ctx.command.name, 'Invalid option!',
                                           "Please select a valid option `category` or `command`.")
        await ctx.send(embed=error)

    @commands.command(
        name="test",
        description="Test command!",
        usage="Unknown"
    )
    @checks.is_owner()
    async def test(self, ctx: Context, message_id: int) -> None:
        is_react = queries.get_react_message(message_id, ctx.guild.id) is not None
        await ctx.reply(f"The message `{message_id}` in guild `{ctx.guild.id}` is {'' if is_react else 'not '}"
                        f"a reactionary message")


def setup(bot):
    bot.add_cog(Utilities(bot))
