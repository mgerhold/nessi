from typing import final
from typing import override

from nessi.value import Value


@final
class InterpolatedString:
    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    @override
    def __str__(self) -> str:
        return f"InterpolatedString({self._text})"

    def interpolate(self, values: dict[str, Value]) -> str:
        result = self._text
        for key, value in values.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
