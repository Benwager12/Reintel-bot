import time

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


def convert_unix_now(): return convert_unix(int(time.time()))


class _CachedItems:
    def __init__(self):
        self.command_info = None
        self.categories_desc = None

    def get_command_info(self):
        return self.command_info

    def set_command_info(self, new_command_info):
        self.command_info = new_command_info

    def get_categories_desc(self):
        return self.categories_desc

    def set_categories_desc(self, new_categories_desc):
        self.categories_desc = new_categories_desc


CachedItems = _CachedItems()


def categories_description(cogs):
    if CachedItems.get_categories_desc() is not None:
        return CachedItems.get_categories_desc()

    items = {cat[:-len('-normal')]: cogs[cat].description for cat in list(cogs.keys()) if cat.endswith("-normal")}
    CachedItems.set_categories_desc(items)
    return items


def command_info(cogs) -> dict:
    if CachedItems.get_command_info() is not None:
        return CachedItems.get_command_info()

    items = dict()
    for cat in list(cogs.keys()):
        if cat.endswith("-normal"):
            items[cat] = dict()
            for cmd in cogs[cat].walk_commands():
                items[cat][cmd.name] = {"description": cmd.description, "aliases": cmd.aliases, "usage": cmd.usage}

    CachedItems.set_command_info(items)
    return items


def command_info_str(command_name: str, cmd_info: dict) -> str:
    info = f"**Command: **{command_name}"
    info += f"\n**Description: **{cmd_info['description']}"
    info += f"\n**Usage: **{cmd_info['usage']}"
    if len(cmd_info['aliases']) > 0:
        info += f"\n**Aliases: **{', '.join(cmd_info['aliases'])}"

    return info
