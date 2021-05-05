from collections import defaultdict
import re
from typing import List
from PoEQuery.official_api_result import Mod

from PoEStats.ggpk_stats import GGPKStatTranslation, domain_to_translation
from PoEStats.trade_stats import stats, option_stats
from PoEStats.re_strings import re_hashtag_pattern, re_insert_pattern

import logging

###
# pre_cache a bunch of translation tools
###

from RePoE import mods


def create_mod_stats_lookup():
    stat_id_set_to_mod_names = defaultdict(list)
    for name, mod in mods.items():
        ids = frozenset({stat["id"] for stat in mod["stats"]})
        stat_id_set_to_mod_names[ids].append(name)
    return stat_id_set_to_mod_names


def create_stats_split_lookup():
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
    return stats_split


def create_ggpk_stats_split_lookup():
    ggpk_stats_split = defaultdict(list)

    all_stat_translations = {
        stat_translation
        for stat_translations in domain_to_translation.values()
        for stat_translation in stat_translations
    }
    for parsed in all_stat_translations:

        for formatter in parsed.formatters:
            split_string = tuple(re.split(re_insert_pattern, formatter.string))
            ggpk_stats_split[split_string].append(
                GGPKStatTranslation(ids=parsed.ids, formatters=tuple([formatter])),
            )
    return ggpk_stats_split


stats_split = create_stats_split_lookup()
ggpk_stats_split = create_ggpk_stats_split_lookup()
stat_id_set_to_mod_names = create_mod_stats_lookup()

for key, value in stats_split.items():
    if "pseudo" not in key and "veiled" not in key:
        if not value in ggpk_stats_split:
            logging.warn(
                f"stat translation not found in ggpk : {value}, {key in option_stats}"
            )


def mod_to_ggpk(
    mod: Mod,
) -> List[GGPKStatTranslation]:
    """
    GET:
    stat "explicit.stat_3102860761" = "#% increased Movement Speed for # seconds on Throwing a Trap"
    (min, max) values for stat
    """
    possible_mod_names = []
    hash_to_min_max_tuples = defaultdict(list)

    for magnitude in mod.magnitudes:
        hash_to_min_max_tuples[magnitude.hash_].append((magnitude.min_, magnitude.max_))

    # for each extended mod stat...
    for hash, min_max_tuples in hash_to_min_max_tuples.items():
        stat_translations = ggpk_stats_split[stats_split[hash]]
        breakpoint()
        # for each possible stat translation...
        for stat_translation in {
            stat_translation
            for stat_translation in stat_translations
            if len(stat_translation.ids) == len(min_max_tuples)
        }:
            # find the min and max from reversing the handlers...
            for formatter in stat_translation.formatters:
                id_to_stat_range = {}
                for id, index_handler, (min, max) in zip(
                    stat_translation.ids, formatter.index_handlers, min_max_tuples
                ):
                    for handler in index_handler:
                        min, max = (
                            handler.reverse_handler(min),
                            handler.reverse_handler(max),
                        )
                    id_to_stat_range[id] = (min, max)

                # check all possible mods which have the same stat ids...
                for mod_name in stat_id_set_to_mod_names[
                    frozenset(stat_translation.ids)
                ]:
                    mod = mods[mod_name]
                    for stat in mod["stats"]:
                        if (
                            stat["min"] != id_to_stat_range[stat["id"]][0]
                            or stat["max"] != id_to_stat_range[stat["id"]][1]
                        ):
                            break
                    else:
                        possible_mod_names.append(mod_name)
    return possible_mod_names


if __name__ == "__main__":

    import json

    mod = Mod(
        json.loads(
            '{"name": "of the Miser", "tier": "S3", "magnitudes": [{"hash": "explicit.stat_1471729472", "min": 5, "max": 7}]}'
        )
    )
    print(mod_to_ggpk(mod))
