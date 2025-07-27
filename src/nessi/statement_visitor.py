from abc import ABC
from abc import abstractmethod
from typing import final


class Statement(ABC):
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
