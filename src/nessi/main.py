from pathlib import Path
from typing import Final

from nassi_shneiderman_generator.latex import render_latex_to_pdf

from nessi.array_type import ArrayType
from nessi.expressions import ArrayElement
from nessi.expressions import BinaryExpression
from nessi.expressions import Integer
from nessi.expressions import Operator
from nessi.expressions import Variable
from nessi.program import Program
from nessi.statements import Assignment
from nessi.statements import Input
from nessi.statements import Output
from nessi.statements import While
from nessi.value import Value


def main() -> None:
    program: Final = Program(
        [
            Input("n", int),
            Input("binary", ArrayType(int, "n")),
            Assignment("decimal", Integer(0)),
            Assignment("power_of_2", Integer(1)),
            Assignment("i", BinaryExpression(Variable("n"), Operator.SUBTRACT, Integer(1))),
            While(
                BinaryExpression(Variable("i"), Operator.GREATER_THAN_OR_EQUAL, Integer(0)),
                [
                    Assignment(
                        "decimal",
                        BinaryExpression(
                            Variable("decimal"),
                            Operator.ADD,
                            BinaryExpression(
                                ArrayElement("binary", Variable("i")),
                                Operator.MULTIPLY,
                                Variable("power_of_2"),
                            ),
                        ),
                    ),
                    Assignment(
                        "power_of_2",
                        BinaryExpression(Variable("power_of_2"), Operator.MULTIPLY, Integer(2)),
                    ),
                    Assignment(
                        "i",
                        BinaryExpression(Variable("i"), Operator.SUBTRACT, Integer(1)),
                    ),
                ],
            ),
            Output("Die Dezimalzahl ist {decimal}."),
        ]
    )
    input_values: Final[dict[str, Value]] = {
        "n": 8,
        "binary": [0, 1, 0, 0, 1, 1, 0, 1],
    }
    output: Final = program.run(input_values, verbose=False)
    diagram: Final = program.generate_diagram()
    latex_code: Final = diagram.emit()
    print(latex_code)
    render_latex_to_pdf(latex_code, Path("test.pdf"))
    print(f"Program output:\n'''\n{output}'''")


if __name__ == "__main__":
    main()
