import re

import disnake
import emoji
from disnake.ext import commands

from helpers import embeds, queries


class Reactionary(commands.Cog, name="reactionary-normal", description=":arrow_up: Create reactionaries, messages that "
                                                                       "allow users to reply and get roles"):
    def __init__(self, bot: commands.bot.Bot):
        self.bot = bot

    @commands.command(
        name="add_reaction",
        description="Create a reactionary message",
        aliases=["react"],
        usage="add_reaction <message_id> <reaction_emoji> <role>"
    )
    async def add_reaction(self, ctx: commands.Context, message_id: str, reaction_emoji: str = None,
                           role: disnake.Role = None):
        """"
        Create a reactionary message
        :param ctx: The context for the command
        :param message_id: The message ID to react to
        :param reaction_emoji: The emoji to react with
        :param role: The role to give to the user
        """
        if ctx.author.guild_permissions.manage_roles is False:
            await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "No permission",
                                                            "You don't have permission to use this command!"))
            return

        if message_id.isnumeric():
            message_id = int(message_id)
        else:
            return await ctx.send(embed=embeds.command_error_embed(ctx.command.name, 'Invalid message ID!',
                                                                   "Please enter a valid message ID."))

        if message_id is None:
            await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "No message ID",
                                                            "Please provide a message ID!"))
            return

        message = await ctx.channel.fetch_message(message_id)
        if message is None:
            await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "No message", "Message not found!"))
            return

        if ctx.author.id != message.author.id:
            await ctx.send("You can't react to someone else's message!")
            return

        if reaction_emoji is None:
            await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "Invalid usage",
                                                            "Please provide a reaction emoji!"))
            return

        emoji_unicode = True

        if not emoji.is_emoji(reaction_emoji):
            match = re.match("<:(.*):(\\d*)>", reaction_emoji)
            if match is None:
                await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "Invalid usage",
                                                                "Please provide a valid emoji!"))
                return
            reaction_emoji = match
            emoji_unicode = False

        if role is None:
            await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "Invalid usage",
                                                            "Please provide a role!"))
            return

        print(ctx.guild.owner_id)
        if ctx.author.top_role.position < role.position and ctx.author.id != ctx.guild.owner_id:
            await ctx.send(embed=embeds.command_error_embed(ctx.command.name, "No permission",
                                                            "That role is higher than yours in the hierarchy."))
            return

        if not emoji_unicode:
            reaction_emoji = reaction_emoji.group(2)

        queries.add_react(ctx.author.id, message_id, reaction_emoji, role.id, ctx.guild.id)
        await message.add_reaction(reaction_emoji)


def setup(bot):
    bot.add_cog(Reactionary(bot))
