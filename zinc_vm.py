#!/usr/bin/env python3
"""
Zinc Compiler - Compiles Zinc source code to native executables via LLVM.

This is a true compiler that uses LLVM to generate native machine code.
It does NOT interpret - it produces standalone executables.

Usage:
    python zinc_vm.py <file.zn>                 # Compile to native executable
    python zinc_vm.py <file.zn> -o <name>       # Specify output name
    python zinc_vm.py <file.zn> --emit-llvm     # Output LLVM IR
    python zinc_vm.py <file.zn> --emit-object   # Output object file
    python zinc_vm.py <file.zn> --run           # Compile and run immediately
    python zinc_vm.py <file.zn> --disassemble   # Show bytecode (intermediate)

Requires: llvmlite (pip install llvmlite)
"""

import sys
import os
import argparse
import subprocess
import tempfile
from pathlib import Path

# Add parent directory to path for parser imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add current directory for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler import compile_program


def check_llvm_available():
    """Check if llvmlite is available."""
    try:
        import llvmlite
        return True
    except ImportError:
        return False


def compile_zinc(source_file: str, output_file: str = None, emit_llvm: bool = False,
                 emit_object: bool = False, disassemble: bool = False,
                 run: bool = False, opt_level: int = 2) -> int:
    """
    Compile a Zinc source file to a native executable.

    Args:
        source_file: Path to the .zn file
        output_file: Path for output (executable, .ll, or .o)
        emit_llvm: If True, output LLVM IR instead of executable
        emit_object: If True, output object file instead of executable
        disassemble: If True, show bytecode disassembly
        run: If True, compile and run immediately
        opt_level: Optimization level (0-3)

    Returns:
        Exit code (0 for success)
    """
    # Read source file
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {source_file}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Compile to bytecode (intermediate representation)
    try:
        compiled = compile_program(source)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    # Show disassembly if requested (bytecode intermediate)
    if disassemble:
        print(compiled.disassemble())
        return 0

    # Check for LLVM
    if not check_llvm_available():
        print("Error: llvmlite not installed.", file=sys.stderr)
        print("Install with: pip install llvmlite", file=sys.stderr)
        return 1

    # Import LLVM codegen
    from llvm_codegen import (
        compile_to_llvm, compile_to_object, compile_to_executable,
        get_llvm_ir, init_llvm
    )

    source_path = Path(source_file)

    # Emit LLVM IR
    if emit_llvm:
        try:
            init_llvm()
            llvm_ir = get_llvm_ir(compiled)
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(llvm_ir)
                print(f"LLVM IR written to: {output_file}")
            else:
                print(llvm_ir)
            return 0
        except Exception as e:
            print(f"Error generating LLVM IR: {e}", file=sys.stderr)
            return 1

    # Emit object file
    if emit_object:
        try:
            obj_file = output_file or str(source_path.with_suffix('.o'))
            compile_to_object(compiled, obj_file, opt_level)
            print(f"Object file written to: {obj_file}")
            return 0
        except Exception as e:
            print(f"Error generating object file: {e}", file=sys.stderr)
            return 1

    # Compile to executable
    try:
        if output_file:
            exe_file = output_file
        else:
            # Default executable name
            if sys.platform == 'win32':
                exe_file = str(source_path.with_suffix('.exe'))
            else:
                exe_file = str(source_path.with_suffix(''))

        compile_to_executable(compiled, exe_file, opt_level)
        print(f"Compiled: {exe_file}")

        # Run if requested
        if run:
            print(f"Running: {exe_file}")
            print("-" * 40)
            try:
                result = subprocess.run([exe_file], check=False)
                return result.returncode
            except Exception as e:
                print(f"Error running executable: {e}", file=sys.stderr)
                return 1

        return 0

    except subprocess.CalledProcessError as e:
        print(f"Linker error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Zinc Compiler - Compiles Zinc to native executables via LLVM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python zinc_vm.py hello.zn              Compile hello.zn to executable
  python zinc_vm.py hello.zn -o hello     Specify output name
  python zinc_vm.py hello.zn --run        Compile and run immediately
  python zinc_vm.py hello.zn --emit-llvm  Output LLVM IR
  python zinc_vm.py hello.zn --emit-object Output object file (.o)
  python zinc_vm.py hello.zn --disassemble Show bytecode (intermediate)

The Zinc compiler uses LLVM to generate optimized native machine code.
This produces standalone executables with no runtime dependencies.

Requirements:
  - llvmlite: pip install llvmlite
  - A C linker (gcc or clang) for final executable linking
'''
    )

    parser.add_argument('source', help='Zinc source file (.zn)')
    parser.add_argument('-o', '--output', help='Output file name')
    parser.add_argument('--emit-llvm', action='store_true',
                        help='Output LLVM IR instead of executable')
    parser.add_argument('--emit-object', action='store_true',
                        help='Output object file instead of executable')
    parser.add_argument('--disassemble', '-d', action='store_true',
                        help='Show bytecode disassembly (intermediate representation)')
    parser.add_argument('--run', '-r', action='store_true',
                        help='Compile and run immediately')
    parser.add_argument('-O', '--optimize', type=int, default=2, choices=[0, 1, 2, 3],
                        help='Optimization level (default: 2)')

    args = parser.parse_args()

    # Validate source file
    if not args.source.endswith('.zn'):
        print(f"Warning: Source file does not have .zn extension", file=sys.stderr)

    return compile_zinc(
        args.source,
        output_file=args.output,
        emit_llvm=args.emit_llvm,
        emit_object=args.emit_object,
        disassemble=args.disassemble,
        run=args.run,
        opt_level=args.optimize
    )


if __name__ == '__main__':
    sys.exit(main())
