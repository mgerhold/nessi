from typing import Final, final

from nassi_shneiderman_generator.diagram import Diagram

from nessi.diagram_generator import DiagramGenerator
from nessi.interpreter import Interpreter, Value
from nessi.statements import Block


@final
class Program:
    def __init__(self, statements: Block) -> None:
        self._statements = statements

    def run(self, input_values: dict[str, Value], *, verbose: bool) -> str:
        interpreter: Final = Interpreter(input_values)
        output = ""
        for statement in self._statements:
            if verbose:
                print(f"Executing statement: '{statement}'")
            statement_output = statement.accept(interpreter)
            if verbose:
                print(f"Output: '{statement_output}'")
                print(f"Variables in interpreter: {interpreter.variables}")
                print()
            output += statement_output

        return output

    def generate_diagram(self) -> Diagram:
        generator: Final = DiagramGenerator()
        return Diagram(generator.generate_diagram_for_block(self._statements))
