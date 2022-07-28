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


def categories_description(cogs=None):
    if cogs is None and CachedItems.get_categories_desc() is None:
        return None

    if CachedItems.get_categories_desc() is not None:
        return CachedItems.get_categories_desc()

    items = {cat[:-len('-normal')]: cogs[cat].description for cat in list(cogs.keys()) if cat.endswith("-normal")}
    CachedItems.set_categories_desc(items)
    return items


def command_info(cogs=None) -> dict | None:
    if cogs is None and CachedItems.get_command_info() is None:
        return None

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


def command_info_dict(command_name: str) -> dict | None:
    command_name = command_name.lower()

    category = find_command_category(command_name)
    info = CachedItems.get_command_info()[category][command_name]
    info['category'] = category
    info['name'] = command_name
    return info


def command_info_str(command_name: str) -> str | None:
    cmd_info = command_info_dict(command_name)
    info = f"**Command: **{cmd_info['name']}"
    info += f"\n**Description: **{cmd_info['description']}"
    info += f"\n**Usage: **`{cmd_info['usage']}`"
    if len(cmd_info['aliases']) > 0:
        info += f"\n**Aliases: **{', '.join(cmd_info['aliases'])}"

    return info


def find_command_category(command_name: str) -> str | None:
    for category in CachedItems.get_command_info():
        if command_name in CachedItems.get_command_info()[category]:
            return category
    return None


def command_usage_message(command_name: str) -> str | None:
    cmd_info = command_info_dict(command_name)
    if cmd_info is None:
        return None
    return f"**Usage: **`{cmd_info['usage']}`"


def command_categories() -> list:
    return list(CachedItems.get_command_info().keys())


def command_exists(command_name: str) -> bool:
    return find_command_category(command_name) is not None


def load_cache(cogs):
    CachedItems.set_command_info(command_info(cogs))
    CachedItems.set_categories_desc(categories_description(cogs))
