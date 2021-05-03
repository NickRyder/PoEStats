from collections import defaultdict
import re
from typing import List
from PoEQuery.official_api_result import Mod

from PoEStats.ggpk_stats import GGPKStatTranslation, stat_translations_parsed
from PoEStats.trade_stats import stats, option_stats
from PoEStats.re_strings import re_hashtag_pattern, re_insert_pattern

import logging

###
# pre_cache a bunch of translation tools
###

# remove things like (Local) (Shields) (Maps) from the end of stats
modified_stats = {k: re.split(r" \(.+\)", v)[0] for k, v in stats.items()}

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

    split_string_to_formatters = defaultdict(list)

    for formatter in parsed.formatters:
        split_string = tuple(re.split(re_insert_pattern, formatter.string))
        # TODO: maybe dong want to split if a translator has multiple formatters
        # that work, instead perhaps need to make a new dataclass for split matches
        split_string_to_formatters[split_string].append(formatter)

    for split_string, formatters in split_string_to_formatters:

        ggpk_stats_split[split_string].append(
            GGPKStatTranslation(ids=parsed.ids, formatters=tuple(formatters)),
        )

for key, value in stats_split.items():
    if "pseudo" not in key and "veiled" not in key:
        if not value in ggpk_stats_split:
            logging.warn(
                f"stat translation not found in ggpk : ", value, key in option_stats
            )


def mod_to_ggpk(
    mod: Mod,
) -> List[GGPKStatTranslation]:
    """
    GET:
    stat "explicit.stat_3102860761" = "#% increased Movement Speed for # seconds on Throwing a Trap"
    (min, max) values for stat
    """
    hash_to_min_max_tuples = defaultdict(list)

    for magnitude in mod.magnitudes:
        hash_to_min_max_tuples[magnitude.hash_].append((magnitude.min_, magnitude.max_))

    for hash, min_max_tuples in hash_to_min_max_tuples.items():
        stat_translations = ggpk_stats_split[stats_split[hash]]
        for stat_translation in {
            stat_translation
            for stat_translation in stat_translations
            if len(stat_translation[1].ids) == len(min_max_tuples)
        }:
            for formatter in stat_translation.formatter:
                formatter

                breakpoint()


if __name__ == "__main__":

    import json

    mod = Mod(
        json.loads(
            '{"name": "Razor-sharp", "tier": "P3", "magnitudes": [{"hash": "explicit.stat_1940865751", "min": 14, "max": 19}, {"hash": "explicit.stat_1940865751", "min": 29, "max": 35}]}'
        )
    )
    mod_to_ggpk(mod)
