"""
Zinc LLVM Compiler

This package provides an LLVM-based compiler for the Zinc programming language.
It compiles Zinc source code to native machine code - no interpretation involved.

Compilation Pipeline:
    1. Parse: Zinc source -> AST (via parser module)
    2. Compile: AST -> Bytecode IR (compiler.py)
    3. Codegen: Bytecode IR -> LLVM IR (llvm_codegen.py)
    4. Link: LLVM IR -> Native executable (via LLVM + linker)

Modules:
    bytecode: Intermediate bytecode representation and data structures
    compiler: AST to bytecode compiler (frontend)
    llvm_codegen: Bytecode to LLVM IR code generator (backend)
    zinc_vm: CLI entry point

Usage (command line):
    python compiler/zinc_vm.py hello.zn           # Compile to executable
    python compiler/zinc_vm.py hello.zn --run     # Compile and run
    python compiler/zinc_vm.py hello.zn --emit-llvm  # Output LLVM IR

Usage (as module):
    from compiler import compile_program
    from compiler.llvm_codegen import compile_to_executable

    program = compile_program(source_code)
    compile_to_executable(program, "output")

Requirements:
    - llvmlite: pip install llvmlite
    - gcc or clang (for linking)
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

# LLVM codegen is optional (requires llvmlite)
try:
    from llvm_codegen import (
        LLVMCodeGenerator,
        compile_to_llvm,
        compile_to_object,
        compile_to_executable,
        get_llvm_ir,
        init_llvm,
        LLVM_AVAILABLE
    )
except ImportError:
    LLVM_AVAILABLE = False
    LLVMCodeGenerator = None
    compile_to_llvm = None
    compile_to_object = None
    compile_to_executable = None
    get_llvm_ir = None
    init_llvm = None

__all__ = [
    # Bytecode IR
    'OpCode', 'Instruction', 'Function', 'CompiledProgram', 'Value', 'ValueType',
    # Frontend compiler
    'Compiler', 'compile_program',
    # LLVM backend
    'LLVMCodeGenerator', 'compile_to_llvm', 'compile_to_object',
    'compile_to_executable', 'get_llvm_ir', 'init_llvm',
    'LLVM_AVAILABLE',
]
