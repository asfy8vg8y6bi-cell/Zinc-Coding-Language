# Zinc Programming Language

Computer go brrrrrrrrr


**Zinc** is a programming language with C semantics but with **English syntax**. At the bottom are instructions for the LLVM compiler.

## Quick Start

### Prerequisites

- Python 3.6+
- GCC (or any C compiler) (For transpiler)

### Hello World

Create a file `hello.zn`:

```zinc
include the standard input and output

to do the main thing:
    say "Hello, World!"
end
```

Compile and run:

```bash
python zinc.py hello.zn --run
```

### Usage (Transpiler)

```bash
python zinc.py <file.zn>              # Compile to executable
python zinc.py <file.zn> -o <name>    # Specify output name
python zinc.py <file.zn> --emit-c     # Output C code only
python zinc.py <file.zn> --run        # Compile and run immediately
python zinc.py <file.zn> --keep-c     # Keep intermediate C file
```

## Language Overview

### Data Types

| Zinc Type | C Type |
|-----------|--------|
| `number` | `int` |
| `decimal` | `double` |
| `letter` | `char` |
| `text` | `char*` |
| `yes or no` | `bool` |
| `nothing` | `void` |

### Variables

```zinc
there is a number called x
there is a number called age which is 25
there is text called name which is "Alice"
let result be 42
```

### Output

```zinc
say "Hello!"
say "The answer is " and then answer
```

### Conditions

```zinc
if x is greater than 10 then
    say "x is big"
otherwise
    say "x is small"
end
```

### Loops

```zinc
repeat 5 times:
    say "Hello!"
end

for each number i from 1 to 10:
    say i
end

while x is greater than 0:
    subtract 1 from x
end
```

### Functions

```zinc
to calculate the sum of number a and number b and return a number:
    return a plus b
end

to do the main thing:
    there is a number called result
    set result to the result of calculate the sum of 5 and 3
    say result
end
```

## Examples

Check the `examples/` directory for complete programs:

- `hello.zn` - Hello World
- `factorial.zn` - Factorial calculation
- `fibonacci.zn` - Fibonacci sequence
- `guessing_game.zn` - Number guessing game
- `bubble_sort.zn` - Bubble sort algorithm
- `linked_list.zn` - Linked list implementation

## Documentation

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for the complete language reference with all 20 examples.

## LLVM Compiler

As an alternative to the C transpiler, Zinc includes an LLVM-based compiler in the `compiler/` directory. This is a **true compiler** that generates native machine code - no interpretation involved.

### Prerequisites

```bash
pip install llvmlite
```

Also requires gcc or clang for linking.

### Compiling with LLVM

```bash
python compiler/zinc_vm.py hello.zn              # Compile to native executable
python compiler/zinc_vm.py hello.zn -o hello     # Specify output name
python compiler/zinc_vm.py hello.zn --run        # Compile and run immediately
python compiler/zinc_vm.py hello.zn --emit-llvm  # Output LLVM IR
python compiler/zinc_vm.py hello.zn --emit-object # Output object file (.o)
python compiler/zinc_vm.py hello.zn --disassemble # Show bytecode IR (intermediate)
```

### Compiler Options

| Option | Description |
|--------|-------------|
| `-o <file>` | Specify output file name |
| `--run`, `-r` | Compile and run immediately |
| `--emit-llvm` | Output LLVM IR instead of executable |
| `--emit-object` | Output object file (.o) instead of executable |
| `--disassemble`, `-d` | Show bytecode intermediate representation |
| `-O <0-3>` | Optimization level (default: 2) |

### Using as a Python Module

```python
from compiler import compile_program
from compiler.llvm_codegen import compile_to_executable

source_code = '''
include the standard input and output

to do the main thing:
    say "Hello from LLVM!"
end
'''

program = compile_program(source_code)
compile_to_executable(program, "hello")
```

### Compilation Pipeline

```
Zinc Source (.zn)
       |
       v
    [Parser] --> AST
       |
       v
   [Compiler] --> Bytecode IR
       |
       v
  [LLVM Codegen] --> LLVM IR
       |
       v
    [LLVM] --> Object Code (.o)
       |
       v
   [Linker] --> Native Executable
```

### Compiler Architecture

The `compiler/` package contains:

| File | Description |
|------|-------------|
| `bytecode.py` | Bytecode IR: instruction set (50+ opcodes), value types, data structures |
| `compiler.py` | Frontend: AST to bytecode IR compiler |
| `llvm_codegen.py` | Backend: bytecode IR to LLVM IR code generator |
| `zinc_vm.py` | Command-line interface |
| `__init__.py` | Package exports |

### LLVM Compiler vs C Transpiler

| Feature | LLVM Compiler (`compiler/`) | C Transpiler (`zinc.py`) |
|---------|----------------------------|-------------------------|
| Backend | LLVM | GCC/Clang via C |
| Output | Native executable | Native executable |
| Optimization | LLVM optimizations (-O0 to -O3) | C compiler optimizations |
| Intermediate | Bytecode IR + LLVM IR | C source code |
| Dependencies | llvmlite + linker | C compiler |

## Philosophy

- Reads like **English**
- No symbols except for strings and numbers
- A non-programmer should understand it
- C semantics under the hood for performance
- Why not?