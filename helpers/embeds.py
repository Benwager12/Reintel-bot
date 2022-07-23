import disnake
from disnake import Member, Embed
from disnake.ext.commands.bot import Bot

from helpers import utilities, queries, config
from commands.normal import *

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
        formatting = utilities.number_emoji(x + 1) + ". "
        formatting += f"~~{todo[0]}~~" if crossed is True or crossed == x + 1 else todo[0]
        formatting += f" ({utilities.convert_unix(todo[1])})"

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


def bot_information_embed() -> disnake.Embed:
    embed = disnake.Embed(
        color=disnake.Color.green(),

        description="This is a bot made by Ben Wager, it has started as a todo list bot, but after some time, I "
                    + "realised that it was a project I really enjoyed creating. Hopefully you enjoy it as much as I"
                    + "enjoyed creating it.\n\nMade with: Disnake (https://docs.disnake.dev/)\n\nInspiration from: "
                    + "Kaya Arkin / NingNangNongy (https://github.com/karkin2002)\n\nGithub page: "
                    + "https://github.com/Benwager12/Reintel-bot/\n\nProduction: " + ("Yes" if config.is_prod else "No")
    )

    embed.set_author(icon_url="https://avatars.githubusercontent.com/u/16391962?v=4", name="Bot Information")
    return embed


def help_embed_categories(cogs) -> disnake.Embed:
    categories = utilities.categories_description(cogs)

    description = "**Usage: **`help [category|command] <category name | command name>`\n\n"
    description += "\n\n".join(f"{cat.title()}: {categories[cat]}" for cat in categories)

    embed = disnake.Embed(
        color=disnake.Color.green(),
        description=description
    )
    embed.set_author(name="Help: Categories")
    return embed


def help_embed_category(cogs, category: str) -> disnake.Embed:
    if category is None:
        embed = disnake.Embed(
            color=disnake.Color.red(),
            description="**Usage: **`help [category|command] <category name | command name>`\n\n"
                        "Please specify a category."
        )
        embed.set_author(name="Help Category: Error")
        return embed

    if f"{category.lower()}-normal" not in cogs:
        embed = disnake.Embed(
            color=disnake.Color.red(),
            description="**Usage: **`help [category|command] <category name | command name>`\n\n"
                        f"The category `{category}` does not exist."
        )
        embed.set_author(name="Help Category: Error")
        return embed

    commands = utilities.command_info(cogs)[f"{category.lower()}-normal"]
    description = "\n\n".join(utilities.command_info_str(command, commands[command]) for command in commands)

    embed = disnake.Embed(
        color=disnake.Color.green(),
        description=description
    )
    embed.set_author(name=f"Help Category: {category.title()}")

    return embed


def help_embed_command(cogs, command: str) -> disnake.Embed:
    if command is None:
        embed = disnake.Embed(
            color=disnake.Color.red(),
            description="**Usage: **`help [category|command] <category name | command name>`\n\n"
                        "Please specify a command."
        )
        embed.set_author(name="Help Command: Error")
        return embed

    category = utilities.find_command_category(command.lower(), cogs)

    if category is None:
        embed = disnake.Embed(
            color=disnake.Color.red(),
            description="**Usage: **`help [category|command] <category name | command name>`\n\n"
                        f"The command `{command}` does not exist."
        )
        embed.set_author(name="Help Command: Error")
        return embed

    info = utilities.command_info_str(command.lower(), utilities.command_info(cogs)[f"{category}"][command.lower()])

    embed = disnake.Embed(
        color=disnake.Color.green(),
        description=info
    )
    embed.set_author(name=f"Help Command: {command.title()}")
    return embed
