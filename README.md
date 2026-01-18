# Zinc Programming Language

**Zinc** is a programming language with C semantics but **pure natural English syntax**. It reads like you're giving instructions to a person.

## Quick Start

### Prerequisites

- Python 3.6+
- GCC (or any C compiler)

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

### Usage

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

## Philosophy

- Reads like **actual English sentences**
- No symbols except for strings and numbers
- A non-programmer should understand it
- C semantics under the hood for performance
