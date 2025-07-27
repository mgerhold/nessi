from enum import Enum
from typing import Final, Optional, final, override

from nessi.context import Context
from nessi.expressions import Expression
from nessi.interpolated_string import InterpolatedString
from nessi.statement_visitor import Statement
from nessi.value import Value

type Block = list[Statement]


@final
class Input(Statement):
    def __init__(self, target: str, type_: type) -> None:
        self._target = target
        self._type = type_

    @property
    def target(self) -> str:
        return self._target

    def raise_if_not_assignable(self, value: Value) -> None:
        if not isinstance(value, self._type):
            raise TypeError(f"Cannot assign {value} to {self._target}: expected {self._type.__name__}")

    @override
    def __str__(self) -> str:
        return f"Input({self._target})"


@final
class Output(Statement):
    def __init__(self, text: str) -> None:
        self._text = InterpolatedString(text)

    @property
    def text(self) -> InterpolatedString:
        return self._text

    def render(self, context: Context) -> str:
        return self._text.interpolate(context)

    @override
    def __str__(self) -> str:
        return f"Output({self._text})"


@final
class Assignment(Statement):
    def __init__(self, target: str, value: Expression) -> None:
        self._target = target
        self._value = value

    @property
    def target(self) -> str:
        return self._target

    @property
    def value(self) -> Expression:
        return self._value

    @override
    def __str__(self) -> str:
        return f"Assignment({self._target}, {self._value})"


@final
class TruthCheck(Statement):
    def __init__(
        self,
        condition: Expression,
        then: Statement | Block,
        else_: Optional[Statement | Block],
    ) -> None:
        self._condition = condition
        self._then = [then] if isinstance(then, Statement) else then
        self._else = [] if else_ is None else ([else_] if isinstance(else_, Statement) else else_)

    @property
    def condition(self) -> Expression:
        return self._condition

    @property
    def then(self) -> Block:
        return self._then

    @property
    def else_(self) -> Block:
        return self._else

    @override
    def __str__(self) -> str:
        then_str: Final = ", ".join(str(statement) for statement in self.then)
        else_str = f", else: {', '.join(str(statement) for statement in self.else_)}" if self._else else ""
        return f"TruthCheck({self._condition}, then: {then_str}{else_str})"


@final
class PreTestedLoop(Statement):
    def __init__(
        self,
        condition: Expression,
        body: Statement | Block,
        *,
        label: Optional[str] = None,
    ) -> None:
        self._condition = condition
        self._body = [body] if isinstance(body, Statement) else body
        self._label = label

    @property
    def condition(self) -> Expression:
        return self._condition

    @property
    def body(self) -> Block:
        return self._body

    @property
    def label(self) -> Optional[str]:
        return self._label

    @override
    def __str__(self) -> str:
        body_str: Final = ", ".join(str(statement) for statement in self.body)
        return f"PreTestedLoop({self._condition}, body: {body_str})"


@final
class PostTestedLoop(Statement):
    def __init__(
        self,
        body: Statement | Block,
        condition: Expression,
        *,
        label: Optional[str] = None,
    ) -> None:
        self._body = [body] if isinstance(body, Statement) else body
        self._condition = condition
        self._label = label

    @property
    def body(self) -> Block:
        return self._body

    @property
    def condition(self) -> Expression:
        return self._condition

    @property
    def label(self) -> Optional[str]:
        return self._label

    @override
    def __str__(self) -> str:
        body_str: Final = ", ".join(str(statement) for statement in self.body)
        return f"PostTestedLoop(body: {body_str}, condition: {self.condition})"


@final
class Loop(Statement):
    def __init__(
        self,
        body: Statement | Block,
        *,
        label: Optional[str] = None,
    ) -> None:
        self._body = [body] if isinstance(body, Statement) else body
        self._label = label

    @property
    def body(self) -> Block:
        return self._body

    @property
    def label(self) -> Optional[str]:
        return self._label

    @override
    def __str__(self) -> str:
        body_str: Final = ", ".join(str(statement) for statement in self.body)
        return f"Loop(body: {body_str})"


@final
class Break(Statement):
    def __init__(self, label: str) -> None:
        self._label = label

    @property
    def label(self) -> str:
        return self._label

    @override
    def __str__(self) -> str:
        return f"Break({self._label})"


@final
class DocumentedBlock(Statement):
    def __init__(self, docstring: str, block: Block) -> None:
        self._docstring = docstring
        self._block = block

    @property
    def docstring(self) -> str:
        return self._docstring

    @property
    def block(self) -> Block:
        return self._block

    @override
    def __str__(self) -> str:
        block_str: Final = ", ".join(str(statement) for statement in self.block)
        return f"DocumentedBlock('{self.docstring}', block: {block_str})"


@final
class RelativeOperator(Enum):
    EQUALS = ("==", "=")
    NOT_EQUALS = ("!=", r"\neq")
    LESS_THAN = ("<", "<")
    LESS_THAN_OR_EQUAL = ("<=", r"\leq")
    GREATER_THAN = (">", ">")
    GREATER_THAN_OR_EQUAL = (">=", r"\geq")


@final
class MatchArm:
    def __init__(
        self,
        operator: RelativeOperator,
        condition: Expression,
        body: Statement | Block,
    ) -> None:
        self._operator = operator
        self._condition = condition
        self._body = [body] if isinstance(body, Statement) else body

    @property
    def operator(self) -> RelativeOperator:
        return self._operator

    @property
    def condition(self) -> Expression:
        return self._condition

    @property
    def body(self) -> Block:
        return self._body


def is_match_arm_condition_satisfied(
    left: Value,
    operator: RelativeOperator,
    right: Value,
) -> bool:
    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        raise TypeError(f"Cannot compare {left} and {right} with operator {operator}")
    if operator == RelativeOperator.EQUALS:
        return left == right
    if operator == RelativeOperator.NOT_EQUALS:
        return left != right
    if operator == RelativeOperator.LESS_THAN:
        return left < right
    if operator == RelativeOperator.LESS_THAN_OR_EQUAL:
        return left <= right
    if operator == RelativeOperator.GREATER_THAN:
        return left > right
    if operator == RelativeOperator.GREATER_THAN_OR_EQUAL:
        return left >= right
    raise ValueError(f"Unknown operator: {operator}")


@final
class Match(Statement):
    def __init__(self, value: Expression, arms: list[MatchArm]) -> None:
        self._value = value
        self._arms = arms

    @property
    def value(self) -> Expression:
        return self._value

    @property
    def arms(self) -> list[MatchArm]:
        return self._arms

    @override
    def __str__(self) -> str:
        arms_str: Final = ", ".join(
            f"MatchArm({arm.condition}, {arm.operator}, {', '.join(str(statement) for statement in arm.body)})"
            for arm in self.arms
        )
        return f"Match({self.value}, arms: [{arms_str}])"
