from typing import NamedTuple
from typing import final


@final
class ArrayType(NamedTuple):
    type_: type
    length: int | str  # Fixed length or variable name.
