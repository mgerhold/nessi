from pathlib import Path
from typing import NamedTuple
from typing import final

from nassi_shneiderman_generator.latex import render_latex_to_pdf

from nessi.array_type import ArrayType
from nessi.expressions import Bool
from nessi.expressions import Variable
from nessi.program import Program
from nessi.statements import Assign
from nessi.statements import Break
from nessi.statements import If
from nessi.statements import Input
from nessi.statements import Print
from nessi.statements import While
from nessi.value import Value


@final
class Example(NamedTuple):
    program: Program
    input_values: dict[str, Value]


EXAMPLES = [
    Example(
        program=Program(
            [
                Input("n", int),
                Input("binary", ArrayType(int, "n")),
                Assign("decimal", 0),
                Assign("power_of_2", 1),
                Assign("i", Variable("n") - 1),
                While(Variable("i") >= 0).Repeat(
                    Assign(
                        "decimal",
                        Variable("decimal") + Variable("binary")[Variable("i")] * Variable("power_of_2"),
                    ),
                    Assign("power_of_2", Variable("power_of_2") * 2),
                    Assign("i", Variable("i") - 1),
                ),
                Print("Die Dezimalzahl ist {decimal}."),
            ]
        ),
        input_values={
            "n": 8,
            "binary": [0, 1, 0, 0, 1, 1, 0, 1],
        },
    ),
    Example(
        program=Program(
            [
                Assign("sum", 0.0),
                Assign("count", 0),
                Input("number", float),
                While(Variable("number") >= 0).Repeat(
                    Assign("sum", Variable("sum") + Variable("number")),
                    Assign("count", Variable("count") + 1),
                    Input("number", float),
                ),
                Print("{sum}, {count}"),
            ]
        ),
        input_values={
            "number": [5.0, 3.2, 7.1, -1.0],
        },
    ),
    Example(
        program=Program(
            [
                Input("numbers", ArrayType(int, 3)),
                Input("index", int),
                Input("value", int),
                Assign(Variable("numbers")[Variable("index")], Variable("value")),
                Assign("i", 0),
                While(Variable("i") < 3).Repeat(
                    Print("{numbers[i]}"),
                    Assign("i", Variable("i") + 1),
                ),
            ]
        ),
        input_values={
            "numbers": [10, 20, 30],
            "index": 1,
            "value": 99,
        },
    ),
    Example(
        program=Program(
            [
                Input("numbers", ArrayType(int, 10), hidden_in_latex=True),
                Input("n", int, hidden_in_latex=True),
                Assign("i", 0),
                While(Variable("i") < Variable("n") - 1, label="Schleife").Repeat(
                    Assign("j", 0),
                    Assign("did_swap", False),
                    While(Variable("j") < Variable("n") - Variable("i") - 1).Repeat(
                        If(Variable("numbers")[Variable("j")] > Variable("numbers")[Variable("j") + 1]).Then(
                            Assign("temp", Variable("numbers")[Variable("j")]),
                            Assign(Variable("numbers")[Variable("j")], Variable("numbers")[Variable("j") + 1]),
                            Assign(Variable("numbers")[Variable("j") + 1], Variable("temp")),
                            Assign("did_swap", True),
                        ),
                        Assign("j", Variable("j") + 1),
                    ),
                    If(Variable("did_swap") == Bool(False)).Then(
                        Break(label="Schleife"),
                    ),
                    Assign("i", Variable("i") + 1),
                ),
                Assign("i", 0),
                While(Variable("i") < Variable("n")).Repeat(
                    Print("{numbers[i]}"),
                    Assign("i", Variable("i") + 1),
                ),
            ]
        ),
        input_values={
            "numbers": [64, 34, 25, 12, 22, 11, 90, 55, 43, 78],
            "n": 10,
        },
    ),
]


def main() -> None:
    for i, example in enumerate(EXAMPLES):
        output = example.program.run(example.input_values, verbose=False)
        diagram = example.program.generate_diagram()
        latex_code = diagram.emit()
        print(latex_code)
        render_latex_to_pdf(latex_code, Path(f"test{i}.pdf"))
        print(f"Program output:\n'''\n{output}'''")


if __name__ == "__main__":
    main()
