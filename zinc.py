#!/usr/bin/env python3
"""
Zinc Compiler - A natural English programming language that transpiles to C.

Usage:
    python zinc.py <file.zn>              # Compile and run
    python zinc.py <file.zn> -o <output>  # Specify output name
    python zinc.py <file.zn> --emit-c     # Output C code only
    python zinc.py <file.zn> --run        # Compile and run immediately
"""

import sys
import os
import argparse
import subprocess
import tempfile
from pathlib import Path

# Add the zinc directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transpiler import transpile


def compile_zinc(source_file: str, output_name: str = None, emit_c: bool = False,
                 run: bool = False, keep_c: bool = False) -> int:
    """
    Compile a Zinc source file.

    Args:
        source_file: Path to the .zn file
        output_name: Name for the output executable (optional)
        emit_c: If True, only output C code
        run: If True, run the compiled program immediately
        keep_c: If True, keep the intermediate C file

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

    # Transpile to C
    try:
        c_code = transpile(source)
    except SyntaxError as e:
        print(f"Syntax error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        return 1

    # If emit-c, just print and exit
    if emit_c:
        print(c_code)
        return 0

    # Determine output filename
    source_path = Path(source_file)
    if output_name:
        exe_name = output_name
    else:
        exe_name = source_path.stem

    # Add .exe extension on Windows
    if sys.platform == 'win32' and not exe_name.endswith('.exe'):
        exe_name += '.exe'

    # Write C code to temporary file
    c_file = source_path.with_suffix('.c')
    try:
        with open(c_file, 'w', encoding='utf-8') as f:
            f.write(c_code)
    except IOError as e:
        print(f"Error writing C file: {e}", file=sys.stderr)
        return 1

    # Compile with gcc
    try:
        compile_cmd = ['gcc', str(c_file), '-o', exe_name, '-lm']
        result = subprocess.run(compile_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"C compilation failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1

    except FileNotFoundError:
        print("Error: gcc not found. Please install a C compiler.", file=sys.stderr)
        return 1
    finally:
        # Clean up C file unless keeping it
        if not keep_c and c_file.exists():
            try:
                c_file.unlink()
            except:
                pass

    print(f"Compiled successfully: {exe_name}")

    # Run if requested
    if run:
        print(f"\n--- Running {exe_name} ---\n")
        try:
            # Use ./ prefix on Unix-like systems for current directory
            if sys.platform != 'win32' and not exe_name.startswith('/'):
                exe_path = './' + exe_name
            else:
                exe_path = exe_name

            result = subprocess.run([exe_path])
            return result.returncode
        except Exception as e:
            print(f"Error running program: {e}", file=sys.stderr)
            return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Zinc Compiler - Natural English to C transpiler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python zinc.py hello.zn              Compile hello.zn to executable
  python zinc.py hello.zn -o hello     Compile with custom output name
  python zinc.py hello.zn --emit-c     Output C code to stdout
  python zinc.py hello.zn --run        Compile and run immediately
  python zinc.py hello.zn --keep-c     Keep the intermediate C file
'''
    )

    parser.add_argument('source', help='Zinc source file (.zn)')
    parser.add_argument('-o', '--output', help='Output executable name')
    parser.add_argument('--emit-c', action='store_true',
                        help='Output C code instead of compiling')
    parser.add_argument('--run', action='store_true',
                        help='Run the program after compilation')
    parser.add_argument('--keep-c', action='store_true',
                        help='Keep the intermediate C file')

    args = parser.parse_args()

    # Validate source file
    if not args.source.endswith('.zn'):
        print(f"Warning: Source file does not have .zn extension", file=sys.stderr)

    return compile_zinc(
        args.source,
        output_name=args.output,
        emit_c=args.emit_c,
        run=args.run,
        keep_c=args.keep_c
    )


if __name__ == '__main__':
    sys.exit(main())
