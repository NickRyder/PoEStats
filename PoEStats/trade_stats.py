import re
from PoEStats.re_strings import re_hashtag_pattern
import requests
from dataclasses import dataclass
from typing import Optional, Tuple


def stats_from_web():
    _STATS_URL = "https://www.pathofexile.com/api/trade/data/stats"
    return requests.get(
        _STATS_URL,
        headers={
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0"
        },
    ).json()


option_stats = {
    mod_dict["id"]: mod_dict["text"]
    for stat_dict in stats_from_web()["result"]
    for mod_dict in stat_dict["entries"]
    if "option" in mod_dict
}

stats = {
    mod_dict["id"]: mod_dict["text"]
    for stat_dict in stats_from_web()["result"]
    for mod_dict in stat_dict["entries"]
}

stats["explicit.stat_2120904498"] = "# to Level of all Raise Skeleton Gems"
stats["implicit.stat_125218179"] = "# to maximum number of Spectres"
stats["crafted.stat_125218179"] = "# to maximum number of Spectres"
stats["implicit.stat_2428829184"] = "# to maximum number of Skeletons"


stats[
    "explicit.stat_3102860761"
] = "#% increased Movement Speed for # seconds on Throwing a Trap"
stats[
    "explicit.stat_723388324"
] = "#% chance to Trigger Socketed Spells when\nyou Spend at least # Mana to Use a Skill"


@dataclass
class ExtendedStatRange:
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class ExtendedStatTranslation:
    stat_id: str
    values: Tuple[ExtendedStatRange, ...]


# matched_strings = set()
# for parsed in stats.values():
#     match_result = re.findall("(.?\#.?)", parsed)
#     if match_result is not None:
#         for string in set(match_result):
#             if string not in matched_strings:
#                 print(parsed)
#         matched_strings |= set(match_result)
# print(matched_strings)