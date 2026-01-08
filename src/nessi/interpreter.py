from typing import Final
from typing import Optional
from typing import final
from typing import override

from nessi.array_type import ArrayType
from nessi.expressions import ArrayElement
from nessi.statement_visitor import Statement
from nessi.statement_visitor import StatementVisitor
from nessi.statements import Assign
from nessi.statements import Break
from nessi.statements import Do
from nessi.statements import DocumentedBlock
from nessi.statements import If
from nessi.statements import Input
from nessi.statements import Loop
from nessi.statements import Match
from nessi.statements import Print
from nessi.statements import While
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
                if isinstance(input_value, list) and not isinstance(statement.type_, ArrayType):
                    first_value: Final = input_value.pop(0)
                    self._store_value(statement.target, first_value)
                else:
                    self._store_value(statement.target, input_value)
                return ""  # No output.
            case Print():
                return f"{statement.render(self.variables)}\n"
            case Assign():
                value: Final = statement.value.evaluate(self.variables)
                # No type checking here. ¯\_(ツ)_/¯
                match statement.target:
                    case str():
                        self._store_value(statement.target, value)
                    case ArrayElement() as array_element:
                        array_name: Final = array_element.array_name
                        index: Final = array_element.index.evaluate(context=self.variables)
                        array_value: Final = self.variables.get(array_name)
                        if not isinstance(array_value, list):
                            raise TypeError(f"Variable '{array_name}' is not an array.")
                        if not isinstance(index, int):
                            raise TypeError(f"Array index must be an integer, got {type(index)}.")
                        if index not in range(len(array_value)):
                            raise IndexError(f"Array index {index} out of bounds for array of size {len(array_value)}.")
                        if any(type(item) is not type(value) for item in array_value):
                            raise TypeError(f"Array '{array_name}' contains elements of different types.")
                        # We just checked that the arrays are compatible (or empty, but 🤫). Therefore,
                        # we ignore the error in the next line.
                        array_value[index] = value  # type: ignore[unsupported-operation]
                return ""  # No output.
            case If():
                is_condition_satisfied = statement.condition.evaluate(self.variables)
                if not isinstance(is_condition_satisfied, bool):
                    raise TypeError(f"Condition must evaluate to a boolean, got {type(is_condition_satisfied)}.")
                if not statement.then_block:
                    raise ValueError("If statement must have a 'then' block.")
                return self._evaluate_block(statement.then_block if is_condition_satisfied else statement.else_block)
            case While():
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
            case Do():
                if statement.label is not None:
                    self._loop_label_stack.append(statement.label)
                output = ""
                while True:
                    output += self._evaluate_block(statement.body)
                    condition: Final = statement.condition
                    if condition is None:
                        raise ValueError("Do statement must have a condition.")
                    is_condition_satisfied = condition.evaluate(self.variables)
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
