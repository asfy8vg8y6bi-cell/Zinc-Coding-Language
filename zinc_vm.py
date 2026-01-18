#!/usr/bin/env python3
"""
Zinc VM Compiler - A bytecode virtual machine for the Zinc language.

This is an alternative to the C transpiler that executes Zinc programs
directly using a stack-based virtual machine.

Usage:
    python zinc_vm.py <file.zn>                 # Compile and run
    python zinc_vm.py <file.zn> --disassemble   # Show bytecode disassembly
    python zinc_vm.py <file.zn> --debug         # Run with debug output
    python zinc_vm.py <file.zn> --emit-bytecode # Output bytecode to file
"""

import sys
import os
import argparse
import pickle
from pathlib import Path

# Add parent directory to path for parser imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add current directory for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler import compile_program
from vm import run_program


def run_zinc_vm(source_file: str, disassemble: bool = False, debug: bool = False,
                emit_bytecode: bool = False, output_file: str = None) -> int:
    """
    Compile and run a Zinc source file using the bytecode VM.

    Args:
        source_file: Path to the .zn file
        disassemble: If True, show bytecode disassembly
        debug: If True, enable debug output during execution
        emit_bytecode: If True, save compiled bytecode to file
        output_file: Path for bytecode output (optional)

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

    # Compile to bytecode
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

    # Show disassembly if requested
    if disassemble:
        print(compiled.disassemble())
        return 0

    # Save bytecode if requested
    if emit_bytecode:
        source_path = Path(source_file)
        if output_file:
            bytecode_file = Path(output_file)
        else:
            bytecode_file = source_path.with_suffix('.znc')

        try:
            with open(bytecode_file, 'wb') as f:
                pickle.dump(compiled, f)
            print(f"Bytecode saved to: {bytecode_file}")
        except IOError as e:
            print(f"Error saving bytecode: {e}", file=sys.stderr)
            return 1
        return 0

    # Run the program
    try:
        exit_code = run_program(compiled, debug=debug)
        return exit_code
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
        return 130
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        if debug:
            import traceback
            traceback.print_exc()
        return 1


def run_bytecode_file(bytecode_file: str, debug: bool = False) -> int:
    """
    Run a pre-compiled bytecode file.

    Args:
        bytecode_file: Path to the .znc file
        debug: If True, enable debug output

    Returns:
        Exit code (0 for success)
    """
    try:
        with open(bytecode_file, 'rb') as f:
            compiled = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {bytecode_file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error loading bytecode: {e}", file=sys.stderr)
        return 1

    try:
        return run_program(compiled, debug=debug)
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
        return 130
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='Zinc VM - Bytecode virtual machine for the Zinc language',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python zinc_vm.py hello.zn                Run hello.zn in the VM
  python zinc_vm.py hello.zn --disassemble  Show bytecode disassembly
  python zinc_vm.py hello.zn --debug        Run with debug output
  python zinc_vm.py hello.zn --emit-bytecode  Save bytecode to hello.znc
  python zinc_vm.py hello.znc               Run pre-compiled bytecode

The Zinc VM executes programs directly without compiling to C.
This makes it portable and easier to debug, though potentially slower
than the native C compiler for compute-intensive programs.
'''
    )

    parser.add_argument('source', help='Zinc source file (.zn) or bytecode file (.znc)')
    parser.add_argument('--disassemble', '-d', action='store_true',
                        help='Show bytecode disassembly instead of running')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output during execution')
    parser.add_argument('--emit-bytecode', '-c', action='store_true',
                        help='Compile and save bytecode to file')
    parser.add_argument('-o', '--output', help='Output file for bytecode')

    args = parser.parse_args()

    # Check if it's a bytecode file
    if args.source.endswith('.znc'):
        if args.disassemble or args.emit_bytecode:
            print("Error: Cannot disassemble or emit bytecode from a bytecode file",
                  file=sys.stderr)
            return 1
        return run_bytecode_file(args.source, debug=args.debug)

    # Validate source file
    if not args.source.endswith('.zn'):
        print(f"Warning: Source file does not have .zn extension", file=sys.stderr)

    return run_zinc_vm(
        args.source,
        disassemble=args.disassemble,
        debug=args.debug,
        emit_bytecode=args.emit_bytecode,
        output_file=args.output
    )


if __name__ == '__main__':
    sys.exit(main())
