import re
from typing import Final, final

from nassi_shneiderman_generator.symbols import Block as DiagramBlock
from nassi_shneiderman_generator.symbols import (
    Branch,
    ContinuousIteration,
    DyadicSelective,
    Imperative,
    MonadicSelective,
    MultipleExclusiveSelective,
    PostTestedIteration,
    PreTestedIteration,
    Serial,
    Symbol,
    Termination,
)

from nessi.statement_visitor import Statement, StatementVisitor
from nessi.statements import (
    Assignment,
    Block,
    Break,
    DocumentedBlock,
    Input,
    Loop,
    Match,
    Output,
    PostTestedLoop,
    PreTestedLoop,
    TruthCheck,
)


@final
class DiagramGenerator(StatementVisitor[Symbol]):
    def visit(self, statement: Statement) -> Symbol:
        match statement:
            case Input():
                return Imperative(rf"Eingabe: \texttt{{{statement.target}}}")
            case Output():
                return Imperative(f"Ausgabe: {DiagramGenerator._placeholders_to_latex(statement.text.text)}")
            case Assignment():
                return Imperative(rf"$\texttt{{{statement.target}}} := {statement.value.to_latex()}$")
            case TruthCheck():
                has_else_branch: Final = bool(statement.else_)
                common_condition_part: Final = f"${statement.condition.to_latex()}$?"
                if has_else_branch:
                    return DyadicSelective(
                        common_condition_part,
                        Branch("ja", self.generate_diagram_for_block(statement.then)),
                        Branch(
                            "nein",
                            self.generate_diagram_for_block(statement.else_),
                        ),
                    )
                return MonadicSelective(
                    common_condition_part,
                    Branch("ja", self.generate_diagram_for_block(statement.then)),
                )
            case PreTestedLoop():
                loop_header_text = "" if statement.label is None else f"{statement.label}: "
                loop_header_text += f"${statement.condition.to_latex()}$"
                return PreTestedIteration(
                    loop_header_text,
                    self.generate_diagram_for_block(statement.body),
                )
            case PostTestedLoop():
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
                return Termination(statement.label)
            case DocumentedBlock():
                return DiagramBlock(
                    statement.docstring,
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
        return re.sub(r"\{([^{}]+)}", r"\\texttt{\1}", text)

    def generate_diagram_for_block(self, block: Block) -> Symbol:
        is_single_statement: Final = len(block) == 1
        if is_single_statement:
            return self.visit(block[0])
        return Serial([self.visit(statement) for statement in block])
