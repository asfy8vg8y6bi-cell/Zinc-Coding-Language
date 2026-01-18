"""
Zinc Virtual Machine - Executes bytecode compiled from Zinc source.
"""

import math
import random
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from bytecode import (
    OpCode, Instruction, Function, CompiledProgram, Value, ValueType,
    make_int, make_float, make_string, make_char, make_bool, make_null, make_array
)


class VMError(Exception):
    """Runtime error in the Zinc VM."""
    pass


@dataclass
class CallFrame:
    """A call frame on the call stack."""
    function: Function
    ip: int = 0  # Instruction pointer
    base: int = 0  # Base of local variables on the stack
    locals: List[Value] = field(default_factory=list)


class VM:
    """
    Stack-based virtual machine for Zinc bytecode.
    """

    def __init__(self, program: CompiledProgram, debug: bool = False):
        self.program = program
        self.debug = debug

        # Runtime state
        self.stack: List[Value] = []
        self.call_stack: List[CallFrame] = []
        self.globals: Dict[str, Value] = {}

        # Current execution state
        self.current_frame: Optional[CallFrame] = None
        self.running = False

        # Initialize random number generator
        random.seed()

    def push(self, value: Value):
        """Push a value onto the stack."""
        self.stack.append(value)

    def pop(self) -> Value:
        """Pop a value from the stack."""
        if not self.stack:
            raise VMError("Stack underflow")
        return self.stack.pop()

    def peek(self, offset: int = 0) -> Value:
        """Peek at a value on the stack."""
        if offset >= len(self.stack):
            raise VMError("Stack underflow")
        return self.stack[-(offset + 1)]

    def run(self) -> int:
        """Run the program and return the exit code."""
        if not self.program.main_function:
            raise VMError("No main function found")

        # Set up the main function
        main_func = self.program.functions[self.program.main_function]
        self.call_function(main_func, [])

        self.running = True
        try:
            while self.running and self.call_stack:
                self.step()

            # Return value from main
            if self.stack:
                result = self.pop()
                if result.type == ValueType.INT:
                    return result.data
            return 0

        except VMError as e:
            frame = self.current_frame
            if frame:
                line = frame.function.code[frame.ip].line if frame.ip < len(frame.function.code) else 0
                print(f"Runtime error at line {line}: {e}")
            else:
                print(f"Runtime error: {e}")
            return 1

    def call_function(self, func: Function, args: List[Value]):
        """Call a function with the given arguments."""
        frame = CallFrame(
            function=func,
            ip=0,
            base=len(self.stack),
            locals=[make_null() for _ in range(func.locals_count)]
        )

        # Initialize parameters with arguments
        for i, arg in enumerate(args):
            if i < len(frame.locals):
                frame.locals[i] = arg

        self.call_stack.append(frame)
        self.current_frame = frame

    def step(self):
        """Execute one instruction."""
        frame = self.current_frame
        if not frame or frame.ip >= len(frame.function.code):
            self.running = False
            return

        instr = frame.function.code[frame.ip]
        frame.ip += 1

        if self.debug:
            self.debug_instruction(instr)

        self.execute(instr)

    def execute(self, instr: Instruction):
        """Execute a single instruction."""
        op = instr.opcode
        operand = instr.operand

        # Push operations
        if op == OpCode.PUSH_INT:
            self.push(make_int(operand))

        elif op == OpCode.PUSH_FLOAT:
            self.push(make_float(operand))

        elif op == OpCode.PUSH_STRING:
            self.push(make_string(operand))

        elif op == OpCode.PUSH_CHAR:
            self.push(make_char(operand))

        elif op == OpCode.PUSH_BOOL:
            self.push(make_bool(operand))

        elif op == OpCode.PUSH_NULL:
            self.push(make_null())

        elif op == OpCode.POP:
            self.pop()

        elif op == OpCode.DUP:
            self.push(self.peek())

        # Variable operations
        elif op == OpCode.LOAD_LOCAL:
            idx = operand
            if idx < len(self.current_frame.locals):
                self.push(self.current_frame.locals[idx])
            else:
                raise VMError(f"Invalid local variable index: {idx}")

        elif op == OpCode.STORE_LOCAL:
            idx = operand
            value = self.pop()
            # Expand locals if needed
            while idx >= len(self.current_frame.locals):
                self.current_frame.locals.append(make_null())
            self.current_frame.locals[idx] = value

        elif op == OpCode.LOAD_GLOBAL:
            name = operand
            if name in self.globals:
                self.push(self.globals[name])
            else:
                raise VMError(f"Undefined global variable: {name}")

        elif op == OpCode.STORE_GLOBAL:
            name = operand
            value = self.pop()
            self.globals[name] = value

        # Arithmetic operations
        elif op == OpCode.ADD:
            b = self.pop()
            a = self.pop()
            self.push(self.binary_op(a, b, "+"))

        elif op == OpCode.SUB:
            b = self.pop()
            a = self.pop()
            self.push(self.binary_op(a, b, "-"))

        elif op == OpCode.MUL:
            b = self.pop()
            a = self.pop()
            self.push(self.binary_op(a, b, "*"))

        elif op == OpCode.DIV:
            b = self.pop()
            a = self.pop()
            self.push(self.binary_op(a, b, "/"))

        elif op == OpCode.MOD:
            b = self.pop()
            a = self.pop()
            self.push(self.binary_op(a, b, "%"))

        elif op == OpCode.NEG:
            a = self.pop()
            if a.type == ValueType.INT:
                self.push(make_int(-a.data))
            elif a.type == ValueType.FLOAT:
                self.push(make_float(-a.data))
            else:
                raise VMError(f"Cannot negate {a.type.name}")

        elif op == OpCode.POW:
            b = self.pop()
            a = self.pop()
            result = math.pow(self.to_number(a), self.to_number(b))
            if a.type == ValueType.FLOAT or b.type == ValueType.FLOAT:
                self.push(make_float(result))
            else:
                self.push(make_int(int(result)))

        # Comparison operations
        elif op == OpCode.EQ:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(self.values_equal(a, b)))

        elif op == OpCode.NE:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(not self.values_equal(a, b)))

        elif op == OpCode.LT:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(self.to_number(a) < self.to_number(b)))

        elif op == OpCode.LE:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(self.to_number(a) <= self.to_number(b)))

        elif op == OpCode.GT:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(self.to_number(a) > self.to_number(b)))

        elif op == OpCode.GE:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(self.to_number(a) >= self.to_number(b)))

        # Logical operations
        elif op == OpCode.AND:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(a.is_truthy() and b.is_truthy()))

        elif op == OpCode.OR:
            b = self.pop()
            a = self.pop()
            self.push(make_bool(a.is_truthy() or b.is_truthy()))

        elif op == OpCode.NOT:
            a = self.pop()
            self.push(make_bool(not a.is_truthy()))

        # Control flow
        elif op == OpCode.JUMP:
            self.current_frame.ip = operand

        elif op == OpCode.JUMP_IF_FALSE:
            condition = self.pop()
            if not condition.is_truthy():
                self.current_frame.ip = operand

        elif op == OpCode.JUMP_IF_TRUE:
            condition = self.pop()
            if condition.is_truthy():
                self.current_frame.ip = operand

        # Function operations
        elif op == OpCode.CALL:
            func_name, arg_count = operand
            self.handle_call(func_name, arg_count)

        elif op == OpCode.RETURN:
            self.handle_return(make_null())

        elif op == OpCode.RETURN_VALUE:
            return_value = self.pop()
            self.handle_return(return_value)

        # Built-in I/O
        elif op == OpCode.PRINT:
            value = self.pop()
            print(self.value_to_string(value), end="")

        elif op == OpCode.PRINT_NEWLINE:
            print()

        elif op == OpCode.INPUT_INT:
            try:
                line = input()
                self.push(make_int(int(line)))
            except ValueError:
                self.push(make_int(0))

        elif op == OpCode.INPUT_FLOAT:
            try:
                line = input()
                self.push(make_float(float(line)))
            except ValueError:
                self.push(make_float(0.0))

        elif op == OpCode.INPUT_STRING:
            line = input()
            self.push(make_string(line))

        elif op == OpCode.INPUT_CHAR:
            line = input()
            self.push(make_char(line[0] if line else '\0'))

        # Math functions
        elif op == OpCode.SQRT:
            a = self.pop()
            result = math.sqrt(self.to_number(a))
            self.push(make_float(result))

        elif op == OpCode.ABS:
            a = self.pop()
            if a.type == ValueType.INT:
                self.push(make_int(abs(a.data)))
            elif a.type == ValueType.FLOAT:
                self.push(make_float(abs(a.data)))
            else:
                raise VMError(f"Cannot get absolute value of {a.type.name}")

        # Array operations
        elif op == OpCode.CREATE_ARRAY:
            size = self.pop()
            if size.type != ValueType.INT:
                raise VMError("Array size must be an integer")
            arr = [make_int(0) for _ in range(size.data)]
            self.push(make_array(arr))

        elif op == OpCode.ARRAY_LITERAL:
            count = operand
            elements = []
            for _ in range(count):
                elements.append(self.pop())
            elements.reverse()
            self.push(make_array(elements))

        elif op == OpCode.ARRAY_GET:
            index = self.pop()
            array = self.pop()
            if array.type != ValueType.ARRAY:
                raise VMError("Cannot index non-array value")
            if index.type != ValueType.INT:
                raise VMError("Array index must be an integer")
            idx = index.data
            # Handle negative indices
            if idx < 0:
                idx = len(array.data) + idx
            if idx < 0 or idx >= len(array.data):
                raise VMError(f"Array index out of bounds: {index.data}")
            self.push(array.data[idx])

        elif op == OpCode.ARRAY_SET:
            value = self.pop()
            index = self.pop()
            array = self.pop()
            if array.type != ValueType.ARRAY:
                raise VMError("Cannot index non-array value")
            if index.type != ValueType.INT:
                raise VMError("Array index must be an integer")
            idx = index.data
            if idx < 0:
                idx = len(array.data) + idx
            if idx < 0 or idx >= len(array.data):
                raise VMError(f"Array index out of bounds: {index.data}")
            array.data[idx] = value

        elif op == OpCode.ARRAY_LENGTH:
            array = self.pop()
            if array.type == ValueType.ARRAY:
                self.push(make_int(len(array.data)))
            elif array.type == ValueType.STRING:
                self.push(make_int(len(array.data)))
            else:
                raise VMError(f"Cannot get length of {array.type.name}")

        # Struct operations
        elif op == OpCode.CREATE_STRUCT:
            struct_name = operand
            if struct_name not in self.program.structs:
                raise VMError(f"Unknown struct type: {struct_name}")
            struct_def = self.program.structs[struct_name]
            fields = {"__type__": struct_name}
            for field_name in struct_def.fields:
                fields[field_name] = make_null()
            self.push(Value(ValueType.STRUCT, fields))

        elif op == OpCode.STRUCT_GET:
            field_name = operand
            struct = self.pop()
            if struct.type != ValueType.STRUCT:
                raise VMError("Cannot access field of non-struct value")
            if field_name not in struct.data:
                raise VMError(f"Unknown field: {field_name}")
            self.push(struct.data[field_name])

        elif op == OpCode.STRUCT_SET:
            field_name = operand
            # Stack order: [value, struct] with struct on top
            struct = self.pop()
            value = self.pop()
            if struct.type != ValueType.STRUCT:
                raise VMError("Cannot access field of non-struct value")
            struct.data[field_name] = value

        # Memory operations
        elif op == OpCode.ALLOC:
            count = self.pop()
            if count.type != ValueType.INT:
                raise VMError("Allocation size must be an integer")
            # Create an array as "allocated memory"
            arr = [make_int(0) for _ in range(count.data)]
            self.push(make_array(arr))

        elif op == OpCode.FREE:
            # In our VM, we don't actually need to free memory
            self.pop()

        elif op == OpCode.ADDRESS_OF:
            # Return a pointer-like value
            kind, idx = operand
            self.push(Value(ValueType.POINTER, (kind, idx)))

        elif op == OpCode.LOAD_PTR:
            ptr = self.pop()
            if ptr.type != ValueType.POINTER:
                raise VMError("Cannot dereference non-pointer value")
            kind, idx = ptr.data
            if kind == "local":
                self.push(self.current_frame.locals[idx])
            elif kind == "global":
                self.push(self.globals[idx])

        elif op == OpCode.STORE_PTR:
            value = self.pop()
            ptr = self.pop()
            if ptr.type != ValueType.POINTER:
                raise VMError("Cannot dereference non-pointer value")
            kind, idx = ptr.data
            if kind == "local":
                self.current_frame.locals[idx] = value
            elif kind == "global":
                self.globals[idx] = value

        # Random
        elif op == OpCode.RANDOM:
            max_val = self.pop()
            min_val = self.pop()
            if min_val.type != ValueType.INT or max_val.type != ValueType.INT:
                raise VMError("Random range must be integers")
            result = random.randint(min_val.data, max_val.data)
            self.push(make_int(result))

        # Control
        elif op == OpCode.HALT:
            self.running = False

        elif op == OpCode.NOP:
            pass

        else:
            raise VMError(f"Unknown opcode: {op}")

    def handle_call(self, func_name: str, arg_count: int):
        """Handle a function call."""
        # Collect arguments from stack
        args = []
        for _ in range(arg_count):
            args.append(self.pop())
        args.reverse()

        # Check for built-in functions
        result = self.call_builtin(func_name, args)
        if result is not None:
            self.push(result)
            return

        # Look up user-defined function
        if func_name not in self.program.functions:
            raise VMError(f"Unknown function: {func_name}")

        func = self.program.functions[func_name]
        if len(args) != len(func.params):
            raise VMError(f"Function {func_name} expects {len(func.params)} arguments, got {len(args)}")

        self.call_function(func, args)

    def call_builtin(self, name: str, args: List[Value]) -> Optional[Value]:
        """Call a built-in function. Returns None if not a builtin."""

        if name == "__strstr__":
            # String contains check
            if len(args) >= 2:
                haystack = self.to_string(args[0])
                needle = self.to_string(args[1])
                return make_bool(needle in haystack)
            return make_bool(False)

        if name == "__open_file__":
            # File operations not fully supported in VM
            return make_null()

        if name == "__close_file__":
            return make_null()

        if name == "__has_line__":
            return make_bool(False)

        if name == "__read_line__":
            return make_null()

        # GUI operations - stub implementations
        if name == "__open_window__":
            width = args[0].data if args else 800
            height = args[1].data if len(args) > 1 else 600
            title = args[2].data if len(args) > 2 else "Zinc App"
            print(f"[GUI] Opening window: {width}x{height} - {title}")
            return make_null()

        if name == "__close_window__":
            print("[GUI] Closing window")
            return make_null()

        if name == "__begin_drawing__":
            return make_null()

        if name == "__end_drawing__":
            return make_null()

        if name == "__clear_screen__":
            return make_null()

        if name == "__draw_rectangle__":
            return make_null()

        if name == "__draw_text__":
            return make_null()

        if name == "__window_should_close__":
            return make_bool(True)  # Always close for non-GUI mode

        if name == "__mouse_x__":
            return make_int(0)

        if name == "__mouse_y__":
            return make_int(0)

        if name == "__mouse_pressed__":
            return make_bool(False)

        return None  # Not a builtin

    def handle_return(self, value: Value):
        """Handle a return from a function."""
        self.call_stack.pop()
        if self.call_stack:
            self.current_frame = self.call_stack[-1]
            self.push(value)
        else:
            self.current_frame = None
            self.push(value)
            self.running = False

    def binary_op(self, a: Value, b: Value, op: str) -> Value:
        """Perform a binary operation."""
        # String concatenation
        if op == "+" and (a.type == ValueType.STRING or b.type == ValueType.STRING):
            return make_string(self.to_string(a) + self.to_string(b))

        # Numeric operations
        av = self.to_number(a)
        bv = self.to_number(b)

        if op == "+":
            result = av + bv
        elif op == "-":
            result = av - bv
        elif op == "*":
            result = av * bv
        elif op == "/":
            if bv == 0:
                raise VMError("Division by zero")
            result = av / bv
        elif op == "%":
            if bv == 0:
                raise VMError("Division by zero")
            result = av % bv
        else:
            raise VMError(f"Unknown operator: {op}")

        # Return appropriate type
        if a.type == ValueType.FLOAT or b.type == ValueType.FLOAT:
            return make_float(float(result))
        else:
            return make_int(int(result))

    def to_number(self, value: Value) -> float:
        """Convert a value to a number."""
        if value.type == ValueType.INT:
            return value.data
        elif value.type == ValueType.FLOAT:
            return value.data
        elif value.type == ValueType.BOOL:
            return 1 if value.data else 0
        elif value.type == ValueType.CHAR:
            return ord(value.data)
        else:
            raise VMError(f"Cannot convert {value.type.name} to number")

    def to_string(self, value: Value) -> str:
        """Convert a value to a string."""
        if value.type == ValueType.STRING:
            return value.data
        elif value.type == ValueType.INT:
            return str(value.data)
        elif value.type == ValueType.FLOAT:
            return str(value.data)
        elif value.type == ValueType.CHAR:
            return value.data
        elif value.type == ValueType.BOOL:
            return "yes" if value.data else "no"
        elif value.type == ValueType.NULL:
            return "null"
        elif value.type == ValueType.ARRAY:
            return "[" + ", ".join(self.to_string(v) for v in value.data) + "]"
        else:
            return str(value)

    def value_to_string(self, value: Value) -> str:
        """Convert a value to a string for printing."""
        return self.to_string(value)

    def values_equal(self, a: Value, b: Value) -> bool:
        """Check if two values are equal."""
        if a.type != b.type:
            # Allow comparing numbers of different types
            if a.type in (ValueType.INT, ValueType.FLOAT) and b.type in (ValueType.INT, ValueType.FLOAT):
                return self.to_number(a) == self.to_number(b)
            return False
        return a.data == b.data

    def debug_instruction(self, instr: Instruction):
        """Print debug information for an instruction."""
        frame = self.current_frame
        print(f"[{frame.function.name}:{frame.ip-1}] {instr}")
        print(f"  Stack: {self.stack[-5:] if len(self.stack) > 5 else self.stack}")


def run_program(program: CompiledProgram, debug: bool = False) -> int:
    """Run a compiled program and return the exit code."""
    vm = VM(program, debug=debug)
    return vm.run()


if __name__ == "__main__":
    from compiler import compile_program

    test_code = '''
include the standard input and output

to do the main thing:
    there is a number called x which is 5
    say "Hello, World!"
    if x is greater than 3 then
        say "x is big"
    end

    repeat 3 times:
        say "Counting..."
    end
end
'''

    compiled = compile_program(test_code)
    print("=== Disassembly ===")
    print(compiled.disassemble())
    print("\n=== Execution ===")
    exit_code = run_program(compiled)
    print(f"\n=== Exit code: {exit_code} ===")
