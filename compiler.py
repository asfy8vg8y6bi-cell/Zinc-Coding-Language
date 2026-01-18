"""
Zinc Bytecode Compiler - Compiles AST to bytecode for the Zinc VM.
"""

import sys
import os

# Add parent directory to path for parser imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Optional, Set, Tuple
from parser import (
    ASTNode, Program, Include, StructDef as ASTStructDef, FunctionDef, TypeSpec, VarDecl,
    Statement, ExpressionStmt, Assignment, IfStatement, ElseIfClause,
    WhileStatement, ForStatement, ForEachStatement, RepeatStatement,
    ReturnStatement, BreakStatement, ContinueStatement, PrintStatement,
    InputStatement, Expression, BinaryOp, UnaryOp, NumberLiteral,
    DecimalLiteral, StringLiteral, CharLiteral, BoolLiteral, NullLiteral,
    Identifier, FunctionCall, ArrayAccess, MemberAccess, AddressOf,
    Dereference, ArrayLiteral, Allocate, Free, RandomNumber,
    OpenWindow, CloseWindow, BeginDrawing, EndDrawing, ClearScreen,
    DrawRectangle, DrawText, WindowShouldClose, MouseX, MouseY, MousePressed,
    parse
)
from bytecode import (
    OpCode, Instruction, Function, StructDef, CompiledProgram,
    ValueType
)


class LoopContext:
    """Tracks loop context for break/continue."""
    def __init__(self):
        self.break_jumps: List[int] = []
        self.continue_target: int = 0


