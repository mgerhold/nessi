from pathlib import Path
from typing import Final

from nassi_shneiderman_generator.latex import render_latex_to_pdf

from nessi.array_type import ArrayType
from nessi.expressions import Variable
from nessi.program import Program
from nessi.statements import Assign
from nessi.statements import Input
from nessi.statements import Print
from nessi.statements import While
from nessi.value import Value


def main() -> None:
    program: Final = Program(
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
