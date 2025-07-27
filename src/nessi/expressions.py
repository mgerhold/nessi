from abc import ABC
from abc import abstractmethod
from enum import Enum
from typing import Final
from typing import final
from typing import override

from nessi.context import Context
from nessi.value import Value


class Expression(ABC):
    @abstractmethod
    def evaluate(self, context: Context) -> Value:
        pass

    @abstractmethod
    def to_latex(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @final
    def __add__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.ADD, other)

    @final
    def __sub__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.SUBTRACT, other)

    @final
    def __mul__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.MULTIPLY, other)

    @final
    def __truediv__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.DIVIDE, other)

    @final
    def __floordiv__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.DIVIDE, other)

    @final
    def __mod__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.MODULUS, other)

    @final
    def __eq__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.EQUALS, other)

    @final
    def __ne__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.NOT_EQUALS, other)

    @final
    def __gt__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.GREATER_THAN, other)

    @final
    def __lt__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.LESS_THAN, other)

    @final
    def __ge__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.GREATER_THAN_OR_EQUAL, other)

    @final
    def __le__(self, other: "Expression") -> "Expression":
        return BinaryExpression(self, Operator.LESS_THAN_OR_EQUAL, other)


@final
class Operator(Enum):
    ADD = ("+", "+")
    SUBTRACT = ("-", "-")
    MULTIPLY = ("*", r"\cdot")
    DIVIDE = ("/", "/")
    MODULUS = ("MOD", r"\:\texttt{MOD}\:")
    GREATER_THAN = (">", ">")
    LESS_THAN = ("<", "<")
    EQUALS = ("==", "=")
    NOT_EQUALS = ("!=", r"\neq")
    GREATER_THAN_OR_EQUAL = (">=", r"\geq")
    LESS_THAN_OR_EQUAL = ("<=", r"\leq")


@final
class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: Operator, right: Expression) -> None:
        self._left = left
        self._operator = operator
        self._right = right

    @override
    def evaluate(self, context: Context) -> Value:
        left: Final = self._left.evaluate(context)
        right: Final = self._right.evaluate(context)
        if (
            (not isinstance(left, int) and not isinstance(left, float))
            or (not isinstance(right, int) and not isinstance(right, float))
            or (self._operator == Operator.MODULUS and not isinstance(left, int) and not isinstance(right, int))
        ):
            raise TypeError(f"Unsupported types for operation {self._operator}: {type(left)} and {type(right)}")
        match self._operator:
            # Arithmetic operators:
            case Operator.ADD:
                return left + right
            case Operator.SUBTRACT:
                return left - right
            case Operator.MULTIPLY:
                return left * right
            case Operator.DIVIDE:
                if isinstance(left, int) and isinstance(right, int):
                    return left // right
                return left / right
            case Operator.MODULUS:
                return left % right
            # Relative operators:
            case Operator.GREATER_THAN:
                return left > right
            case Operator.LESS_THAN:
                return left < right
            case Operator.EQUALS:
                return left == right
            case Operator.NOT_EQUALS:
                return left != right
            case Operator.GREATER_THAN_OR_EQUAL:
                return left >= right
            case Operator.LESS_THAN_OR_EQUAL:
                return left <= right
            case _:
                raise ValueError(f"Unsupported operator: {self._operator}")

    @override
    def to_latex(self) -> str:
        left: Final = self._left.to_latex()
        right: Final = self._right.to_latex()
        operator: Final = self._operator.value[1]
        return f"{left} {operator} {right}"

    @override
    def __str__(self) -> str:
        return f"({self._left} {self._operator.value} {self._right})"


@final
class Variable(Expression):
    def __init__(self, name: str) -> None:
        self._name = name

    @override
    def evaluate(self, context: Context) -> Value:
        value: Final = context.get(self._name)
        if value is None:
            raise KeyError(f"Variable '{self._name}' not found in context")
        return value

    @override
    def to_latex(self) -> str:
        return rf"\texttt{{{self._name.replace('_', r'\_')}}}"

    @override
    def __str__(self) -> str:
        return f"Variable({self._name})"

    def __getitem__(self, index: Expression) -> "ArrayElement":
        return ArrayElement(self._name, index)


@final
class Integer(Expression):
    def __init__(self, value: int) -> None:
        self._value = value

    @override
    def evaluate(self, context: Context) -> Value:
        return self._value

    @override
    def to_latex(self) -> str:
        return str(self._value)

    @override
    def __str__(self) -> str:
        return str(self._value)


@final
class Float(Expression):
    def __init__(self, value: float) -> None:
        self._value = value

    @override
    def evaluate(self, context: Context) -> Value:
        return self._value

    @override
    def to_latex(self) -> str:
        return str(self._value).replace(".", ",")

    @override
    def __str__(self) -> str:
        return str(self._value)


@final
class ArrayElement(Expression):
    def __init__(self, array_name: str, index: Expression) -> None:
        self._array_name = array_name
        self._index = index

    @override
    def evaluate(self, context: Context) -> Value:
        array: Final = context.get(self._array_name)
        if array is None or not isinstance(array, list):
            raise KeyError(f"Array '{self._array_name}' not found in context or is not a list")
        index_value: Final = self._index.evaluate(context)
        if not isinstance(index_value, int):
            raise TypeError(f"Index must be an integer, got {type(index_value)}")
        if index_value not in range(len(array)):
            raise IndexError(f"Index {index_value} out of bounds for array '{self._array_name}'")
        return array[index_value]

    @override
    def to_latex(self) -> str:
        index: Final = self._index.to_latex()
        return rf"\texttt{{{self._array_name.replace('_', r'\_')}}}[{index}]"

    @override
    def __str__(self) -> str:
        return f"{self._array_name}[{self._index}]"
