"""
Zinc Bytecode - Instruction set and bytecode structures for the Zinc VM.
"""

from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional, Union


class OpCode(IntEnum):
    """Bytecode opcodes for the Zinc VM."""

    # Stack operations
    PUSH_INT = auto()       # Push integer constant
    PUSH_FLOAT = auto()     # Push float constant
    PUSH_STRING = auto()    # Push string constant
    PUSH_CHAR = auto()      # Push char constant
    PUSH_BOOL = auto()      # Push boolean constant
    PUSH_NULL = auto()      # Push null
    POP = auto()            # Pop top of stack
    DUP = auto()            # Duplicate top of stack

    # Variable operations
    LOAD_VAR = auto()       # Load variable by name
    STORE_VAR = auto()      # Store to variable by name
    LOAD_LOCAL = auto()     # Load local variable by index
    STORE_LOCAL = auto()    # Store to local variable by index
    LOAD_GLOBAL = auto()    # Load global variable by name
    STORE_GLOBAL = auto()   # Store to global variable by name
    DECLARE_VAR = auto()    # Declare a new variable

    # Arithmetic operations
    ADD = auto()            # a + b
    SUB = auto()            # a - b
    MUL = auto()            # a * b
    DIV = auto()            # a / b
    MOD = auto()            # a % b
    NEG = auto()            # -a (unary negation)
    POW = auto()            # a ** b (power)

    # Comparison operations
    EQ = auto()             # a == b
    NE = auto()             # a != b
    LT = auto()             # a < b
    LE = auto()             # a <= b
    GT = auto()             # a > b
    GE = auto()             # a >= b

    # Logical operations
    AND = auto()            # a && b
    OR = auto()             # a || b
    NOT = auto()            # !a

    # Control flow
    JUMP = auto()           # Unconditional jump
    JUMP_IF_FALSE = auto()  # Jump if top of stack is false
    JUMP_IF_TRUE = auto()   # Jump if top of stack is true

    # Function operations
    CALL = auto()           # Call function
    RETURN = auto()         # Return from function
    RETURN_VALUE = auto()   # Return value from function

    # Built-in functions
    PRINT = auto()          # Print values
    PRINT_NEWLINE = auto()  # Print newline
    INPUT_INT = auto()      # Read integer from user
    INPUT_FLOAT = auto()    # Read float from user
    INPUT_STRING = auto()   # Read string from user
    INPUT_CHAR = auto()     # Read char from user

    # Math functions
    SQRT = auto()           # Square root
    ABS = auto()            # Absolute value

    # Array operations
    CREATE_ARRAY = auto()   # Create array with size
    ARRAY_GET = auto()      # Get array element
    ARRAY_SET = auto()      # Set array element
    ARRAY_LENGTH = auto()   # Get array length
    ARRAY_LITERAL = auto()  # Create array from stack values

    # Struct operations
    CREATE_STRUCT = auto()  # Create struct instance
    STRUCT_GET = auto()     # Get struct field
    STRUCT_SET = auto()     # Set struct field

    # Memory operations (for pointers)
    ALLOC = auto()          # Allocate memory
    FREE = auto()           # Free memory
    LOAD_PTR = auto()       # Load value at pointer
    STORE_PTR = auto()      # Store value at pointer
    ADDRESS_OF = auto()     # Get address of variable

    # Loop control
    BREAK = auto()          # Break from loop
    CONTINUE = auto()       # Continue to next iteration

    # Random
    RANDOM = auto()         # Generate random number

    # Program control
    HALT = auto()           # Stop execution
    NOP = auto()            # No operation


class ValueType(IntEnum):
    """Types of values in the VM."""
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()
    BOOL = auto()
    NULL = auto()
    ARRAY = auto()
    STRUCT = auto()
    POINTER = auto()
    FUNCTION = auto()


@dataclass
class Value:
    """A runtime value in the VM."""
    type: ValueType
    data: Any

    def __repr__(self):
        if self.type == ValueType.STRING:
            return f'"{self.data}"'
        elif self.type == ValueType.CHAR:
            return f"'{self.data}'"
        elif self.type == ValueType.BOOL:
            return "yes" if self.data else "no"
        elif self.type == ValueType.NULL:
            return "null"
        elif self.type == ValueType.ARRAY:
            return f"[{', '.join(str(v) for v in self.data)}]"
        else:
            return str(self.data)

    def is_truthy(self) -> bool:
        """Check if value is truthy."""
        if self.type == ValueType.BOOL:
            return self.data
        elif self.type == ValueType.INT:
            return self.data != 0
        elif self.type == ValueType.FLOAT:
            return self.data != 0.0
        elif self.type == ValueType.STRING:
            return len(self.data) > 0
        elif self.type == ValueType.NULL:
            return False
        elif self.type == ValueType.ARRAY:
            return len(self.data) > 0
        return True


@dataclass
class Instruction:
    """A single bytecode instruction."""
    opcode: OpCode
    operand: Any = None
    line: int = 0  # Source line number for debugging

    def __repr__(self):
        if self.operand is not None:
            return f"{self.opcode.name} {self.operand!r}"
        return self.opcode.name


@dataclass
class Function:
    """A compiled function."""
    name: str
    params: List[str]
    param_types: List[str]
    return_type: Optional[str]
    code: List[Instruction] = field(default_factory=list)
    locals_count: int = 0
    is_main: bool = False

    def __repr__(self):
        return f"Function({self.name}, params={self.params})"


@dataclass
class StructDef:
    """A struct definition."""
    name: str
    fields: Dict[str, str]  # field_name -> type

    def __repr__(self):
        return f"StructDef({self.name}, fields={list(self.fields.keys())})"


@dataclass
class CompiledProgram:
    """A complete compiled program."""
    functions: Dict[str, Function] = field(default_factory=dict)
    structs: Dict[str, StructDef] = field(default_factory=dict)
    globals: Dict[str, Any] = field(default_factory=dict)
    constants: List[Any] = field(default_factory=list)
    main_function: Optional[str] = None

    def add_constant(self, value: Any) -> int:
        """Add a constant and return its index."""
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1

    def disassemble(self) -> str:
        """Generate a human-readable disassembly."""
        lines = []
        lines.append("=== Zinc Bytecode Disassembly ===\n")

        if self.structs:
            lines.append("--- Structs ---")
            for name, struct in self.structs.items():
                lines.append(f"struct {name}:")
                for field_name, field_type in struct.fields.items():
                    lines.append(f"  {field_type} {field_name}")
            lines.append("")

        lines.append("--- Functions ---")
        for name, func in self.functions.items():
            lines.append(f"\nfunction {name}({', '.join(func.params)}):")
            for i, instr in enumerate(func.code):
                lines.append(f"  {i:4d}: {instr}")

        return "\n".join(lines)


# Helper functions for creating values
def make_int(value: int) -> Value:
    return Value(ValueType.INT, value)

def make_float(value: float) -> Value:
    return Value(ValueType.FLOAT, value)

def make_string(value: str) -> Value:
    return Value(ValueType.STRING, value)

def make_char(value: str) -> Value:
    return Value(ValueType.CHAR, value)

def make_bool(value: bool) -> Value:
    return Value(ValueType.BOOL, value)

def make_null() -> Value:
    return Value(ValueType.NULL, None)

def make_array(elements: List[Value]) -> Value:
    return Value(ValueType.ARRAY, elements)

def make_struct(name: str, fields: Dict[str, Value]) -> Value:
    return Value(ValueType.STRUCT, {"__type__": name, **fields})
