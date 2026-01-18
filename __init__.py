"""
Zinc Bytecode Compiler and Virtual Machine

This package provides an alternative to the C transpiler that compiles
Zinc source code to bytecode and executes it in a virtual machine.

Modules:
    bytecode: Instruction set and bytecode data structures
    compiler: AST to bytecode compiler
    vm: Stack-based virtual machine
    zinc_vm: CLI entry point

Usage (command line):
    python -m compiler.zinc_vm hello.zn        # Run a Zinc program
    python compiler/zinc_vm.py hello.zn        # Alternative syntax

Usage (as module):
    from compiler import compile_program, run_program
    program = compile_program(source_code)
    exit_code = run_program(program)
"""

import sys
import os

# Add this directory to path for internal imports
_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)
# Add parent directory for parser imports
_parent = os.path.dirname(_dir)
if _parent not in sys.path:
    sys.path.insert(0, _parent)

from bytecode import OpCode, Instruction, Function, CompiledProgram, Value, ValueType
from compiler import Compiler, compile_program
from vm import VM, run_program

__all__ = [
    'OpCode', 'Instruction', 'Function', 'CompiledProgram', 'Value', 'ValueType',
    'Compiler', 'compile_program',
    'VM', 'run_program',
]
