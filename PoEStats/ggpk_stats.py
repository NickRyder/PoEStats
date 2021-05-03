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
    condition: Tuple[StatRange]
    format: Tuple[StatFormat]
    index_handlers: Tuple[List[IndexHandler]]
    string: str

    def __init__(self, json):
        self.condition = tuple(
            [StatRange(condition) for condition in json["condition"]]
        )
        self.format = tuple([StatFormat(format) for format in json["format"]])
        self.index_handlers = tuple(
            [
                tuple([IndexHandler.from_id(handler) for handler in handlers])
                for handlers in json["index_handlers"]
            ]
        )
        self.string = json["string"]

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

    @classmethod
    def load(cls, json: dict):
        return cls(
            ids=tuple(json["ids"]),
            formatters=tuple(
                [StatFormatter(stat_formatter) for stat_formatter in json["English"]]
            ),
        )

    def translate(self, id_to_value_dict: Dict[str, int]):
        values = [id_to_value_dict.get(id, 0) for id in self.ids]

        if all([value == 0 for value in values]):
            raise FormatterError("No ids from this translation")

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


# grab both the main stat_translations and the sub_stat_translations
stat_translations = list(
    {GGPKStatTranslation.load(v) for v in stat_translations_json}
    # | {
    #     GGPKStatTranslation.load(v)
    #     for sub_translations in sub_stat_translations.values()
    #     for v in sub_translations
    # }
)

stat_id_to_stat_translation: Dict[str, GGPKStatTranslation] = {}

for stat_translation in stat_translations:
    for id in stat_translation.ids:
        assert id not in stat_id_to_stat_translation
        stat_id_to_stat_translation[id] = stat_translation


if __name__ == "__main__":
    from RePoE import mods
    import logging

    for mod in mods.values():
        print("")
        mod_id_values = {stat["id"]: stat["min"] for stat in mod["stats"]}
        lines = 0
        while mod_id_values:
            id = next(iter(mod_id_values.keys()))
            if id in stat_id_to_stat_translation:
                stat_translation = stat_id_to_stat_translation[id]
                print(stat_translation.translate(mod_id_values))
                lines += 1
                for id in stat_translation.ids:
                    if id in mod_id_values:
                        del mod_id_values[id]
            else:
                logging.warn(f"Found no stat translation for {id}")
                del mod_id_values[id]
        if lines > 1:
            breakpoint()
