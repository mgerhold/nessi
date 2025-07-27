from abc import ABC
from abc import abstractmethod
from typing import final


class Statement(ABC):
    def __init__(self, *, hidden_in_latex: bool) -> None:
        self._hidden_in_latex = hidden_in_latex

    @final
    @property
    def hidden_in_latex(self) -> bool:
        return self._hidden_in_latex

    @final
    def accept[T](self, visitor: "StatementVisitor[T]") -> T:
        return visitor.visit(self)

    @abstractmethod
    def __str__(self) -> str:
        pass


class StatementVisitor[T](ABC):
    @abstractmethod
    def visit(self, statement: Statement) -> T:
        pass
