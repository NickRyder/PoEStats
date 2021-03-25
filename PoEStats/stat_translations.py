from typing import List, Optional
from RePoE import stat_translations
from dataclasses import dataclass
from enum import Enum
import re
from PoEStats.re_strings import re_insert_group_pattern


@dataclass
class StatRange():
    min: Optional[int] = None
    max: Optional[int] = None
    negated: Optional[bool] = False
    
    def __init__(self, json):

        self.min = json.get("min")
        self.max = json.get("max")
        self.negated = json.get("negated", False)


class StatFormat(Enum):
    NUMBER = "#"
    SIGNED_NUMBER = "+#"
    IGNORE = "ignore"

class StatHandler(Enum):
    per_minute_to_per_second = 'per_minute_to_per_second'
    divide_by_one_hundred = 'divide_by_one_hundred'
    milliseconds_to_seconds = 'milliseconds_to_seconds'
    multiply_by_four = 'multiply_by_four'
    milliseconds_to_seconds_1dp = 'milliseconds_to_seconds_1dp'
    divide_by_ten_0dp = 'divide_by_ten_0dp'
    mod_value_to_item_class = 'mod_value_to_item_class'
    divide_by_one_hundred_and_negate = 'divide_by_one_hundred_and_negate'
    divide_by_twelve = 'divide_by_twelve'
    times_twenty = 'times_twenty'
    canonical_stat = 'canonical_stat'
    sixty_percent_of_value = '60%_of_value'
    divide_by_six = 'divide_by_six'
    divide_by_three = 'divide_by_three'
    divide_by_two_0dp = 'divide_by_two_0dp'
    divide_by_five = 'divide_by_five'
    per_minute_to_per_second_0dp = 'per_minute_to_per_second_0dp'
    per_minute_to_per_second_2dp = 'per_minute_to_per_second_2dp'
    thirty_percent_of_value = '30%_of_value'
    milliseconds_to_seconds_0dp = 'milliseconds_to_seconds_0dp'
    per_minute_to_per_second_2dp_if_required = 'per_minute_to_per_second_2dp_if_required'
    negate = 'negate'
    old_leech_permyriad = 'old_leech_permyriad'
    per_minute_to_per_second_1dp = 'per_minute_to_per_second_1dp'
    old_leech_percent = 'old_leech_percent'
    milliseconds_to_seconds_2dp = 'milliseconds_to_seconds_2dp'
    divide_by_twenty_then_double_0dp = 'divide_by_twenty_then_double_0dp'
    divide_by_fifteen_0dp = 'divide_by_fifteen_0dp'
    divide_by_one_hundred_2dp = 'divide_by_one_hundred_2dp'
    deciseconds_to_seconds = 'deciseconds_to_seconds'


@dataclass
class StatFormatter():
    condition: List[StatRange]
    format: List[str]
    index_handlers: List[List[str]]
    string: str

    def __init__(self, json):
        self.condition = [StatRange(condition) for condition in json["condition"]]
        self.format = [StatFormat(format) for format in json["format"]]
        self.index_handlers = [[StatHandler(handler) for handler in handlers] for handlers in json["index_handlers"]]
        self.string = json["string"]

@dataclass
class StatTranslation():
    ids : List[str]
    formatters: List[StatFormatter]

    def __init__(self, json):
        self.ids = json["ids"]
        self.formatters = [StatFormatter(stat_formatter) for stat_formatter in json["English"]]

stat_translations_parsed = [StatTranslation(v) for v in stat_translations]

for v in stat_translations_parsed:
    for formatter in v.formatters:
        print(re.split(re_insert_group_pattern, formatter.string))  