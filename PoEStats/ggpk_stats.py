from PoEStats.index_handlers import IndexHandler
from typing import Dict, List, Optional, Tuple
from RePoE import stat_translations as stat_translations_json
from RePoE.stat_translations import stat_translations as sub_stat_translations
from dataclasses import dataclass
from enum import Enum


@dataclass(unsafe_hash=True)
class StatRange:
    min: Optional[int] = None
    max: Optional[int] = None
    negated: Optional[bool] = False

    def __init__(self, json):
        self.min = json.get("min")
        self.max = json.get("max")
        self.negated = json.get("negated", False)

    def value_in_range(self, value: int) -> bool:
        """
        determine if value is in the range represented by self
        if so return True, else False
        """
        if self.min is not None and value < self.min:
            membership = False
        elif self.max is not None and value > self.max:
            membership = False
        else:
            membership = True

        if self.negated:
            return ~membership
        else:
            return membership


class StatFormat(Enum):
    NUMBER = "#"
    SIGNED_NUMBER = "+#"
    IGNORE = "ignore"

    def value_to_string(self, value: float) -> Optional[str]:
        if self == StatFormat.NUMBER:
            return str(value)
        elif self == StatFormat.SIGNED_NUMBER:
            if value > 0:
                sign = "+"
            elif value < 0:
                sign = "-"
            else:
                sign = ""
            return sign + str(value)
        elif self == StatFormat.IGNORE:
            return None


class FormatterError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message):
        # self.expression = expression
        self.message = message


@dataclass(unsafe_hash=True)
class StatFormatter:
    condition: Tuple[StatRange] = tuple()
    format: Tuple[StatFormat] = tuple()
    index_handlers: Tuple[Tuple[IndexHandler]] = tuple()
    string: str = ""

    @classmethod
    def load(cls, json):
        return StatFormatter(
            condition=tuple([StatRange(condition) for condition in json["condition"]]),
            format=tuple([StatFormat(format) for format in json["format"]]),
            index_handlers=tuple(
                [
                    tuple([IndexHandler.from_id(handler) for handler in handlers])
                    for handlers in json["index_handlers"]
                ]
            ),
            string=json["string"],
        )

    def values_to_string(self, values: Tuple[float]):
        formatted_strings = []
        for value, condition, format, index_handlers in zip(
            values, self.condition, self.format, self.index_handlers
        ):
            if not condition.value_in_range(value):
                raise FormatterError(f"Value {value} not in range {condition}")

            for index_handler in index_handlers:
                value = index_handler.handler(value)

            formatted_strings.append(format.value_to_string(value))

        translated_string = self.string
        for idx, formatted_string in enumerate(formatted_strings):
            if formatted_string is None:
                assert f"{{{idx}}}" not in translated_string
            else:
                translated_string = translated_string.replace(
                    f"{{{idx}}}", formatted_string
                )
        return translated_string


@dataclass(unsafe_hash=True)
class GGPKStatTranslation:
    ids: Tuple[str]
    formatters: Tuple[StatFormatter]
    hidden: bool = False

    @classmethod
    def load(cls, json: dict):
        return cls(
            ids=tuple(json["ids"]),
            formatters=tuple(
                [
                    StatFormatter.load(stat_formatter)
                    for stat_formatter in json["English"]
                ]
            ),
            hidden=json.get("hidden", False),
        )

    def translate(self, id_to_value_dict: Dict[str, int]) -> Optional[str]:
        if self.hidden:
            return None
        values = [id_to_value_dict.get(id, 0) for id in self.ids]

        if all([value == 0 for value in values]):
            raise ValueError("Translating with all zero values")

        for formatter in self.formatters:
            try:
                return formatter.values_to_string(values)
            except FormatterError:
                pass
        raise FormatterError(f"No formatters fit values {id_to_value_dict}")

    def reverse_translate(
        self,
    ):
        pass


stats_with_no_translation = set()

all_translatable_stats = set()


class StatTranslations(list):
    def __init__(self, stat_translations_json: List[dict]):
        super().__init__([GGPKStatTranslation.load(v) for v in stat_translations_json])

        self._stat_id_to_stat_translation = {}
        for stat_translation in self:
            for id in stat_translation.ids:
                assert id not in self._stat_id_to_stat_translation
                self._stat_id_to_stat_translation[id] = stat_translation

    def from_id(self, id: str) -> GGPKStatTranslation:
        if id not in self._stat_id_to_stat_translation:
            stats_with_no_translation.add(id)
            # if id in all_translatable_stats:
            #     print(id)
            #     breakpoint()
            # assert id not in all_translatable_stats, id
            # if id in WHITELIST:
            return GGPKStatTranslation(
                (id,), formatters=(StatFormatter(),), hidden=True
            )
        return self._stat_id_to_stat_translation[id]


# grab both the main stat_translations and the sub_stat_translations

stat_translations = StatTranslations(stat_translations_json)
stat_translations_atlas = StatTranslations(sub_stat_translations["atlas"])
stat_translations_areas = StatTranslations(sub_stat_translations["areas"])

all_translatable_stats = {
    id for stat_translation in stat_translations_json for id in stat_translation["ids"]
} | {
    id
    for _stat_translations in sub_stat_translations.values()
    for stat_translation in _stat_translations
    for id in stat_translation["ids"]
}

domain_to_translation = {
    "affliction_jewel": stat_translations,
    "delve": stat_translations_areas,
    "flask": stat_translations,
    "misc": stat_translations,
    "atlas": stat_translations_atlas,
    "crafted": stat_translations,
    "abyss_jewel": stat_translations,
    "watchstone": stat_translations,
    "item": stat_translations,
    "area": stat_translations_areas,
}


def translate_mod(mod: dict):
    item_stat_translation = domain_to_translation[mod["domain"]]
    mod_id_values = {
        stat["id"]: stat["min"] for stat in mod["stats"] if stat["min"] != 0
    }
    while mod_id_values:
        id = next(iter(mod_id_values.keys()))
        stat_translation = item_stat_translation.from_id(id)
        print(stat_translation.translate(mod_id_values))
        for id in stat_translation.ids:
            if id in mod_id_values:
                del mod_id_values[id]


if __name__ == "__main__":
    from RePoE import mods
    from pprint import pprint

    for name, mod in mods.items():
        print("")
        try:
            if name not in ["LocalPhysicalDamageAddedAsEachElementTransformed"]:
                translate_mod(mod)
        except Exception as e:
            print(name)
            pprint(mod)
            raise e

    NotImplemented
    # todo analyze stats_with_no_translation
    # make sure they dont show up in sub stat translations

    # later todo: make ranges display in translate
    # later todo: allow reverse translation
