from collections import defaultdict
import re
from typing import List
from PoEStats.ggpk_stats import GGPKStatTranslation, stat_translations_parsed
from PoEStats.trade_stats import ExtendedStatTranslation, stats, option_stats
from PoEStats.re_strings import re_hashtag_pattern, re_insert_pattern

###
# pre_cache a bunch of translation tools
###

# remove things like (Local) (Shields) (Maps) from the end of stats
modified_stats = {k: re.split(r".*\(.+\)", v)[0] for k, v in stats.items()}

stats_split = {}
for stat_id, stat_string in modified_stats.items():
    split_string = tuple(re.split(re_hashtag_pattern, stat_string))
    # confirm that no two distinct stat_strings split into the same split_string
    assert all(
        [
            modified_stats[k] == stat_string
            for k, v in stats_split.items()
            if v == split_string
        ]
    )
    stats_split[stat_id] = split_string

ggpk_stats_split = defaultdict(list)
for parsed in stat_translations_parsed:
    for formatter_idx, formatter in enumerate(parsed.formatters):
        split_string = tuple(re.split(re_insert_pattern, formatter.string))
        ggpk_stats_split[split_string].append((formatter_idx, parsed))

for key, value in stats_split.items():
    if "pseudo" not in key and "veiled" not in key:
        if not value in ggpk_stats_split:
            print(value, key in option_stats)


def extended_to_ggpk(
    extended_stat_translation: ExtendedStatTranslation,
) -> List[GGPKStatTranslation]:
    """
    GET:
    stat "explicit.stat_3102860761" = "#% increased Movement Speed for # seconds on Throwing a Trap"
    (min, max) values for stat
    """
