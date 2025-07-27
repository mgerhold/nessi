from typing import Final
from typing import Optional
from typing import final
from typing import override

from nessi.statement_visitor import Statement
from nessi.statement_visitor import StatementVisitor
from nessi.statements import Assignment
from nessi.statements import Break
from nessi.statements import DocumentedBlock
from nessi.statements import Input
from nessi.statements import Loop
from nessi.statements import Match
from nessi.statements import Output
from nessi.statements import PostTestedLoop
from nessi.statements import PreTestedLoop
from nessi.statements import TruthCheck
from nessi.statements import is_match_arm_condition_satisfied
from nessi.value import Value


@final
class MissingValueForInputError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Input value for '{name}' required but not provided.")


@final
class InvalidBreakLabelError(ValueError):
    def __init__(self, label: str) -> None:
        super().__init__(f"Invalid break label '{label}'.")


@final
class UnexhaustiveMatchError(ValueError):
    def __init__(self) -> None:
        super().__init__("Match statement is not exhaustive.")


@final
class Interpreter(StatementVisitor[str]):
    def __init__(self, input_values: dict[str, Value]) -> None:
        self._input_values = input_values
        self._variables: dict[str, Value] = {}
        self._loop_label_stack: list[str] = []
        self._current_break_label: Optional[str] = None

    @override
    def visit(self, statement: Statement) -> str:
        match statement:
            case Input():
                input_value: Final = self._get_input_value(statement.target)
                statement.raise_if_not_assignable(input_value, self.variables)
                self._store_value(statement.target, input_value)
                return ""  # No output.
            case Output():
                return f"{statement.render(self.variables)}\n"
            case Assignment():
                value: Final = statement.value.evaluate(self.variables)
                # No type checking here. ¯\_(ツ)_/¯
                self._store_value(statement.target, value)
                return ""  # No output.
            case TruthCheck():
                is_condition_satisfied = statement.condition.evaluate(self.variables)
                if not isinstance(is_condition_satisfied, bool):
                    raise TypeError(f"Condition must evaluate to a boolean, got {type(is_condition_satisfied)}.")
                return self._evaluate_block(statement.then if is_condition_satisfied else statement.else_)
            case PreTestedLoop():
                if statement.label is not None:
                    self._loop_label_stack.append(statement.label)
                output = ""
                while True:
                    is_condition_satisfied = statement.condition.evaluate(self.variables)
                    if not isinstance(is_condition_satisfied, bool):
                        raise TypeError(f"Condition must evaluate to a boolean, got {type(is_condition_satisfied)}.")
                    if not is_condition_satisfied:
                        break
                    output += self._evaluate_block(statement.body)
                    if self._current_break_label is not None:
                        break
                if statement.label is not None:
                    if self._current_break_label == statement.label:
                        self._current_break_label = None
                    self._loop_label_stack.pop()
                return output
            case PostTestedLoop():
                if statement.label is not None:
                    self._loop_label_stack.append(statement.label)
                output = ""
                while True:
                    output += self._evaluate_block(statement.body)
                    is_condition_satisfied = statement.condition.evaluate(self.variables)
                    if not isinstance(is_condition_satisfied, bool):
                        raise TypeError(f"Condition must evaluate to a boolean, got {type(is_condition_satisfied)}.")
                    if not is_condition_satisfied or self._current_break_label is not None:
                        break
                if statement.label is not None:
                    if self._current_break_label == statement.label:
                        self._current_break_label = None
                    self._loop_label_stack.pop()
                return output
            case Loop():
                if statement.label is not None:
                    self._loop_label_stack.append(statement.label)
                output = ""
                while True:
                    output += self._evaluate_block(statement.body)
                    if self._current_break_label is not None:
                        break
                if statement.label is not None:
                    if self._current_break_label == statement.label:
                        self._current_break_label = None
                    self._loop_label_stack.pop()
                return output
            case Break():
                if statement.label not in self._loop_label_stack:
                    raise InvalidBreakLabelError(statement.label)
                self._current_break_label = statement.label
                return ""  # No output.
            case DocumentedBlock():
                return self._evaluate_block(statement.block)
            case Match():
                matched_value: Final = statement.value.evaluate(self.variables)
                for arm in statement.arms:
                    arm_value = arm.condition.evaluate(self.variables)
                    if is_match_arm_condition_satisfied(matched_value, arm.operator, arm_value):
                        return self._evaluate_block(arm.body)
                raise UnexhaustiveMatchError()
            case _:
                raise NotImplementedError(f"Statement type '{type(statement)}' not implemented.")

    @property
    def variables(self) -> dict[str, Value]:
        return self._variables

    def _evaluate_block(self, block: list[Statement]) -> str:
        output = ""
        for statement in block:
            output += self.visit(statement)
            if self._current_break_label is not None:
                break
        return output

    def _store_value(self, name: str, value: Value) -> None:
        self._variables[name] = value

    def _get_input_value(self, name: str) -> Value:
        value = self._input_values.get(name)
        if value is None:
            raise MissingValueForInputError(name)
        return value
