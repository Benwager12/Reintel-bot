"""
During the creation of this bot, I made use of @kkrypt0nn's Python-Discord-Bot-Template.
Thank you very much for the great bot template!
"""


import disnake
import emoji.core
from disnake.ext.commands import Bot
from disnake import ApplicationCommandInteraction
from disnake.ext import tasks, commands
from helpers import utilities, queries
from helpers import config

import os
import exceptions

intents = disnake.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True


bot = Bot(
    command_prefix=commands.when_mentioned_or(config.config["PREFIX"]),
    intents=intents,
    config=config.config,
    help_command=None
)


@bot.event
async def on_ready():
    print("-" * 20)
    print(f'Logged in as {bot.user.display_name} ({bot.user.id})')
    print(f"Is production: {'Yes' if config.is_prod else 'No'}")

    print("\nRegistering commands:")
    load_commands()

    print("\nLoaded cache")
    utilities.load_cache(bot.cogs)
    print("-" * 20)
    
    presence = "with lists." if config.is_prod else "with code."
    await bot.change_presence(activity=disnake.Game(name=presence))


@bot.event
async def on_raw_reaction_add(payload: disnake.RawReactionActionEvent) -> None:
    await utilities.role_from_reaction(payload, bot)


@bot.event
async def on_raw_reaction_remove(payload: disnake.RawReactionActionEvent) -> None:
    await utilities.role_from_reaction(payload, bot)


@bot.event
async def on_raw_message_delete(payload: disnake.RawMessageDeleteEvent) -> None:
    emojis = queries.delete_reactionary(payload.message_id, payload.guild_id)
    queries.delete_emojis(emojis)


@tasks.loop(seconds=5)
async def check_timers():
    print('Checking timers...')


def load_commands() -> None:
    for ctype in ["normal"]:
        for file in os.listdir(f"./commands/{ctype}"):
            if file.endswith(".py"):
                bot.load_extension(f"commands.{ctype}.{file[:-3]}")
                print(f"Registered {ctype} category {file.split('-')[0]}")


@bot.event
async def on_slash_command(interaction: ApplicationCommandInteraction) -> None:
    print(f"Executed {interaction.data.name} command in {interaction.guild.name} (ID: {interaction.guild.id}) by "
          f"{interaction.author} (ID: {interaction.author.id})")


@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception) -> None:
    """
    The code in this event is executed every time a valid slash command catches an error
    :param interaction: The slash command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.is_owner() check in your command, or you can raise the error by yourself.

        'hidden=True' will make so that only the user who execute the command can see the message
        """
        embed = disnake.Embed(
            title="Error!",
            description="You are blacklisted from using the bot.",
            color=0xE02B2B
        )
        print("A blacklisted user tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.errors.MissingPermissions):
        embed = disnake.Embed(
            title="Error!",
            description="You are missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to execute this command!",
            color=0xE02B2B
        )
        print("A blacklisted user tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    raise error

bot.run(config.config['DISCORD_TOKEN'])
