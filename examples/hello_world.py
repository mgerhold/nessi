from pathlib import Path
from typing import Final

from nassi_shneiderman_generator.main import render_latex_to_pdf

from nessi.program import Program
from nessi.statements import Print

program: Final = Program(
    [
        Print("Hello, World!"),
    ]
)

output: Final = program.run({})
print(f"Program output:\n{output}")  # Outputs: "Hello, World!"

diagram: Final = program.generate_diagram()
latex_code: Final = diagram.emit()

print(f"LaTeX code for Tikz diagram:\n{latex_code}")

# If you have the necessary LaTeX tooling installed (and available in your PATH),
# you can render the LaTeX code to a PDF file.
render_latex_to_pdf(latex_code, Path("hello_world.pdf"))
