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


def categories_description(cogs): return {cat[:-len('-normal')]: cogs[cat].description for cat in list(cogs.keys())
                                          if cat.endswith("-normal")}

