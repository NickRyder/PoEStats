from dataclasses import dataclass
from typing import Tuple


@dataclass
class PrimitiveStat:
    stat_pieces: Tuple[str]
    stat_numbers: Tuple[str]