class Compiler:
    """Compiles Zinc AST to bytecode."""

    def __init__(self):
        self.program = CompiledProgram()
        self.current_function: Optional[Function] = None
        self.local_vars: Dict[str, int] = {}  # var_name -> local index
        self.local_types: Dict[str, str] = {}  # var_name -> type
        self.local_count = 0
        self.loop_stack: List[LoopContext] = []
        self.array_sizes: Dict[str, int] = {}  # var_name -> size

    def compile(self, program: Program) -> CompiledProgram:
        """Compile a complete program."""
        self.program = CompiledProgram()

        # Compile struct definitions
        for struct in program.structures:
            self.compile_struct(struct)

        # Compile functions
        for func in program.functions:
            self.compile_function(func)

        # Find main function
        if "main" in self.program.functions:
            self.program.main_function = "main"

        return self.program

    def compile_struct(self, struct: ASTStructDef):
        """Compile a struct definition."""
        fields = {}
        for field in struct.fields:
            type_name = self.type_to_string(field.var_type)
            fields[field.name] = type_name

        self.program.structs[struct.name] = StructDef(
            name=struct.name,
            fields=fields
        )

    def compile_function(self, func: FunctionDef):
        """Compile a function definition."""
        # Create function object
        params = [p.name for p in func.params]
        param_types = [self.type_to_string(p.var_type) for p in func.params]
        return_type = self.type_to_string(func.return_type) if func.return_type else None

        compiled_func = Function(
            name=func.name,
            params=params,
            param_types=param_types,
            return_type=return_type,
            is_main=func.is_main
        )

        self.current_function = compiled_func
        self.local_vars = {}
        self.local_types = {}
        self.local_count = 0
        self.array_sizes = {}

        # Add parameters as local variables
        for i, param in enumerate(func.params):
            self.local_vars[param.name] = self.local_count
            self.local_types[param.name] = self.type_to_string(param.var_type)
            self.local_count += 1

        # Compile function body
        for stmt in func.body:
            self.compile_statement(stmt)

        # Add implicit return for void functions
        if not compiled_func.code or compiled_func.code[-1].opcode != OpCode.RETURN:
            if func.is_main:
                self.emit(OpCode.PUSH_INT, 0)
                self.emit(OpCode.RETURN_VALUE)
            else:
                self.emit(OpCode.RETURN)

        compiled_func.locals_count = self.local_count
        self.program.functions[func.name] = compiled_func
        self.current_function = None

    def emit(self, opcode: OpCode, operand: any = None, line: int = 0) -> int:
        """Emit a bytecode instruction."""
        instr = Instruction(opcode, operand, line)
        self.current_function.code.append(instr)
        return len(self.current_function.code) - 1

    def current_offset(self) -> int:
        """Get the current instruction offset."""
        return len(self.current_function.code)

    def patch_jump(self, offset: int, target: int = None):
        """Patch a jump instruction with the target address."""
        if target is None:
            target = self.current_offset()
        self.current_function.code[offset].operand = target

    def type_to_string(self, type_spec: Optional[TypeSpec]) -> str:
        """Convert a TypeSpec to a string representation."""
        if type_spec is None:
            return "int"

        if type_spec.base_type == "struct":
            base = type_spec.struct_name
        else:
            base = type_spec.base_type

        if type_spec.is_array:
            return f"array:{base}"
        if type_spec.is_pointer:
            return f"pointer:{base}"
        return base

    def compile_statement(self, stmt: Statement):
        """Compile a statement."""
        if isinstance(stmt, VarDecl):
            self.compile_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.compile_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self.compile_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self.compile_while(stmt)
        elif isinstance(stmt, ForStatement):
            self.compile_for(stmt)
        elif isinstance(stmt, ForEachStatement):
            self.compile_foreach(stmt)
        elif isinstance(stmt, RepeatStatement):
            self.compile_repeat(stmt)
        elif isinstance(stmt, PrintStatement):
            self.compile_print(stmt)
        elif isinstance(stmt, InputStatement):
            self.compile_input(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.compile_return(stmt)
        elif isinstance(stmt, BreakStatement):
            self.compile_break()
        elif isinstance(stmt, ContinueStatement):
            self.compile_continue()
        elif isinstance(stmt, Free):
            self.compile_free(stmt)
        elif isinstance(stmt, ExpressionStmt):
            self.compile_expression(stmt.expression)
            self.emit(OpCode.POP)  # Discard result
        # GUI statements - emit as function calls
        elif isinstance(stmt, OpenWindow):
            self.compile_open_window(stmt)
        elif isinstance(stmt, CloseWindow):
            self.emit(OpCode.CALL, ("__close_window__", 0))
            self.emit(OpCode.POP)
        elif isinstance(stmt, BeginDrawing):
            self.emit(OpCode.CALL, ("__begin_drawing__", 0))
            self.emit(OpCode.POP)
        elif isinstance(stmt, EndDrawing):
            self.emit(OpCode.CALL, ("__end_drawing__", 0))
            self.emit(OpCode.POP)
        elif isinstance(stmt, ClearScreen):
            self.emit(OpCode.PUSH_STRING, stmt.color)
            self.emit(OpCode.CALL, ("__clear_screen__", 1))
            self.emit(OpCode.POP)
        elif isinstance(stmt, DrawRectangle):
            self.compile_draw_rectangle(stmt)
        elif isinstance(stmt, DrawText):
            self.compile_draw_text(stmt)

    def compile_var_decl(self, decl: VarDecl):
        """Compile a variable declaration."""
        var_name = decl.name
        var_type = self.type_to_string(decl.var_type)

        # Allocate local variable slot
        self.local_vars[var_name] = self.local_count
        self.local_types[var_name] = var_type
        var_index = self.local_count
        self.local_count += 1

        # Handle file declarations
        if decl.is_file:
            if decl.file_path:
                self.compile_expression(decl.file_path)
                self.emit(OpCode.PUSH_STRING, decl.file_mode)
                self.emit(OpCode.CALL, ("__open_file__", 2))
            else:
                self.emit(OpCode.PUSH_NULL)
            self.emit(OpCode.STORE_LOCAL, var_index)
            return

        # Handle array declarations
        if decl.var_type and decl.var_type.is_array:
            if isinstance(decl.initial_value, ArrayLiteral):
                # Array with initializer
                size = len(decl.initial_value.elements)
                self.array_sizes[var_name] = size

                # Push elements in order (VM will reverse when popping)
                for elem in decl.initial_value.elements:
                    self.compile_expression(elem)
                self.emit(OpCode.ARRAY_LITERAL, size)
            elif decl.var_type.array_size:
                # Fixed-size array
                size = decl.var_type.array_size
                self.array_sizes[var_name] = size
                self.emit(OpCode.PUSH_INT, size)
                self.emit(OpCode.CREATE_ARRAY)
            else:
                # Dynamic array
                self.emit(OpCode.PUSH_NULL)

            self.emit(OpCode.STORE_LOCAL, var_index)
            return

        # Regular variable with initial value
        if decl.initial_value:
            self.compile_expression(decl.initial_value)
        else:
            # Default initialization
            if var_type in ("number", "int", "boolean"):
                self.emit(OpCode.PUSH_INT, 0)
            elif var_type in ("decimal", "float"):
                self.emit(OpCode.PUSH_FLOAT, 0.0)
            elif var_type in ("text", "string"):
                self.emit(OpCode.PUSH_NULL)
            elif var_type == "letter":
                self.emit(OpCode.PUSH_CHAR, '\0')
            elif var_type.startswith("struct:") or (decl.var_type and decl.var_type.base_type == "struct"):
                # Create a new struct instance
                struct_name = decl.var_type.struct_name if decl.var_type else var_type.split(":")[1]
                self.emit(OpCode.CREATE_STRUCT, struct_name)
            else:
                self.emit(OpCode.PUSH_NULL)

        self.emit(OpCode.STORE_LOCAL, var_index)

    def compile_assignment(self, assign: Assignment):
        """Compile an assignment statement."""
        # Compile the value first
        self.compile_expression(assign.value)

        # Handle different assignment targets
        if isinstance(assign.target, Identifier):
            var_name = assign.target.name
            if var_name in self.local_vars:
                self.emit(OpCode.STORE_LOCAL, self.local_vars[var_name])
            else:
                self.emit(OpCode.STORE_GLOBAL, var_name)

        elif isinstance(assign.target, ArrayAccess):
            # Stack: [value]
            # Need: [array, index, value] then ARRAY_SET
            self.compile_expression(assign.target.array)  # array
            self.compile_expression(assign.target.index)  # index
            # Rotate stack: value is now at top, need it after index
            # We emitted value first, so we need to handle this differently
            # Actually, let's reorder: emit array and index first, then swap
            # Easier: just redo with correct order

        elif isinstance(assign.target, MemberAccess):
            # Struct field assignment
            self.compile_expression(assign.target.object)
            self.emit(OpCode.STRUCT_SET, assign.target.member)

        elif isinstance(assign.target, Dereference):
            # Pointer dereference assignment
            self.compile_expression(assign.target.operand)
            self.emit(OpCode.STORE_PTR)

        # For array access, we need special handling
        if isinstance(assign.target, ArrayAccess):
            # Pop the value we compiled first
            # Actually, let's fix this properly by compiling in correct order
            # Remove the last instruction (it was wrong)
            self.current_function.code.pop()

            # Compile array, index, then value
            self.compile_expression(assign.target.array)
            self.compile_expression(assign.target.index)
            self.compile_expression(assign.value)
            self.emit(OpCode.ARRAY_SET)

    def compile_if(self, stmt: IfStatement):
        """Compile an if statement."""
        # Compile condition
        self.compile_expression(stmt.condition)

        # Jump if false to else/end
        jump_to_else = self.emit(OpCode.JUMP_IF_FALSE, 0)

        # Compile then body
        for s in stmt.then_body:
            self.compile_statement(s)

        # If there are else-if or else clauses
        if stmt.else_if_clauses or stmt.else_body:
            jump_to_end = self.emit(OpCode.JUMP, 0)
            self.patch_jump(jump_to_else)

            # Compile else-if clauses
            end_jumps = [jump_to_end]
            for else_if in stmt.else_if_clauses:
                self.compile_expression(else_if.condition)
                jump_to_next = self.emit(OpCode.JUMP_IF_FALSE, 0)

                for s in else_if.body:
                    self.compile_statement(s)

                end_jumps.append(self.emit(OpCode.JUMP, 0))
                self.patch_jump(jump_to_next)

            # Compile else body
            for s in stmt.else_body:
                self.compile_statement(s)

            # Patch all end jumps
            for jump in end_jumps:
                self.patch_jump(jump)
        else:
            self.patch_jump(jump_to_else)

    def compile_while(self, stmt: WhileStatement):
        """Compile a while statement."""
        loop_ctx = LoopContext()
        loop_ctx.continue_target = self.current_offset()
        self.loop_stack.append(loop_ctx)

        # Loop start
        loop_start = self.current_offset()

        # Compile condition
        self.compile_expression(stmt.condition)
        loop_exit = self.emit(OpCode.JUMP_IF_FALSE, 0)

        # Compile body
        for s in stmt.body:
            self.compile_statement(s)

        # Jump back to condition
        self.emit(OpCode.JUMP, loop_start)

        # Patch exit jump
        self.patch_jump(loop_exit)

        # Patch break jumps
        for break_jump in loop_ctx.break_jumps:
            self.patch_jump(break_jump)

        self.loop_stack.pop()

    def compile_for(self, stmt: ForStatement):
        """Compile a for statement (range-based)."""
        # Create loop variable
        var_name = stmt.var_name
        self.local_vars[var_name] = self.local_count
        self.local_types[var_name] = "number"
        var_index = self.local_count
        self.local_count += 1

        # Initialize loop variable with start value
        self.compile_expression(stmt.start)
        self.emit(OpCode.STORE_LOCAL, var_index)

        loop_ctx = LoopContext()
        loop_ctx.continue_target = self.current_offset()
        self.loop_stack.append(loop_ctx)

        # Loop condition
        loop_start = self.current_offset()
        self.emit(OpCode.LOAD_LOCAL, var_index)
        self.compile_expression(stmt.end)
        if stmt.step == 1:
            self.emit(OpCode.LE)  # i <= end
        else:
            self.emit(OpCode.GE)  # i >= end (for down to)

        loop_exit = self.emit(OpCode.JUMP_IF_FALSE, 0)

        # Compile body
        for s in stmt.body:
            self.compile_statement(s)

        # Increment/decrement
        self.emit(OpCode.LOAD_LOCAL, var_index)
        self.emit(OpCode.PUSH_INT, 1)
        if stmt.step == 1:
            self.emit(OpCode.ADD)
        else:
            self.emit(OpCode.SUB)
        self.emit(OpCode.STORE_LOCAL, var_index)

        # Jump back
        self.emit(OpCode.JUMP, loop_start)
        self.patch_jump(loop_exit)

        # Patch breaks
        for break_jump in loop_ctx.break_jumps:
            self.patch_jump(break_jump)

        self.loop_stack.pop()

    def compile_foreach(self, stmt: ForEachStatement):
        """Compile a for-each statement."""
        # Create loop variable
        var_name = stmt.var_name
        self.local_vars[var_name] = self.local_count
        self.local_types[var_name] = self.type_to_string(stmt.var_type)
        var_index = self.local_count
        self.local_count += 1

        # Create index variable
        idx_index = self.local_count
        self.local_count += 1

        # Initialize index to 0
        self.emit(OpCode.PUSH_INT, 0)
        self.emit(OpCode.STORE_LOCAL, idx_index)

        # Get array reference
        self.compile_expression(stmt.iterable)
        arr_index = self.local_count
        self.local_count += 1
        self.emit(OpCode.STORE_LOCAL, arr_index)

        loop_ctx = LoopContext()
        loop_ctx.continue_target = self.current_offset()
        self.loop_stack.append(loop_ctx)

        # Loop condition: index < array.length
        loop_start = self.current_offset()
        self.emit(OpCode.LOAD_LOCAL, idx_index)
        self.emit(OpCode.LOAD_LOCAL, arr_index)
        self.emit(OpCode.ARRAY_LENGTH)
        self.emit(OpCode.LT)

        loop_exit = self.emit(OpCode.JUMP_IF_FALSE, 0)

        # Load current element
        self.emit(OpCode.LOAD_LOCAL, arr_index)
        self.emit(OpCode.LOAD_LOCAL, idx_index)
        self.emit(OpCode.ARRAY_GET)
        self.emit(OpCode.STORE_LOCAL, var_index)

        # Compile body
        for s in stmt.body:
            self.compile_statement(s)

        # Increment index
        self.emit(OpCode.LOAD_LOCAL, idx_index)
        self.emit(OpCode.PUSH_INT, 1)
        self.emit(OpCode.ADD)
        self.emit(OpCode.STORE_LOCAL, idx_index)

        # Jump back
        self.emit(OpCode.JUMP, loop_start)
        self.patch_jump(loop_exit)

        # Patch breaks
        for break_jump in loop_ctx.break_jumps:
            self.patch_jump(break_jump)

        self.loop_stack.pop()

    def compile_repeat(self, stmt: RepeatStatement):
        """Compile a repeat statement."""
        # Create counter variable
        counter_index = self.local_count
        self.local_count += 1

        # Initialize counter to 0
        self.emit(OpCode.PUSH_INT, 0)
        self.emit(OpCode.STORE_LOCAL, counter_index)

        # Compile limit expression once
        self.compile_expression(stmt.count)
        limit_index = self.local_count
        self.local_count += 1
        self.emit(OpCode.STORE_LOCAL, limit_index)

        loop_ctx = LoopContext()
        loop_ctx.continue_target = self.current_offset()
        self.loop_stack.append(loop_ctx)

        # Loop condition: counter < limit
        loop_start = self.current_offset()
        self.emit(OpCode.LOAD_LOCAL, counter_index)
        self.emit(OpCode.LOAD_LOCAL, limit_index)
        self.emit(OpCode.LT)

        loop_exit = self.emit(OpCode.JUMP_IF_FALSE, 0)

        # Compile body
        for s in stmt.body:
            self.compile_statement(s)

        # Increment counter
        self.emit(OpCode.LOAD_LOCAL, counter_index)
        self.emit(OpCode.PUSH_INT, 1)
        self.emit(OpCode.ADD)
        self.emit(OpCode.STORE_LOCAL, counter_index)

        # Jump back
        self.emit(OpCode.JUMP, loop_start)
        self.patch_jump(loop_exit)

        # Patch breaks
        for break_jump in loop_ctx.break_jumps:
            self.patch_jump(break_jump)

        self.loop_stack.pop()

    def compile_print(self, stmt: PrintStatement):
        """Compile a print statement."""
        # Compile each part and print it
        for i, part in enumerate(stmt.parts):
            self.compile_expression(part)
            self.emit(OpCode.PRINT)

        # Print newline
        self.emit(OpCode.PRINT_NEWLINE)

    def compile_input(self, stmt: InputStatement):
        """Compile an input statement."""
        # Determine input type
        if stmt.input_type == "number":
            self.emit(OpCode.INPUT_INT)
        elif stmt.input_type == "decimal":
            self.emit(OpCode.INPUT_FLOAT)
        elif stmt.input_type == "letter":
            self.emit(OpCode.INPUT_CHAR)
        else:
            self.emit(OpCode.INPUT_STRING)

        # Store in target
        if isinstance(stmt.target, Identifier):
            var_name = stmt.target.name
            if var_name in self.local_vars:
                self.emit(OpCode.STORE_LOCAL, self.local_vars[var_name])
            else:
                self.emit(OpCode.STORE_GLOBAL, var_name)

    def compile_return(self, stmt: ReturnStatement):
        """Compile a return statement."""
        if stmt.value:
            self.compile_expression(stmt.value)
            self.emit(OpCode.RETURN_VALUE)
        else:
            self.emit(OpCode.RETURN)

    def compile_break(self):
        """Compile a break statement."""
        if not self.loop_stack:
            raise SyntaxError("Break statement outside of loop")
        jump = self.emit(OpCode.JUMP, 0)
        self.loop_stack[-1].break_jumps.append(jump)

    def compile_continue(self):
        """Compile a continue statement."""
        if not self.loop_stack:
            raise SyntaxError("Continue statement outside of loop")
        self.emit(OpCode.JUMP, self.loop_stack[-1].continue_target)

    def compile_free(self, stmt: Free):
        """Compile a free statement."""
        self.compile_expression(stmt.pointer)
        self.emit(OpCode.FREE)

    def compile_expression(self, expr: Expression):
        """Compile an expression."""
        if isinstance(expr, NumberLiteral):
            self.emit(OpCode.PUSH_INT, expr.value)

        elif isinstance(expr, DecimalLiteral):
            self.emit(OpCode.PUSH_FLOAT, expr.value)

        elif isinstance(expr, StringLiteral):
            self.emit(OpCode.PUSH_STRING, expr.value)

        elif isinstance(expr, CharLiteral):
            self.emit(OpCode.PUSH_CHAR, expr.value)

        elif isinstance(expr, BoolLiteral):
            self.emit(OpCode.PUSH_BOOL, expr.value)

        elif isinstance(expr, NullLiteral):
            self.emit(OpCode.PUSH_NULL)

        elif isinstance(expr, Identifier):
            var_name = expr.name
            if var_name in self.local_vars:
                self.emit(OpCode.LOAD_LOCAL, self.local_vars[var_name])
            else:
                self.emit(OpCode.LOAD_GLOBAL, var_name)

        elif isinstance(expr, BinaryOp):
            self.compile_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            self.compile_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            self.compile_function_call(expr)

        elif isinstance(expr, ArrayAccess):
            self.compile_expression(expr.array)
            self.compile_expression(expr.index)
            self.emit(OpCode.ARRAY_GET)

        elif isinstance(expr, MemberAccess):
            self.compile_expression(expr.object)
            self.emit(OpCode.STRUCT_GET, expr.member)

        elif isinstance(expr, AddressOf):
            # For address-of, we emit a special marker
            if isinstance(expr.operand, Identifier):
                var_name = expr.operand.name
                if var_name in self.local_vars:
                    self.emit(OpCode.ADDRESS_OF, ("local", self.local_vars[var_name]))
                else:
                    self.emit(OpCode.ADDRESS_OF, ("global", var_name))

        elif isinstance(expr, Dereference):
            self.compile_expression(expr.operand)
            self.emit(OpCode.LOAD_PTR)

        elif isinstance(expr, ArrayLiteral):
            for elem in expr.elements:
                self.compile_expression(elem)
            self.emit(OpCode.ARRAY_LITERAL, len(expr.elements))

        elif isinstance(expr, Allocate):
            self.compile_expression(expr.count)
            type_name = self.type_to_string(expr.alloc_type)
            self.emit(OpCode.ALLOC, type_name)

        elif isinstance(expr, RandomNumber):
            self.compile_expression(expr.min_val)
            self.compile_expression(expr.max_val)
            self.emit(OpCode.RANDOM)

        # GUI expressions
        elif isinstance(expr, WindowShouldClose):
            self.emit(OpCode.CALL, ("__window_should_close__", 0))

        elif isinstance(expr, MouseX):
            self.emit(OpCode.CALL, ("__mouse_x__", 0))

        elif isinstance(expr, MouseY):
            self.emit(OpCode.CALL, ("__mouse_y__", 0))

        elif isinstance(expr, MousePressed):
            self.emit(OpCode.CALL, ("__mouse_pressed__", 0))

    def compile_binary_op(self, expr: BinaryOp):
        """Compile a binary operation."""
        # Short-circuit evaluation for && and ||
        if expr.operator == "&&":
            self.compile_expression(expr.left)
            self.emit(OpCode.DUP)
            jump_false = self.emit(OpCode.JUMP_IF_FALSE, 0)
            self.emit(OpCode.POP)
            self.compile_expression(expr.right)
            self.patch_jump(jump_false)
            return

        if expr.operator == "||":
            self.compile_expression(expr.left)
            self.emit(OpCode.DUP)
            jump_true = self.emit(OpCode.JUMP_IF_TRUE, 0)
            self.emit(OpCode.POP)
            self.compile_expression(expr.right)
            self.patch_jump(jump_true)
            return

        # Regular binary operations
        self.compile_expression(expr.left)
        self.compile_expression(expr.right)

        op_map = {
            "+": OpCode.ADD,
            "-": OpCode.SUB,
            "*": OpCode.MUL,
            "/": OpCode.DIV,
            "%": OpCode.MOD,
            "==": OpCode.EQ,
            "!=": OpCode.NE,
            "<": OpCode.LT,
            "<=": OpCode.LE,
            ">": OpCode.GT,
            ">=": OpCode.GE,
        }

        if expr.operator in op_map:
            self.emit(op_map[expr.operator])
        else:
            raise SyntaxError(f"Unknown binary operator: {expr.operator}")

    def compile_unary_op(self, expr: UnaryOp):
        """Compile a unary operation."""
        self.compile_expression(expr.operand)

        if expr.operator == "-":
            self.emit(OpCode.NEG)
        elif expr.operator == "!":
            self.emit(OpCode.NOT)
        else:
            raise SyntaxError(f"Unknown unary operator: {expr.operator}")

    def compile_function_call(self, expr: FunctionCall):
        """Compile a function call."""
        name = expr.name

        # Handle built-in functions
        if name == "__len__":
            if expr.arguments:
                self.compile_expression(expr.arguments[0])
                self.emit(OpCode.ARRAY_LENGTH)
            else:
                self.emit(OpCode.PUSH_INT, 0)
            return

        if name == "sqrt":
            self.compile_expression(expr.arguments[0])
            self.emit(OpCode.SQRT)
            return

        if name == "abs":
            self.compile_expression(expr.arguments[0])
            self.emit(OpCode.ABS)
            return

        if name == "pow":
            self.compile_expression(expr.arguments[0])
            self.compile_expression(expr.arguments[1])
            self.emit(OpCode.POW)
            return

        if name == "strstr":
            # String contains check
            self.compile_expression(expr.arguments[0])
            self.compile_expression(expr.arguments[1])
            self.emit(OpCode.CALL, ("__strstr__", 2))
            return

        if name == "__has_line__":
            self.compile_expression(expr.arguments[0])
            self.emit(OpCode.CALL, ("__has_line__", 1))
            return

        if name == "__read_line__":
            self.compile_expression(expr.arguments[0])
            self.compile_expression(expr.arguments[1])
            self.emit(OpCode.CALL, ("__read_line__", 2))
            return

        if name == "fclose":
            self.compile_expression(expr.arguments[0])
            self.emit(OpCode.CALL, ("__close_file__", 1))
            return

        # Regular function call
        for arg in expr.arguments:
            self.compile_expression(arg)

        self.emit(OpCode.CALL, (name, len(expr.arguments)))

    # GUI compilation methods
    def compile_open_window(self, stmt: OpenWindow):
        self.compile_expression(stmt.width)
        self.compile_expression(stmt.height)
        if stmt.title:
            self.compile_expression(stmt.title)
        else:
            self.emit(OpCode.PUSH_STRING, "Zinc App")
        self.emit(OpCode.CALL, ("__open_window__", 3))
        self.emit(OpCode.POP)

    def compile_draw_rectangle(self, stmt: DrawRectangle):
        self.compile_expression(stmt.x)
        self.compile_expression(stmt.y)
        self.compile_expression(stmt.width)
        self.compile_expression(stmt.height)
        self.emit(OpCode.PUSH_STRING, stmt.color)
        self.emit(OpCode.CALL, ("__draw_rectangle__", 5))
        self.emit(OpCode.POP)

    def compile_draw_text(self, stmt: DrawText):
        self.compile_expression(stmt.text)
        self.compile_expression(stmt.x)
        self.compile_expression(stmt.y)
        self.compile_expression(stmt.size)
        self.emit(OpCode.PUSH_STRING, stmt.color)
        self.emit(OpCode.CALL, ("__draw_text__", 5))
        self.emit(OpCode.POP)


def compile_program(source: str) -> CompiledProgram:
    """Convenience function to compile Zinc source to bytecode."""
    program = parse(source)
    compiler = Compiler()
    return compiler.compile(program)


if __name__ == "__main__":
    test_code = '''
include the standard input and output

to do the main thing:
    there is a number called x which is 5
    say "Hello, World!"
    if x is greater than 3 then
        say "x is big"
    end
end
'''

    compiled = compile_program(test_code)
    print(compiled.disassemble())
