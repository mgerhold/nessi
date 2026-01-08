import re
from typing import final
from typing import override

from nessi.value import Value


@final
class InterpolatedString:
    _PATTERN = re.compile(r"\{(?P<key>[A-Za-z_]\w*)(?:\[(?P<index>[^]]+)])?}")

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    @override
    def __str__(self) -> str:
        return f"InterpolatedString({self._text})"

    def interpolate(self, values: dict[str, Value]) -> str:
        # Supports:
        #   {key}
        #   {key[index]}  -> detected, but not implemented yet
        result_parts: list[str] = []
        last = 0

        for match_ in InterpolatedString._PATTERN.finditer(self._text):
            result_parts.append(self._text[last : match_.start()])
            last = match_.end()

            key = match_.group("key")
            index = match_.group("index")

            if key not in values:
                # Unknown placeholder -> leave unchanged.
                result_parts.append(match_.group(0))
                continue

            value = values[key]
            if index is not None:
                if index not in values:
                    # Unknown index -> leave unchanged.
                    result_parts.append(match_.group(0))
                    continue
                index_value = values[index]
                if not isinstance(value, list):
                    raise TypeError(f"Value for key '{key}' is not a list.")
                if not isinstance(index_value, int):
                    raise TypeError(f"Index value for key '{index}' is not an integer.")
                try:
                    value = value[index_value]
                except IndexError:
                    raise IndexError(f"Index {index_value} out of range for key '{key}'.")

            result_parts.append(str(value))

        result_parts.append(self._text[last:])
        return "".join(result_parts)
