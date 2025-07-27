from pathlib import Path
from typing import Final

from nassi_shneiderman_generator.latex import render_latex_to_pdf

from nessi.expressions import BinaryExpression, Integer, Operator, Variable
from nessi.program import Program
from nessi.statements import (
    Assignment,
    Break,
    Input,
    Loop,
    Match,
    MatchArm,
    Output,
    PostTestedLoop,
    PreTestedLoop,
    RelativeOperator,
    TruthCheck,
)
from nessi.value import Value


def main() -> None:
    program: Final = Program(
        [
            Input("n", int),
            Assignment(
                "n",
                BinaryExpression(Variable("n"), Operator.ADD, Integer(2)),
            ),
            Output("Der Wert ist {n}."),
            PreTestedLoop(
                BinaryExpression(
                    Variable("n"),
                    Operator.LESS_THAN,
                    Integer(50),
                ),
                [
                    TruthCheck(
                        BinaryExpression(
                            BinaryExpression(
                                Variable("n"),
                                Operator.MODULUS,
                                Integer(2),
                            ),
                            Operator.EQUALS,
                            Integer(0),
                        ),
                        Output("{n} ist gerade."),
                        [
                            Output("{n} ist ungerade. Raus hier!"),
                            Break("Schleife"),
                        ],
                    ),
                    Assignment(
                        "n",
                        BinaryExpression(Variable("n"), Operator.ADD, Integer(1)),
                    ),
                ],
                label="Schleife",
            ),
            Match(
                Variable("n"),
                [
                    MatchArm(
                        RelativeOperator.LESS_THAN,
                        Integer(40),
                        Output("Sehr komisch"),
                    ),
                    MatchArm(
                        RelativeOperator.LESS_THAN,
                        Integer(41),
                        Output("Hä?"),
                    ),
                    MatchArm(
                        RelativeOperator.LESS_THAN,
                        Integer(50),
                        Output("War zu erwarten."),
                    ),
                    MatchArm(
                        RelativeOperator.GREATER_THAN_OR_EQUAL,
                        Integer(51),
                        Output("Wuss?"),
                    ),
                ],
            ),
            PostTestedLoop(
                [
                    Assignment(
                        "n",
                        BinaryExpression(Variable("n"), Operator.SUBTRACT, Integer(10)),
                    ),
                    Output("Der Wert ist {n}."),
                ],
                BinaryExpression(
                    Variable("n"),
                    Operator.GREATER_THAN,
                    Integer(0),
                ),
            ),
            PreTestedLoop(
                BinaryExpression(Integer(1), Operator.EQUALS, Integer(1)),
                Loop(
                    [
                        Assignment(
                            "n",
                            BinaryExpression(Variable("n"), Operator.ADD, Integer(1)),
                        ),
                        Output("Der Wert ist {n}."),
                        TruthCheck(
                            BinaryExpression(
                                Variable("n"),
                                Operator.GREATER_THAN,
                                Integer(10),
                            ),
                            [
                                Output("Der Wert ist größer als 10."),
                                Break("Schleife"),
                            ],
                            Output("Der Wert ist kleiner oder gleich 10."),
                        ),
                    ]
                ),
                label="Schleife",
            ),
        ]
    )
    input_values: Final[dict[str, Value]] = {
        "n": 40,
    }
    output: Final = program.run(input_values, verbose=False)
    diagram: Final = program.generate_diagram()
    latex_code: Final = diagram.emit()
    render_latex_to_pdf(latex_code, Path("test.pdf"))
    print(f"Program output:\n'''\n{output}'''")
    # generate_diagrams(
    #     folder_path=Path("diagramme").resolve(),
    #     force_recreate=False,
    # )


if __name__ == "__main__":
    main()
