import re
from typing import Final
from typing import final

from nassi_shneiderman_generator.symbols import Block as DiagramBlock
from nassi_shneiderman_generator.symbols import Branch
from nassi_shneiderman_generator.symbols import ContinuousIteration
from nassi_shneiderman_generator.symbols import DyadicSelective
from nassi_shneiderman_generator.symbols import Imperative
from nassi_shneiderman_generator.symbols import MonadicSelective
from nassi_shneiderman_generator.symbols import MultipleExclusiveSelective
from nassi_shneiderman_generator.symbols import PostTestedIteration
from nassi_shneiderman_generator.symbols import PreTestedIteration
from nassi_shneiderman_generator.symbols import Serial
from nassi_shneiderman_generator.symbols import Symbol
from nassi_shneiderman_generator.symbols import Termination

from nessi.array_type import ArrayType
from nessi.statement_visitor import Statement
from nessi.statement_visitor import StatementVisitor
from nessi.statements import Assignment
from nessi.statements import Block
from nessi.statements import Break
from nessi.statements import DocumentedBlock
from nessi.statements import DoWhile
from nessi.statements import If
from nessi.statements import Input
from nessi.statements import Loop
from nessi.statements import Match
from nessi.statements import Output
from nessi.statements import While


@final
class DiagramGenerator(StatementVisitor[Symbol]):
    def visit(self, statement: Statement) -> Symbol:
        match statement:
            case Input():
                sanitized_target: Final = statement.target.replace("_", r"\_")
                if isinstance(statement.type_, ArrayType):
                    if isinstance(statement.type_.length, int):
                        return Imperative(rf"Eingabe: \texttt{{{sanitized_target}}}[{statement.type_.length}]")
                    if isinstance(statement.type_.length, str):
                        return Imperative(
                            rf"Eingabe: \texttt{{{sanitized_target}}}"
                            + rf"[\texttt{{{statement.type_.length.replace('_', r'\_')}}}]"
                        )
                    raise NotImplementedError(
                        "Diagram generation for array input not implemented: "
                        + f"Unexpected length type {type(statement.type_.length)}"
                    )
                return Imperative(rf"Eingabe: \texttt{{{sanitized_target}}}")
            case Output():
                return Imperative(f"Ausgabe: {DiagramGenerator._placeholders_to_latex(statement.text.text)}")
            case Assignment():
                return Imperative(
                    rf"$\texttt{{{statement.target.replace('_', r'\_')}}} := {statement.value.to_latex()}$"
                )
            case If():
                has_else_branch: Final = bool(statement.Else)
                common_condition_part: Final = f"${statement.condition.to_latex()}$?"
                if has_else_branch:
                    return DyadicSelective(
                        common_condition_part,
                        Branch("ja", self.generate_diagram_for_block(statement.then_block)),
                        Branch(
                            "nein",
                            self.generate_diagram_for_block(statement.else_block),
                        ),
                    )
                return MonadicSelective(
                    common_condition_part,
                    Branch("ja", self.generate_diagram_for_block(statement.then_block)),
                )
            case While():
                loop_header_text = "" if statement.label is None else f"{statement.label}: "
                loop_header_text += f"${statement.condition.to_latex()}$"
                return PreTestedIteration(
                    loop_header_text,
                    self.generate_diagram_for_block(statement.body),
                )
            case DoWhile():
                loop_footer_text = "" if statement.label is None else f"{statement.label}: "
                loop_footer_text += f"${statement.condition.to_latex()}$"
                return PostTestedIteration(
                    loop_footer_text,
                    self.generate_diagram_for_block(statement.body),
                )
            case Loop():
                # TODO: The diagram generator currently does not support labels for
                #       continuous iterations. As soon as this is implemented, we should
                #       uncomment the following lines.
                # loop_header_text = (
                #     "" if statement.label is None else f"{statement.label}: "
                # )
                return ContinuousIteration(
                    # loop_header_text,
                    self.generate_diagram_for_block(statement.body),
                )
            case Break():
                return Termination(statement.label.replace("_", r"\_"))
            case DocumentedBlock():
                return DiagramBlock(
                    statement.docstring.replace("_", r"\_"),
                    self.generate_diagram_for_block(statement.block),
                )
            case Match():
                return MultipleExclusiveSelective(
                    f"${statement.value.to_latex()}$",
                    [
                        Branch(
                            f"${arm.operator.value[1]} {arm.condition.to_latex()}$",
                            self.generate_diagram_for_block(arm.body),
                        )
                        for arm in statement.arms
                    ],
                )
            case _:
                raise NotImplementedError(f"Diagram generation for {type(statement)} is not implemented.")

    @staticmethod
    def _placeholders_to_latex(text: str) -> str:
        return re.sub(r"\{([^{}]+)}", r"\\texttt{\1}", text).replace("_", r"\_")

    def generate_diagram_for_block(self, block: Block) -> Symbol:
        is_single_statement: Final = len(block) == 1
        if is_single_statement:
            return self.visit(block[0])
        return Serial([self.visit(statement) for statement in block if not statement.hidden_in_latex])
