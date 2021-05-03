from dataclasses import dataclass
from typing import Callable, ClassVar


@dataclass(unsafe_hash=True)
class IndexHandler:
    id: str
    handler: Callable[[int], float] = lambda _: NotImplemented
    reverse_handler: Callable[[float], int] = lambda _: NotImplemented

    _id_to_quantifier: ClassVar[dict] = {}

    def __post_init__(self):
        self._id_to_quantifier[self.id] = self

    @classmethod
    def from_id(cls, id: str):
        try:
            return cls._id_to_quantifier[id]
        except KeyError:
            raise KeyError(f"Please register TranslationQuantifier for {id}")


IndexHandler(
    id="30%_of_value",
    handler=lambda v: v * 0.3,
    reverse_handler=lambda v: v / 0.3,
)

IndexHandler(
    id="60%_of_value",
    handler=lambda v: v * 0.6,
    reverse_handler=lambda v: v / 0.6,
)

IndexHandler(
    id="deciseconds_to_seconds",
    handler=lambda v: v / 10,
    reverse_handler=lambda v: float(v) * 10,
)

IndexHandler(
    id="divide_by_three",
    handler=lambda v: v / 3,
    reverse_handler=lambda v: float(v) * 3,
)

IndexHandler(
    id="divide_by_five",
    handler=lambda v: v / 5,
    reverse_handler=lambda v: float(v) * 5,
)

IndexHandler(
    id="divide_by_one_hundred",
    handler=lambda v: v / 100,
    reverse_handler=lambda v: float(v) * 100,
)

IndexHandler(
    id="divide_by_one_hundred_and_negate",
    handler=lambda v: -v / 100,
    reverse_handler=lambda v: -float(v) * 100,
)

IndexHandler(
    id="divide_by_one_hundred_2dp",
    handler=lambda v: round(v / 100, 2),
    reverse_handler=lambda v: float(v) * 100,
)

IndexHandler(
    id="divide_by_two_0dp",
    handler=lambda v: v // 2,
    reverse_handler=lambda v: int(v) * 2,
)

IndexHandler(
    id="divide_by_six",
    handler=lambda v: v / 6,
    reverse_handler=lambda v: int(v) * 6,
)

IndexHandler(
    id="divide_by_ten_0dp",
    handler=lambda v: v // 10,
    reverse_handler=lambda v: int(v) * 10,
)

IndexHandler(
    id="divide_by_twelve",
    handler=lambda v: v / 12,
    reverse_handler=lambda v: int(v) * 12,
)

IndexHandler(
    id="divide_by_fifteen_0dp",
    handler=lambda v: v // 15,
    reverse_handler=lambda v: int(v) * 15,
)

IndexHandler(
    id="divide_by_twenty_then_double_0dp",
    handler=lambda v: v // 20 * 2,
    reverse_handler=lambda v: int(v) * 20 // 2,
)

IndexHandler(
    id="milliseconds_to_seconds",
    handler=lambda v: v / 1000,
    reverse_handler=lambda v: float(v) * 1000,
)

IndexHandler(
    id="milliseconds_to_seconds_0dp",
    handler=lambda v: int(round(v / 1000, 0)),
    reverse_handler=lambda v: float(v) * 1000,
)
IndexHandler(
    id="milliseconds_to_seconds_1dp",
    handler=lambda v: round(v / 1000, 1),
    reverse_handler=lambda v: float(v) * 1000,
)

IndexHandler(
    id="milliseconds_to_seconds_2dp",
    handler=lambda v: round(v / 1000, 2),
    reverse_handler=lambda v: float(v) * 1000,
)

# TODO: Not exactly sure yet how this one works
IndexHandler(
    id="milliseconds_to_seconds_2dp_if_required",
    handler=lambda v: round(v / 1000, 2),
    reverse_handler=lambda v: float(v) * 1000,
)

IndexHandler(
    id="multiplicative_damage_modifier",
    handler=lambda v: v + 100,
    reverse_handler=lambda v: float(v) - 100,
)

IndexHandler(
    id="multiplicative_permyriad_damage_modifier",
    handler=lambda v: v / 100 + 100,
    reverse_handler=lambda v: (float(v) - 100) * 100,
)

IndexHandler(
    id="multiply_by_four",
    handler=lambda v: v * 4,
    reverse_handler=lambda v: int(v) // 4,
)

IndexHandler(
    id="negate",
    handler=lambda v: -v,
    reverse_handler=lambda v: -float(v),
)

IndexHandler(
    id="old_leech_percent",
    handler=lambda v: v / 5,
    reverse_handler=lambda v: float(v) * 5,
)

IndexHandler(
    id="old_leech_permyriad",
    handler=lambda v: v / 500,
    reverse_handler=lambda v: float(v) * 500,
)

IndexHandler(
    id="per_minute_to_per_second",
    handler=lambda v: round(v / 60, 1),
    reverse_handler=lambda v: float(v) * 60,
)

IndexHandler(
    id="per_minute_to_per_second_0dp",
    handler=lambda v: int(round(v / 60, 0)),
    reverse_handler=lambda v: float(v) * 60,
)

IndexHandler(
    id="per_minute_to_per_second_1dp",
    handler=lambda v: round(v / 60, 1),
    reverse_handler=lambda v: float(v) * 60,
)

IndexHandler(
    id="per_minute_to_per_second_2dp",
    handler=lambda v: round(v / 60, 2),
    reverse_handler=lambda v: float(v) * 60,
)

IndexHandler(
    id="per_minute_to_per_second_2dp_if_required",
    handler=lambda v: round(v / 60, 2) if v % 60 != 0 else v // 60,
    reverse_handler=lambda v: float(v) * 60,
)

IndexHandler(
    id="times_twenty",
    handler=lambda v: v * 20,
    reverse_handler=lambda v: int(v) // 20,
)

IndexHandler(
    id="canonical_line",
)

IndexHandler(
    id="canonical_stat",
)

# These will be replaced by install_data_dependant_quantifiers
IndexHandler(
    id="mod_value_to_item_class",
)

IndexHandler(
    id="tempest_mod_text",
)

IndexHandler(
    id="display_indexable_support",
)

IndexHandler(
    id="tree_expansion_jewel_passive",
)

IndexHandler(
    id="affliction_reward_type",
)

IndexHandler(
    id="passive_hash",
)

IndexHandler(
    id="reminderstring",
)
