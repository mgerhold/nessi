from abc import ABC, abstractmethod
from enum import Enum
from typing import Final, final, override

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
        return rf"\texttt{{{self._name}}}"

    @override
    def __str__(self) -> str:
        return f"Variable({self._name})"


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
