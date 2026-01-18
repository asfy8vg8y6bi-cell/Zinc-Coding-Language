"""
Zinc Transpiler - Converts AST to C code.
"""

from typing import List, Dict, Optional, Set
from parser import (
    ASTNode, Program, Include, StructDef, FunctionDef, TypeSpec, VarDecl,
    Statement, ExpressionStmt, Assignment, IfStatement, ElseIfClause,
    WhileStatement, ForStatement, ForEachStatement, RepeatStatement,
    ReturnStatement, BreakStatement, ContinueStatement, PrintStatement,
    InputStatement, Expression, BinaryOp, UnaryOp, NumberLiteral,
    DecimalLiteral, StringLiteral, CharLiteral, BoolLiteral, NullLiteral,
    Identifier, FunctionCall, ArrayAccess, MemberAccess, AddressOf,
    Dereference, ArrayLiteral, Allocate, Free, RandomNumber,
    # GUI types
    OpenWindow, CloseWindow, BeginDrawing, EndDrawing, ClearScreen,
    DrawRectangle, DrawText, WindowShouldClose, MouseX, MouseY, MousePressed,
    parse
)


class Transpiler:
    def __init__(self):
        self.indent_level = 0
        self.output_lines: List[str] = []
        self.includes: Set[str] = set()
        self.struct_names: Set[str] = set()
        self.array_vars: Dict[str, int] = {}  # var_name -> size
        self.current_func_vars: Dict[str, TypeSpec] = {}

    def indent(self) -> str:
        return "    " * self.indent_level

    def emit(self, line: str):
        self.output_lines.append(self.indent() + line)

    def emit_raw(self, line: str):
        self.output_lines.append(line)

    def transpile(self, program: Program) -> str:
        self.output_lines = []
        self.includes = set()

        # Collect all includes
        for inc in program.includes:
            self.includes.add(inc.library)

        # Always include stdio for printf/scanf
        self.includes.add("stdio")

        # Emit includes
        for inc in sorted(self.includes):
            if inc == "raylib":
                self.emit_raw(f'#include "raylib.h"')
            else:
                self.emit_raw(f"#include <{inc}.h>")

        self.emit_raw("")

        # Emit struct definitions
        for struct in program.structures:
            self.struct_names.add(struct.name)
            self.transpile_struct(struct)

        # Forward declare functions
        for func in program.functions:
            if not func.is_main:
                self.emit_forward_decl(func)

        if program.functions:
            self.emit_raw("")

        # Emit function definitions
        for func in program.functions:
            self.transpile_function(func)
            self.emit_raw("")

        return "\n".join(self.output_lines)

    def emit_forward_decl(self, func: FunctionDef):
        return_type = self.type_to_c(func.return_type) if func.return_type else "void"
        params = ", ".join(
            f"{self.type_to_c(p.var_type)} {p.name}" for p in func.params
        ) or "void"
        self.emit_raw(f"{return_type} {func.name}({params});")

    def transpile_struct(self, struct: StructDef):
        self.emit_raw(f"typedef struct {{")
        self.indent_level += 1
        for field in struct.fields:
            field_type = self.type_to_c(field.var_type)
            self.emit(f"{field_type} {field.name};")
        self.indent_level -= 1
        self.emit_raw(f"}} {struct.name};")
        self.emit_raw("")

    def transpile_function(self, func: FunctionDef):
        self.current_func_vars = {}
        self.array_vars = {}

        if func.is_main:
            self.emit_raw("int main(void) {")
        else:
            return_type = self.type_to_c(func.return_type) if func.return_type else "void"
            params = ", ".join(
                f"{self.type_to_c(p.var_type)} {p.name}" for p in func.params
            ) or "void"
            self.emit_raw(f"{return_type} {func.name}({params}) {{")

        self.indent_level += 1

        for stmt in func.body:
            self.transpile_statement(stmt)

        # Add return 0 for main if not present
        if func.is_main:
            if not func.body or not isinstance(func.body[-1], ReturnStatement):
                self.emit("return 0;")

        self.indent_level -= 1
        self.emit_raw("}")

    def type_to_c(self, type_spec: Optional[TypeSpec]) -> str:
        if type_spec is None:
            return "int"

        base = ""
        if type_spec.base_type == "number":
            base = "int"
        elif type_spec.base_type == "decimal":
            base = "double"
        elif type_spec.base_type == "text":
            base = "char*"
        elif type_spec.base_type == "letter":
            base = "char"
        elif type_spec.base_type == "boolean":
            base = "int"
        elif type_spec.base_type == "nothing":
            base = "void"
        elif type_spec.base_type == "struct":
            base = type_spec.struct_name
        elif type_spec.base_type == "file":
            base = "FILE*"
        else:
            base = "int"

        if type_spec.is_pointer:
            base += "*"

        return base

    def transpile_statement(self, stmt: Statement):
        if isinstance(stmt, VarDecl):
            self.transpile_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            self.transpile_assignment(stmt)
        elif isinstance(stmt, IfStatement):
            self.transpile_if(stmt)
        elif isinstance(stmt, WhileStatement):
            self.transpile_while(stmt)
        elif isinstance(stmt, ForStatement):
            self.transpile_for(stmt)
        elif isinstance(stmt, ForEachStatement):
            self.transpile_foreach(stmt)
        elif isinstance(stmt, RepeatStatement):
            self.transpile_repeat(stmt)
        elif isinstance(stmt, PrintStatement):
            self.transpile_print(stmt)
        elif isinstance(stmt, InputStatement):
            self.transpile_input(stmt)
        elif isinstance(stmt, ReturnStatement):
            self.transpile_return(stmt)
        elif isinstance(stmt, BreakStatement):
            self.emit("break;")
        elif isinstance(stmt, ContinueStatement):
            self.emit("continue;")
        elif isinstance(stmt, Free):
            self.transpile_free(stmt)
        # GUI statements
        elif isinstance(stmt, OpenWindow):
            self.transpile_open_window(stmt)
        elif isinstance(stmt, CloseWindow):
            self.emit("CloseWindow();")
        elif isinstance(stmt, BeginDrawing):
            self.emit("BeginDrawing();")
        elif isinstance(stmt, EndDrawing):
            self.emit("EndDrawing();")
        elif isinstance(stmt, ClearScreen):
            self.emit(f"ClearBackground({stmt.color});")
        elif isinstance(stmt, DrawRectangle):
            self.transpile_draw_rectangle(stmt)
        elif isinstance(stmt, DrawText):
            self.transpile_draw_text(stmt)
        elif isinstance(stmt, ExpressionStmt):
            expr_code = self.transpile_expression(stmt.expression)
            self.emit(f"{expr_code};")

    def transpile_var_decl(self, decl: VarDecl):
        if decl.is_file:
            # File declaration
            if decl.file_path:
                mode = '"r"' if decl.file_mode == "read" else '"w"'
                path = self.transpile_expression(decl.file_path)
                self.emit(f"FILE* {decl.name} = fopen({path}, {mode});")
            else:
                self.emit(f"FILE* {decl.name} = NULL;")
            return

        c_type = self.type_to_c(decl.var_type)

        # Track variable type
        if decl.var_type:
            self.current_func_vars[decl.name] = decl.var_type

        if decl.var_type and decl.var_type.is_array:
            # Array declaration
            if isinstance(decl.initial_value, ArrayLiteral):
                elements = ", ".join(
                    self.transpile_expression(e) for e in decl.initial_value.elements
                )
                size = len(decl.initial_value.elements)
                self.array_vars[decl.name] = size
                # For arrays with initializers, use the element type
                elem_type = c_type.rstrip("*")
                self.emit(f"{elem_type} {decl.name}[{size}] = {{{elements}}};")
            elif decl.var_type.array_size:
                size = decl.var_type.array_size
                self.array_vars[decl.name] = size
                elem_type = c_type.rstrip("*")
                self.emit(f"{elem_type} {decl.name}[{size}];")
            else:
                # Dynamic array - use pointer
                self.emit(f"{c_type}* {decl.name} = NULL;")
        elif decl.initial_value:
            init = self.transpile_expression(decl.initial_value)

            # Handle allocate expressions
            if isinstance(decl.initial_value, Allocate):
                self.emit(f"{c_type}* {decl.name} = {init};")
            else:
                self.emit(f"{c_type} {decl.name} = {init};")
        else:
            # Default initialization
            if c_type == "char*":
                self.emit(f"{c_type} {decl.name} = NULL;")
            elif c_type.endswith("*"):
                self.emit(f"{c_type} {decl.name} = NULL;")
            elif decl.var_type and decl.var_type.base_type == "struct":
                # Struct initialization
                self.emit(f"{c_type} {decl.name} = {{0}};")
            else:
                self.emit(f"{c_type} {decl.name} = 0;")

    def transpile_assignment(self, assign: Assignment):
        target = self.transpile_expression(assign.target)
        value = self.transpile_expression(assign.value)
        self.emit(f"{target} = {value};")

    def transpile_if(self, stmt: IfStatement):
        cond = self.transpile_expression(stmt.condition)
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        for s in stmt.then_body:
            self.transpile_statement(s)
        self.indent_level -= 1

        for else_if in stmt.else_if_clauses:
            cond = self.transpile_expression(else_if.condition)
            self.emit(f"}} else if ({cond}) {{")
            self.indent_level += 1
            for s in else_if.body:
                self.transpile_statement(s)
            self.indent_level -= 1

        if stmt.else_body:
            self.emit("} else {")
            self.indent_level += 1
            for s in stmt.else_body:
                self.transpile_statement(s)
            self.indent_level -= 1

        self.emit("}")

    def transpile_while(self, stmt: WhileStatement):
        cond = self.transpile_expression(stmt.condition)
        self.emit(f"while ({cond}) {{")
        self.indent_level += 1
        for s in stmt.body:
            self.transpile_statement(s)
        self.indent_level -= 1
        self.emit("}")

    def transpile_for(self, stmt: ForStatement):
        var = stmt.var_name
        start = self.transpile_expression(stmt.start)
        end = self.transpile_expression(stmt.end)

        if stmt.step == 1:
            self.emit(f"for (int {var} = {start}; {var} <= {end}; {var}++) {{")
        else:
            self.emit(f"for (int {var} = {start}; {var} >= {end}; {var}--) {{")

        self.indent_level += 1
        for s in stmt.body:
            self.transpile_statement(s)
        self.indent_level -= 1
        self.emit("}")

    def transpile_foreach(self, stmt: ForEachStatement):
        var = stmt.var_name
        iterable = self.transpile_expression(stmt.iterable)
        var_type = self.type_to_c(stmt.var_type)

        # Get array size if known
        if isinstance(stmt.iterable, Identifier) and stmt.iterable.name in self.array_vars:
            size = self.array_vars[stmt.iterable.name]
            self.emit(f"for (int __i__ = 0; __i__ < {size}; __i__++) {{")
            self.indent_level += 1
            self.emit(f"{var_type} {var} = {iterable}[__i__];")
        else:
            # Unknown size - need runtime length
            self.emit(f"for (int __i__ = 0; __i__ < sizeof({iterable})/sizeof({iterable}[0]); __i__++) {{")
            self.indent_level += 1
            self.emit(f"{var_type} {var} = {iterable}[__i__];")

        for s in stmt.body:
            self.transpile_statement(s)
        self.indent_level -= 1
        self.emit("}")

    def transpile_repeat(self, stmt: RepeatStatement):
        count = self.transpile_expression(stmt.count)
        self.emit(f"for (int __rep__ = 0; __rep__ < {count}; __rep__++) {{")
        self.indent_level += 1
        for s in stmt.body:
            self.transpile_statement(s)
        self.indent_level -= 1
        self.emit("}")

    def transpile_print(self, stmt: PrintStatement):
        # Build printf format string and arguments
        format_parts = []
        args = []

        for part in stmt.parts:
            if isinstance(part, StringLiteral):
                # Escape the string for C
                escaped = part.value.replace("\\", "\\\\").replace('"', '\\"')
                format_parts.append(escaped)
            elif isinstance(part, NumberLiteral):
                format_parts.append("%d")
                args.append(str(part.value))
            elif isinstance(part, DecimalLiteral):
                format_parts.append("%f")
                args.append(str(part.value))
            elif isinstance(part, CharLiteral):
                format_parts.append("%c")
                args.append(f"'{part.value}'")
            elif isinstance(part, Identifier):
                # Determine type from context
                var_type = self.current_func_vars.get(part.name)
                if var_type:
                    if var_type.base_type == "text":
                        format_parts.append("%s")
                    elif var_type.base_type == "decimal":
                        format_parts.append("%f")
                    elif var_type.base_type == "letter":
                        format_parts.append("%c")
                    else:
                        format_parts.append("%d")
                else:
                    format_parts.append("%d")  # default to int
                args.append(part.name)
            else:
                # Complex expression - default to %d
                expr = self.transpile_expression(part)
                format_parts.append("%d")
                args.append(expr)

        format_str = "".join(format_parts)
        if args:
            args_str = ", " + ", ".join(args)
        else:
            args_str = ""

        self.emit(f'printf("{format_str}\\n"{args_str});')

    def transpile_input(self, stmt: InputStatement):
        target = self.transpile_expression(stmt.target)

        if stmt.input_type == "number":
            self.emit(f'scanf("%d", &{target});')
        elif stmt.input_type == "decimal":
            self.emit(f'scanf("%lf", &{target});')
        elif stmt.input_type == "letter":
            self.emit(f'scanf(" %c", &{target});')
        else:  # text
            # Need to allocate buffer first
            self.emit(f'char __buf__[256];')
            self.emit(f'scanf("%255s", __buf__);')
            self.emit(f'{target} = __buf__;')

    def transpile_return(self, stmt: ReturnStatement):
        if stmt.value:
            value = self.transpile_expression(stmt.value)
            self.emit(f"return {value};")
        else:
            self.emit("return;")

    def transpile_free(self, stmt: Free):
        ptr = self.transpile_expression(stmt.pointer)
        self.emit(f"free({ptr});")

    def transpile_expression(self, expr: Expression) -> str:
        if isinstance(expr, NumberLiteral):
            return str(expr.value)
        elif isinstance(expr, DecimalLiteral):
            return str(expr.value)
        elif isinstance(expr, StringLiteral):
            escaped = expr.value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(expr, CharLiteral):
            if expr.value == '\n':
                return "'\\n'"
            elif expr.value == '\t':
                return "'\\t'"
            else:
                return f"'{expr.value}'"
        elif isinstance(expr, BoolLiteral):
            return "1" if expr.value else "0"
        elif isinstance(expr, NullLiteral):
            return "NULL"
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryOp):
            left = self.transpile_expression(expr.left)
            right = self.transpile_expression(expr.right)
            return f"({left} {expr.operator} {right})"
        elif isinstance(expr, UnaryOp):
            operand = self.transpile_expression(expr.operand)
            return f"({expr.operator}{operand})"
        elif isinstance(expr, FunctionCall):
            return self.transpile_function_call(expr)
        elif isinstance(expr, ArrayAccess):
            array = self.transpile_expression(expr.array)
            index = self.transpile_expression(expr.index)
            # Handle -1 as last index
            if isinstance(expr.index, NumberLiteral) and expr.index.value == -1:
                if isinstance(expr.array, Identifier) and expr.array.name in self.array_vars:
                    size = self.array_vars[expr.array.name]
                    return f"{array}[{size - 1}]"
                return f"{array}[sizeof({array})/sizeof({array}[0]) - 1]"
            return f"{array}[{index}]"
        elif isinstance(expr, MemberAccess):
            obj = self.transpile_expression(expr.object)
            # Check if object is a pointer
            if isinstance(expr.object, Identifier):
                var_type = self.current_func_vars.get(expr.object.name)
                if var_type and var_type.is_pointer:
                    return f"{obj}->{expr.member}"
            return f"{obj}.{expr.member}"
        elif isinstance(expr, AddressOf):
            operand = self.transpile_expression(expr.operand)
            return f"&{operand}"
        elif isinstance(expr, Dereference):
            operand = self.transpile_expression(expr.operand)
            return f"*{operand}"
        elif isinstance(expr, ArrayLiteral):
            elements = ", ".join(self.transpile_expression(e) for e in expr.elements)
            return f"{{{elements}}}"
        elif isinstance(expr, Allocate):
            count = self.transpile_expression(expr.count)
            c_type = self.type_to_c(expr.alloc_type)
            return f"malloc({count} * sizeof({c_type}))"
        elif isinstance(expr, RandomNumber):
            min_val = self.transpile_expression(expr.min_val)
            max_val = self.transpile_expression(expr.max_val)
            self.includes.add("stdlib")
            self.includes.add("time")
            return f"(rand() % ({max_val} - {min_val} + 1) + {min_val})"
        # GUI expressions
        elif isinstance(expr, WindowShouldClose):
            return "WindowShouldClose()"
        elif isinstance(expr, MouseX):
            return "GetMouseX()"
        elif isinstance(expr, MouseY):
            return "GetMouseY()"
        elif isinstance(expr, MousePressed):
            return "IsMouseButtonPressed(MOUSE_LEFT_BUTTON)"
        else:
            return "0"

    def transpile_function_call(self, call: FunctionCall) -> str:
        name = call.name

        # Handle special built-in functions
        if name == "__len__":
            if call.arguments:
                arr = self.transpile_expression(call.arguments[0])
                if isinstance(call.arguments[0], Identifier):
                    var_name = call.arguments[0].name
                    if var_name in self.array_vars:
                        return str(self.array_vars[var_name])
                return f"(sizeof({arr})/sizeof({arr}[0]))"
            return "0"
        elif name == "__has_line__":
            if call.arguments:
                file_var = self.transpile_expression(call.arguments[0])
                return f"!feof({file_var})"
            return "0"
        elif name == "__read_line__":
            if len(call.arguments) >= 2:
                file_var = self.transpile_expression(call.arguments[0])
                target = self.transpile_expression(call.arguments[1])
                return f"fgets({target}, sizeof({target}), {file_var})"
            return "NULL"
        elif name == "strstr":
            # String contains - returns non-null if found
            if len(call.arguments) >= 2:
                haystack = self.transpile_expression(call.arguments[0])
                needle = self.transpile_expression(call.arguments[1])
                self.includes.add("string")
                return f"(strstr({haystack}, {needle}) != NULL)"
            return "0"

        # Regular function call
        args = ", ".join(self.transpile_expression(a) for a in call.arguments)
        return f"{name}({args})"

    # GUI transpile methods
    def transpile_open_window(self, stmt: OpenWindow):
        width = self.transpile_expression(stmt.width)
        height = self.transpile_expression(stmt.height)
        title = self.transpile_expression(stmt.title) if stmt.title else '"Zinc App"'
        self.emit(f"InitWindow({width}, {height}, {title});")
        self.emit("SetTargetFPS(60);")

    def transpile_draw_rectangle(self, stmt: DrawRectangle):
        x = self.transpile_expression(stmt.x)
        y = self.transpile_expression(stmt.y)
        w = self.transpile_expression(stmt.width)
        h = self.transpile_expression(stmt.height)
        self.emit(f"DrawRectangle({x}, {y}, {w}, {h}, {stmt.color});")

    def transpile_draw_text(self, stmt: DrawText):
        text = self.transpile_expression(stmt.text)
        x = self.transpile_expression(stmt.x)
        y = self.transpile_expression(stmt.y)
        size = self.transpile_expression(stmt.size)
        self.emit(f"DrawText({text}, {x}, {y}, {size}, {stmt.color});")


def transpile(source: str) -> str:
    """Convenience function to transpile Zinc source to C."""
    program = parse(source)
    transpiler = Transpiler()
    return transpiler.transpile(program)


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

    c_code = transpile(test_code)
    print("Generated C code:")
    print(c_code)
