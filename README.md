# Nessi

![Nessi Logo](assets/logo.png)

A Python-based framework for program interpretation and Nassi-Shneiderman diagram generation using AST structures.

> [!WARNING]
> The implementation of this project is still incomplete. Feel free to contribute.

*Note: The project logo has been generated using ChatGPT.*

## Overview

Nessi is a framework designed for educational purposes that uses Abstract Syntax Trees (AST) represented as Python data structures to work with structured programming concepts. It provides:

- **Program Execution**: An interpreter that executes programs represented as Python AST data structures
- **Visual Diagrams**: Automatic generation of Nassi-Shneiderman diagrams from the same AST structures

## Features

### Control Structures

- **Conditional Statements**: `TruthCheck` for if-else logic
- **Loops**: Pre-tested, post-tested, and continuous iterations with optional labels
- **Multi-Conditional Statements**: `Match` statements with multiple conditions
- **Break Statements**: Labeled breaks for structured loop control

### Data Types and Operations

- **Basic Types**: Integers, floats, strings, and booleans
- **Variables**: Dynamic variable storage and retrieval
- **Expressions**: Binary operations (arithmetic and relational)
- **Input/Output**: Interactive input and formatted output with string interpolation

### Program Visualization

- **Nassi-Shneiderman Diagrams**: Automatic generation of structured flowcharts
- **LaTeX Export**: High-quality PDF diagram output

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
# Clone the repository
git clone git@github.com:mgerhold/nessi.git
cd nessi

# Install dependencies
uv sync
```

## Usage

See the `examples` folder for usage demonstrations. To run an example, type:

```bash
uv run python examples/<filename>.py
```

## Core Components

Nessi works with AST nodes represented as Python classes. Each node type corresponds to a programming construct:

### Statements

- `Input`: Read user input
- `Output`: Display formatted output with variable interpolation
- `Assignment`: Variable assignment with expression evaluation
- `TruthCheck`: Conditional branching (if-else)
- `PreTestedLoop`: While loops
- `PostTestedLoop`: Do-while loops
- `Loop`: Infinite loops with break conditions
- `Match`: Branching with multiple conditions
- `Break`: Labeled break statements
- `DocumentedBlock`: Commented code blocks

### Expressions

- `Variable`: Variable references
- `Integer`: Integer literals
- `BinaryExpression`: Binary operations (arithmetic and comparison)
- Support for operators: `+`, `-`, `*`, `/`, `MOD`, `>`, `<`, `==`, `!=`, `>=`, `<=`
