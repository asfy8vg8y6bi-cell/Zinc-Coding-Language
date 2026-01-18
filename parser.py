"""
Zinc Parser - Builds an AST from tokens, handling flexible English syntax.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Union
from lexer import Token, TokenType, tokenize


# AST Node Types
@dataclass
class ASTNode:
    line: int = 0


@dataclass
class Program(ASTNode):
    includes: List['Include'] = field(default_factory=list)
    structures: List['StructDef'] = field(default_factory=list)
    functions: List['FunctionDef'] = field(default_factory=list)


@dataclass
class Include(ASTNode):
    library: str = ""


@dataclass
class StructDef(ASTNode):
    name: str = ""
    fields: List['VarDecl'] = field(default_factory=list)


@dataclass
class FunctionDef(ASTNode):
    name: str = ""
    params: List['VarDecl'] = field(default_factory=list)
    return_type: Optional['TypeSpec'] = None
    body: List['Statement'] = field(default_factory=list)
    is_main: bool = False


@dataclass
class TypeSpec(ASTNode):
    base_type: str = ""  # "number", "decimal", "text", "letter", "boolean", "nothing"
    is_pointer: bool = False
    is_array: bool = False
    array_size: Optional[int] = None
    struct_name: Optional[str] = None  # For custom struct types


@dataclass
class VarDecl(ASTNode):
    name: str = ""
    var_type: Optional[TypeSpec] = None
    initial_value: Optional['Expression'] = None
    is_file: bool = False
    file_path: Optional['Expression'] = None
    file_mode: str = ""  # "read" or "write"


@dataclass
class Statement(ASTNode):
    pass


@dataclass
class ExpressionStmt(Statement):
    expression: 'Expression' = None


@dataclass
class Assignment(Statement):
    target: 'Expression' = None
    value: 'Expression' = None
    operator: str = "="  # =, +=, -=, *=, /=


@dataclass
class IfStatement(Statement):
    condition: 'Expression' = None
    then_body: List[Statement] = field(default_factory=list)
    else_if_clauses: List['ElseIfClause'] = field(default_factory=list)
    else_body: List[Statement] = field(default_factory=list)


@dataclass
class ElseIfClause(ASTNode):
    condition: 'Expression' = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class WhileStatement(Statement):
    condition: 'Expression' = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class ForStatement(Statement):
    var_name: str = ""
    var_type: Optional[TypeSpec] = None
    start: 'Expression' = None
    end: 'Expression' = None
    step: int = 1  # 1 for ascending, -1 for descending
    body: List[Statement] = field(default_factory=list)


@dataclass
class ForEachStatement(Statement):
    var_name: str = ""
    var_type: Optional[TypeSpec] = None
    iterable: 'Expression' = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class RepeatStatement(Statement):
    count: 'Expression' = None
    body: List[Statement] = field(default_factory=list)


@dataclass
class ReturnStatement(Statement):
    value: Optional['Expression'] = None


@dataclass
class BreakStatement(Statement):
    pass


@dataclass
class ContinueStatement(Statement):
    pass


@dataclass
class PrintStatement(Statement):
    parts: List['Expression'] = field(default_factory=list)


@dataclass
class InputStatement(Statement):
    target: 'Expression' = None
    input_type: str = ""  # "number", "decimal", "text", "letter"


# GUI Statements
@dataclass
class OpenWindow(Statement):
    width: 'Expression' = None
    height: 'Expression' = None
    title: 'Expression' = None


@dataclass
class CloseWindow(Statement):
    pass


@dataclass
class BeginDrawing(Statement):
    pass


@dataclass
class EndDrawing(Statement):
    pass


@dataclass
class ClearScreen(Statement):
    color: str = "RAYWHITE"


@dataclass
class DrawRectangle(Statement):
    x: 'Expression' = None
    y: 'Expression' = None
    width: 'Expression' = None
    height: 'Expression' = None
    color: str = "LIGHTGRAY"


@dataclass
class DrawText(Statement):
    text: 'Expression' = None
    x: 'Expression' = None
    y: 'Expression' = None
    size: 'Expression' = None
    color: str = "BLACK"


@dataclass
class Expression(ASTNode):
    pass


@dataclass
class BinaryOp(Expression):
    left: Expression = None
    operator: str = ""
    right: Expression = None


@dataclass
class UnaryOp(Expression):
    operator: str = ""
    operand: Expression = None


@dataclass
class NumberLiteral(Expression):
    value: int = 0


@dataclass
class DecimalLiteral(Expression):
    value: float = 0.0


@dataclass
class StringLiteral(Expression):
    value: str = ""


@dataclass
class CharLiteral(Expression):
    value: str = ""


@dataclass
class BoolLiteral(Expression):
    value: bool = False


@dataclass
class NullLiteral(Expression):
    pass


@dataclass
class Identifier(Expression):
    name: str = ""


@dataclass
class FunctionCall(Expression):
    name: str = ""
    arguments: List[Expression] = field(default_factory=list)


@dataclass
class ArrayAccess(Expression):
    array: Expression = None
    index: Expression = None


@dataclass
class MemberAccess(Expression):
    object: Expression = None
    member: str = ""


@dataclass
class AddressOf(Expression):
    operand: Expression = None


@dataclass
class Dereference(Expression):
    operand: Expression = None


@dataclass
class ArrayLiteral(Expression):
    elements: List[Expression] = field(default_factory=list)


@dataclass
class Allocate(Expression):
    alloc_type: TypeSpec = None
    count: Expression = None


@dataclass
class Free(Statement):
    pointer: Expression = None


@dataclass
class RandomNumber(Expression):
    min_val: Expression = None
    max_val: Expression = None


# GUI Expressions
@dataclass
class WindowShouldClose(Expression):
    pass


@dataclass
class MouseX(Expression):
    pass


@dataclass
class MouseY(Expression):
    pass


@dataclass
class MousePressed(Expression):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_line = 1

    def error(self, msg: str):
        token = self.current()
        raise SyntaxError(f"Parse error at line {token.line}: {msg} (got {token.type.name}: {token.value!r})")

    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF

    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        token = self.current()
        self.pos += 1
        self.current_line = token.line
        return token

    def match(self, *types: TokenType) -> bool:
        return self.current().type in types

    def expect(self, *types: TokenType) -> Token:
        if self.match(*types):
            return self.advance()
        expected = " or ".join(t.name for t in types)
        self.error(f"Expected {expected}")

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()

    def skip_optional(self, *types: TokenType):
        while self.match(*types):
            self.advance()

    def parse(self) -> Program:
        program = Program(line=1)

        self.skip_newlines()

        while not self.match(TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.EOF):
                break

            if self.match(TokenType.INCLUDE, TokenType.USE):
                program.includes.append(self.parse_include())
            elif self.match(TokenType.DEFINE):
                program.structures.append(self.parse_struct())
            elif self.match(TokenType.TO_FUNC, TokenType.TO):
                program.functions.append(self.parse_function())
            elif self.match(TokenType.NOTE, TokenType.NOTES, TokenType.REMINDER):
                self.parse_comment()
            else:
                self.error(f"Unexpected token at top level: {self.current().type.name}")

            self.skip_newlines()

        return program

    def parse_include(self) -> Include:
        line = self.current().line
        self.advance()  # include/use

        if self.match(TokenType.STANDARD_IO):
            self.advance()
            return Include(library="stdio", line=line)
        elif self.match(TokenType.STANDARD_MATH):
            self.advance()
            return Include(library="math", line=line)
        elif self.match(TokenType.STRING_FUNCTIONS):
            self.advance()
            return Include(library="string", line=line)
        elif self.match(TokenType.FILE_FUNCTIONS):
            self.advance()
            return Include(library="stdio", line=line)  # FILE is in stdio
        elif self.match(TokenType.RANDOM_FUNCTIONS):
            self.advance()
            return Include(library="stdlib", line=line)
        elif self.match(TokenType.RAYLIB_GRAPHICS):
            self.advance()
            return Include(library="raylib", line=line)
        elif self.match(TokenType.FILE_CALLED):
            self.advance()
            name = self.expect(TokenType.STRING_LITERAL, TokenType.IDENTIFIER).value
            return Include(library=name, line=line)
        elif self.match(TokenType.THE):
            self.advance()
            if self.match(TokenType.FILE_CALLED):
                self.advance()
                name = self.expect(TokenType.STRING_LITERAL, TokenType.IDENTIFIER).value
                return Include(library=name, line=line)

        self.error("Expected library name after include")

    def parse_struct(self) -> StructDef:
        line = self.current().line
        self.advance()  # define

        self.skip_optional(TokenType.A, TokenType.AN)
        name = self.expect(TokenType.IDENTIFIER).value

        self.expect(TokenType.AS_HAVING)
        self.skip_optional(TokenType.COLON)
        self.skip_newlines()

        fields = []
        while not self.match(TokenType.END, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.END):
                break
            field_type = self.parse_type()
            self.expect(TokenType.CALLED)
            field_name = self.expect(TokenType.IDENTIFIER).value
            fields.append(VarDecl(name=field_name, var_type=field_type, line=self.current_line))
            self.skip_newlines()

        self.expect(TokenType.END)

        return StructDef(name=name, fields=fields, line=line)

    def parse_function(self) -> FunctionDef:
        line = self.current().line
        self.advance()  # to

        # Check for "do the main thing"
        if self.match(TokenType.DO_MAIN):
            self.advance()
            self.skip_optional(TokenType.COLON)
            self.skip_newlines()
            body = self.parse_block()
            return FunctionDef(name="main", is_main=True, body=body, line=line,
                             return_type=TypeSpec(base_type="number"))

        # Parse function name (can be multiple words)
        name_parts = []
        params = []
        return_type = None

        # Parse until we hit a colon or "and return"
        while not self.match(TokenType.COLON, TokenType.AND_RETURN, TokenType.EOF):
            if self.match(TokenType.NEWLINE):
                break

            # Check for parameter types
            if self.match(TokenType.NUMBER, TokenType.DECIMAL, TokenType.TEXT,
                         TokenType.LETTER, TokenType.YES_OR_NO, TokenType.BOOLEAN,
                         TokenType.POINTER_TO, TokenType.LIST_OF):
                # This is a parameter
                param_type = self.parse_type()

                # Check for "called" keyword
                if self.match(TokenType.CALLED):
                    self.advance()

                param_name = self.expect(TokenType.IDENTIFIER).value
                params.append(VarDecl(name=param_name, var_type=param_type, line=self.current_line))

                # Skip "and" between parameters
                self.skip_optional(TokenType.AND, TokenType.COMMA)
            elif self.match(TokenType.IDENTIFIER):
                # Check if this might be a struct type
                next_token = self.peek(1)
                if next_token.type in (TokenType.CALLED, TokenType.POINTER_TO):
                    # This is a parameter with struct type
                    struct_name = self.advance().value
                    param_type = TypeSpec(base_type="struct", struct_name=struct_name)
                    if self.match(TokenType.POINTER_TO):
                        self.advance()
                        param_type.is_pointer = True
                    if self.match(TokenType.CALLED):
                        self.advance()
                    param_name = self.expect(TokenType.IDENTIFIER).value
                    params.append(VarDecl(name=param_name, var_type=param_type, line=self.current_line))
                    self.skip_optional(TokenType.AND, TokenType.COMMA)
                else:
                    name_parts.append(self.advance().value)
            elif self.match(TokenType.WITH, TokenType.OF, TokenType.THE, TokenType.A, TokenType.AN, TokenType.IN):
                name_parts.append(self.advance().value)
            else:
                self.advance()  # Skip other tokens as part of name

        # Parse return type
        if self.match(TokenType.AND_RETURN):
            self.advance()
            self.skip_optional(TokenType.A, TokenType.AN)
            return_type = self.parse_type()

        self.skip_optional(TokenType.COLON)
        self.skip_newlines()

        # Convert name parts to function name
        func_name = "_".join(name_parts) if name_parts else "unnamed"
        func_name = func_name.replace(" ", "_").lower()

        body = self.parse_block()

        return FunctionDef(name=func_name, params=params, return_type=return_type,
                          body=body, line=line)

    def parse_type(self) -> TypeSpec:
        type_spec = TypeSpec(line=self.current_line)

        # Handle pointer
        if self.match(TokenType.POINTER_TO):
            self.advance()
            type_spec.is_pointer = True
            self.skip_optional(TokenType.A, TokenType.AN)

        # Handle list/array
        if self.match(TokenType.LIST_OF):
            self.advance()
            type_spec.is_array = True

            # Check for array size
            if self.match(TokenType.NUMBER_LITERAL):
                type_spec.array_size = int(self.advance().value)

        # Parse base type
        if self.match(TokenType.NUMBER):
            self.advance()
            type_spec.base_type = "number"
        elif self.match(TokenType.DECIMAL):
            self.advance()
            type_spec.base_type = "decimal"
        elif self.match(TokenType.TEXT):
            self.advance()
            type_spec.base_type = "text"
        elif self.match(TokenType.LETTER):
            self.advance()
            type_spec.base_type = "letter"
        elif self.match(TokenType.YES_OR_NO, TokenType.BOOLEAN):
            self.advance()
            type_spec.base_type = "boolean"
        elif self.match(TokenType.NOTHING):
            self.advance()
            type_spec.base_type = "nothing"
        elif self.match(TokenType.IDENTIFIER):
            type_spec.base_type = "struct"
            type_spec.struct_name = self.advance().value
        else:
            type_spec.base_type = "number"  # default

        return type_spec

    def parse_block(self) -> List[Statement]:
        statements = []

        while not self.match(TokenType.END, TokenType.OTHERWISE, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.END, TokenType.OTHERWISE, TokenType.EOF):
                break

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

            self.skip_newlines()

        if self.match(TokenType.END):
            self.advance()

        return statements

    def parse_statement(self) -> Optional[Statement]:
        self.skip_newlines()

        if self.match(TokenType.THERE_IS):
            return self.parse_var_decl()
        elif self.match(TokenType.LET):
            return self.parse_let_statement()
        elif self.match(TokenType.CHANGE, TokenType.SET, TokenType.NOW, TokenType.MAKE):
            return self.parse_assignment()
        elif self.match(TokenType.ADD):
            return self.parse_add_statement()
        elif self.match(TokenType.SUBTRACT):
            return self.parse_subtract_statement()
        elif self.match(TokenType.MULTIPLY):
            return self.parse_multiply_statement()
        elif self.match(TokenType.DIVIDE):
            return self.parse_divide_statement()
        elif self.match(TokenType.INCREASE):
            return self.parse_increment()
        elif self.match(TokenType.DECREASE):
            return self.parse_decrement()
        elif self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.WHILE, TokenType.KEEP_DOING):
            return self.parse_while()
        elif self.match(TokenType.FOR_EACH):
            return self.parse_for()
        elif self.match(TokenType.REPEAT):
            return self.parse_repeat()
        elif self.match(TokenType.SAY, TokenType.PRINT, TokenType.SHOW, TokenType.DISPLAY):
            return self.parse_print()
        elif self.match(TokenType.ASK_USER_FOR, TokenType.READ, TokenType.GET_INPUT):
            return self.parse_input()
        elif self.match(TokenType.RETURN):
            return self.parse_return()
        elif self.match(TokenType.STOP_THE_LOOP, TokenType.LEAVE_THE_LOOP):
            self.advance()
            return BreakStatement(line=self.current_line)
        elif self.match(TokenType.SKIP_TO_NEXT, TokenType.CONTINUE_NEXT):
            self.advance()
            return ContinueStatement(line=self.current_line)
        elif self.match(TokenType.STOP_PROGRAM):
            self.advance()
            return ReturnStatement(value=NumberLiteral(value=1), line=self.current_line)
        elif self.match(TokenType.FREE):
            return self.parse_free()
        elif self.match(TokenType.CLOSE_FILE):
            return self.parse_close_file()
        # GUI statements
        elif self.match(TokenType.OPEN_WINDOW):
            return self.parse_open_window()
        elif self.match(TokenType.CLOSE_WINDOW):
            self.advance()
            return CloseWindow(line=self.current_line)
        elif self.match(TokenType.BEGIN_DRAWING):
            self.advance()
            return BeginDrawing(line=self.current_line)
        elif self.match(TokenType.END_DRAWING):
            self.advance()
            return EndDrawing(line=self.current_line)
        elif self.match(TokenType.CLEAR_SCREEN):
            return self.parse_clear_screen()
        elif self.match(TokenType.DRAW_RECTANGLE):
            return self.parse_draw_rectangle()
        elif self.match(TokenType.DRAW_TEXT):
            return self.parse_draw_text()
        elif self.match(TokenType.NOTE, TokenType.NOTES, TokenType.REMINDER):
            self.parse_comment()
            return None
        elif self.match(TokenType.IDENTIFIER):
            # Could be a function call or assignment via identifier
            return self.parse_identifier_statement()
        elif self.match(TokenType.NUMBER, TokenType.DECIMAL, TokenType.TEXT, TokenType.LETTER):
            # Type at start of statement - variable declaration
            return self.parse_typed_var_decl()
        else:
            # Try parsing as expression statement
            expr = self.parse_expression()
            if expr:
                return ExpressionStmt(expression=expr, line=self.current_line)
            return None

    def parse_var_decl(self) -> VarDecl:
        line = self.current().line
        self.advance()  # there is

        # Check for file declaration
        is_file = False
        file_path = None
        file_mode = ""

        # Handle "a file called X which opens Y for reading"
        if self.match(TokenType.A, TokenType.AN):
            self.advance()

        # Check for "file called"
        if self.current().value.lower() == "file":
            is_file = True
            self.advance()
            self.skip_optional(TokenType.CALLED)
            var_name = self.expect(TokenType.IDENTIFIER).value

            if self.match(TokenType.OPENS):
                self.advance()
                file_path = self.parse_expression()
                if self.match(TokenType.FOR_READING):
                    self.advance()
                    file_mode = "read"
                elif self.match(TokenType.FOR_WRITING):
                    self.advance()
                    file_mode = "write"

            return VarDecl(name=var_name, var_type=TypeSpec(base_type="file"),
                          is_file=True, file_path=file_path, file_mode=file_mode, line=line)

        var_type = self.parse_type()

        self.expect(TokenType.CALLED)
        var_name = self.expect(TokenType.IDENTIFIER).value

        initial_value = None

        # Check for "which is" or "which has"
        if self.match(TokenType.WHICH_IS):
            self.advance()
            initial_value = self.parse_expression()
        elif self.match(TokenType.HAS):
            self.advance()
            # Handle struct initialization with named fields
            initial_value = self.parse_struct_init()
        elif self.match(TokenType.CONTAINING):
            self.advance()
            # Array initialization
            elements = [self.parse_expression()]
            while self.match(TokenType.COMMA):
                self.advance()
                elements.append(self.parse_expression())
            initial_value = ArrayLiteral(elements=elements, line=line)

        return VarDecl(name=var_name, var_type=var_type, initial_value=initial_value, line=line)

    def parse_typed_var_decl(self) -> VarDecl:
        """Parse declarations like 'number x is 5'"""
        line = self.current().line
        var_type = self.parse_type()
        var_name = self.expect(TokenType.IDENTIFIER).value

        initial_value = None
        if self.match(TokenType.IS):
            self.advance()
            initial_value = self.parse_expression()

        return VarDecl(name=var_name, var_type=var_type, initial_value=initial_value, line=line)

    def parse_struct_init(self) -> Expression:
        """Parse struct initialization like 'name "Alice" and age 25'"""
        # For now, just parse as the first expression
        # A more complete implementation would handle named fields
        return self.parse_expression()

    def parse_let_statement(self) -> Statement:
        line = self.current().line
        self.advance()  # let

        var_name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.BE)
        value = self.parse_expression()

        # Check if this is a new variable or assignment
        # Treat "let x be y" as both declaration and assignment
        return VarDecl(name=var_name, initial_value=value, line=line)

    def parse_assignment(self) -> Assignment:
        line = self.current().line
        self.advance()  # change/set/now/make

        target = self.parse_assignment_target()

        self.skip_optional(TokenType.TO, TokenType.IS, TokenType.EQUAL_TO)

        value = self.parse_expression()

        return Assignment(target=target, value=value, line=line)

    def parse_assignment_target(self) -> Expression:
        """Parse the left-hand side of an assignment."""
        if self.match(TokenType.ITEM_NUMBER):
            self.advance()
            index = self.parse_expression()
            self.skip_optional(TokenType.IN)
            array = self.parse_primary()
            return ArrayAccess(array=array, index=index, line=self.current_line)
        elif self.match(TokenType.FIRST_ITEM_IN):
            self.advance()
            array = self.parse_primary()
            return ArrayAccess(array=array, index=NumberLiteral(value=0), line=self.current_line)
        elif self.match(TokenType.LAST_ITEM_IN):
            self.advance()
            array = self.parse_primary()
            # This needs runtime support - for now use -1 as sentinel
            return ArrayAccess(array=array, index=NumberLiteral(value=-1), line=self.current_line)
        elif self.match(TokenType.VALUE_AT):
            self.advance()
            ptr = self.parse_primary()
            return Dereference(operand=ptr, line=self.current_line)
        elif self.match(TokenType.THE):
            self.advance()
            return self.parse_assignment_target()
        else:
            target = self.parse_primary()
            # Check for 's (possessive)
            if self.match(TokenType.APOSTROPHE_S):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                return MemberAccess(object=target, member=member, line=self.current_line)
            return target

    def parse_add_statement(self) -> Statement:
        line = self.current().line
        self.advance()  # add

        value = self.parse_expression()

        self.expect(TokenType.TO)
        target = self.parse_primary()

        return Assignment(target=target,
                         value=BinaryOp(left=target, operator="+", right=value),
                         line=line)

    def parse_subtract_statement(self) -> Statement:
        line = self.current().line
        self.advance()  # subtract

        value = self.parse_expression()

        self.expect(TokenType.FROM)
        target = self.parse_primary()

        return Assignment(target=target,
                         value=BinaryOp(left=target, operator="-", right=value),
                         line=line)

    def parse_multiply_statement(self) -> Statement:
        line = self.current().line
        self.advance()  # multiply

        target = self.parse_primary()
        self.skip_optional(TokenType.TIMES)  # "by" is parsed as TIMES
        value = self.parse_expression()

        return Assignment(target=target,
                         value=BinaryOp(left=target, operator="*", right=value),
                         line=line)

    def parse_divide_statement(self) -> Statement:
        line = self.current().line
        self.advance()  # divide

        target = self.parse_primary()
        self.skip_optional(TokenType.TIMES)  # "by" is parsed as TIMES
        value = self.parse_expression()

        return Assignment(target=target,
                         value=BinaryOp(left=target, operator="/", right=value),
                         line=line)

    def parse_increment(self) -> Statement:
        line = self.current().line
        self.advance()  # increase
        target = self.parse_primary()
        return Assignment(target=target,
                         value=BinaryOp(left=target, operator="+", right=NumberLiteral(value=1)),
                         line=line)

    def parse_decrement(self) -> Statement:
        line = self.current().line
        self.advance()  # decrease
        target = self.parse_primary()
        return Assignment(target=target,
                         value=BinaryOp(left=target, operator="-", right=NumberLiteral(value=1)),
                         line=line)

    def parse_if(self) -> IfStatement:
        line = self.current().line
        self.advance()  # if

        condition = self.parse_condition()
        self.expect(TokenType.THEN)
        self.skip_newlines()

        then_body = []
        else_if_clauses = []
        else_body = []

        # Parse then body
        while not self.match(TokenType.END, TokenType.OTHERWISE, TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.END, TokenType.OTHERWISE, TokenType.EOF):
                break
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
            self.skip_newlines()

        # Parse else-if and else clauses
        while self.match(TokenType.OTHERWISE):
            self.advance()

            if self.match(TokenType.IF):
                # else-if
                self.advance()
                else_if_cond = self.parse_condition()
                self.expect(TokenType.THEN)
                self.skip_newlines()

                else_if_body = []
                while not self.match(TokenType.END, TokenType.OTHERWISE, TokenType.EOF):
                    self.skip_newlines()
                    if self.match(TokenType.END, TokenType.OTHERWISE, TokenType.EOF):
                        break
                    stmt = self.parse_statement()
                    if stmt:
                        else_if_body.append(stmt)
                    self.skip_newlines()

                else_if_clauses.append(ElseIfClause(condition=else_if_cond, body=else_if_body))
            else:
                # else
                self.skip_newlines()
                while not self.match(TokenType.END, TokenType.EOF):
                    self.skip_newlines()
                    if self.match(TokenType.END, TokenType.EOF):
                        break
                    stmt = self.parse_statement()
                    if stmt:
                        else_body.append(stmt)
                    self.skip_newlines()
                break

        if self.match(TokenType.END):
            self.advance()

        return IfStatement(condition=condition, then_body=then_body,
                          else_if_clauses=else_if_clauses, else_body=else_body, line=line)

    def parse_while(self) -> WhileStatement:
        line = self.current().line
        self.advance()  # while or keep_doing

        condition = self.parse_condition()
        self.skip_optional(TokenType.COLON)
        self.skip_newlines()

        body = self.parse_block()

        return WhileStatement(condition=condition, body=body, line=line)

    def parse_for(self) -> Union[ForStatement, ForEachStatement]:
        line = self.current().line
        self.advance()  # for each

        var_type = self.parse_type()
        var_name = self.expect(TokenType.IDENTIFIER).value

        if self.match(TokenType.FROM):
            # for each number i from 1 to 10
            self.advance()
            start = self.parse_expression()

            step = 1
            if self.match(TokenType.DOWN_TO):
                self.advance()
                step = -1
            else:
                self.expect(TokenType.TO)

            end = self.parse_expression()
            self.skip_optional(TokenType.COLON)
            self.skip_newlines()

            body = self.parse_block()

            return ForStatement(var_name=var_name, var_type=var_type,
                              start=start, end=end, step=step, body=body, line=line)
        elif self.match(TokenType.IN):
            # for each item in the list
            self.advance()
            self.skip_optional(TokenType.THE)
            iterable = self.parse_expression()
            self.skip_optional(TokenType.COLON)
            self.skip_newlines()

            body = self.parse_block()

            return ForEachStatement(var_name=var_name, var_type=var_type,
                                   iterable=iterable, body=body, line=line)
        else:
            self.error("Expected 'from' or 'in' in for loop")

    def parse_repeat(self) -> RepeatStatement:
        line = self.current().line
        self.advance()  # repeat

        # Use parse_primary to avoid "times" being parsed as multiplication
        count = self.parse_primary()
        self.skip_optional(TokenType.TIMES_LOOP)
        if self.match(TokenType.TIMES):
            self.advance()
        self.skip_optional(TokenType.COLON)
        self.skip_newlines()

        body = self.parse_block()

        return RepeatStatement(count=count, body=body, line=line)

    def parse_print(self) -> PrintStatement:
        line = self.current().line
        self.advance()  # say/print/show/display

        parts = []

        # Handle "the value of"
        if self.match(TokenType.THE_VALUE_OF):
            self.advance()

        parts.append(self.parse_expression())

        while self.match(TokenType.AND_THEN, TokenType.FOLLOWED_BY, TokenType.AND):
            self.advance()
            if self.match(TokenType.THEN):
                self.advance()
            parts.append(self.parse_expression())

        return PrintStatement(parts=parts, line=line)

    def parse_input(self) -> InputStatement:
        line = self.current().line

        input_type = "text"

        if self.match(TokenType.ASK_USER_FOR):
            # Already includes type info in some patterns
            token_value = self.advance().value.lower()
            if "number" in token_value:
                input_type = "number"
            elif "decimal" in token_value:
                input_type = "decimal"
            elif "letter" in token_value:
                input_type = "letter"
            else:
                input_type = "text"

            target = self.parse_primary()
        elif self.match(TokenType.READ):
            self.advance()
            if self.match(TokenType.A, TokenType.AN):
                self.advance()
            if self.match(TokenType.NUMBER):
                self.advance()
                input_type = "number"
            elif self.match(TokenType.DECIMAL):
                self.advance()
                input_type = "decimal"
            elif self.match(TokenType.TEXT):
                self.advance()
                input_type = "text"

            self.skip_optional(TokenType.INTO)
            target = self.parse_primary()
        else:  # GET_INPUT
            self.advance()
            target = self.parse_primary()

        return InputStatement(target=target, input_type=input_type, line=line)

    def parse_return(self) -> ReturnStatement:
        line = self.current().line
        self.advance()  # return

        value = None
        if not self.match(TokenType.NEWLINE, TokenType.END, TokenType.EOF):
            value = self.parse_expression()

        return ReturnStatement(value=value, line=line)

    def parse_free(self) -> Free:
        line = self.current().line
        self.advance()  # free
        pointer = self.parse_expression()
        return Free(pointer=pointer, line=line)

    def parse_close_file(self) -> ExpressionStmt:
        line = self.current().line
        self.advance()  # close the file
        file_var = self.parse_primary()
        return ExpressionStmt(
            expression=FunctionCall(name="fclose", arguments=[file_var]),
            line=line
        )

    def parse_comment(self):
        """Skip comment lines."""
        if self.match(TokenType.NOTE, TokenType.REMINDER):
            self.advance()
            self.skip_optional(TokenType.COLON)
            # Skip to end of line
            while not self.match(TokenType.NEWLINE, TokenType.EOF):
                self.advance()
        elif self.match(TokenType.NOTES):
            self.advance()
            self.skip_optional(TokenType.COLON)
            # Skip until "end notes"
            while not self.match(TokenType.END_NOTES, TokenType.EOF):
                self.advance()
            if self.match(TokenType.END_NOTES):
                self.advance()

    # GUI parsing methods
    def parse_open_window(self) -> OpenWindow:
        line = self.current().line
        self.advance()  # open a window sized
        width = self.parse_primary()
        # Skip "by" or "x"
        if self.current().value.lower() in ("by", "x"):
            self.advance()
        height = self.parse_primary()
        title = None
        if self.match(TokenType.CALLED, TokenType.WITH):
            self.advance()
            if self.match(TokenType.IDENTIFIER) and self.current().value.lower() == "title":
                self.advance()
            title = self.parse_expression()
        elif self.match(TokenType.STRING_LITERAL):
            title = self.parse_expression()
        return OpenWindow(width=width, height=height, title=title, line=line)

    def parse_clear_screen(self) -> ClearScreen:
        line = self.current().line
        self.advance()  # clear the screen with
        color = "RAYWHITE"
        if self.match(TokenType.IDENTIFIER):
            color = self.advance().value.upper()
        return ClearScreen(color=color, line=line)

    def parse_draw_rectangle(self) -> DrawRectangle:
        line = self.current().line
        self.advance()  # draw a rectangle at
        x = self.parse_primary()
        self.skip_optional(TokenType.COMMA)
        y = self.parse_primary()
        # Parse "sized" or "with size"
        if self.current().value.lower() in ("sized", "size", "with"):
            self.advance()
            if self.current().value.lower() == "size":
                self.advance()
        width = self.parse_primary()
        # Skip "by" or "x"
        if self.current().value.lower() in ("by", "x"):
            self.advance()
        height = self.parse_primary()
        color = "LIGHTGRAY"
        if self.current().value.lower() in ("in", "with", "colored"):
            self.advance()
            if self.current().value.lower() == "color":
                self.advance()
            if self.match(TokenType.IDENTIFIER):
                color = self.advance().value.upper()
        return DrawRectangle(x=x, y=y, width=width, height=height, color=color, line=line)

    def parse_draw_text(self) -> DrawText:
        line = self.current().line
        self.advance()  # draw text
        text = self.parse_expression()
        x = NumberLiteral(value=0)
        y = NumberLiteral(value=0)
        size = NumberLiteral(value=20)
        color = "BLACK"
        # Parse "at X, Y"
        if self.current().value.lower() == "at":
            self.advance()
            x = self.parse_expression()
            self.skip_optional(TokenType.COMMA)
            y = self.parse_expression()
        # Parse "size N" or "sized N"
        if self.current().value.lower() in ("size", "sized", "with"):
            self.advance()
            if self.current().value.lower() == "size":
                self.advance()
            size = self.parse_expression()
        # Parse "in COLOR" or "colored COLOR"
        if self.current().value.lower() in ("in", "colored", "with"):
            self.advance()
            if self.current().value.lower() == "color":
                self.advance()
            if self.match(TokenType.IDENTIFIER):
                color = self.advance().value.upper()
        return DrawText(text=text, x=x, y=y, size=size, color=color, line=line)

    def parse_identifier_statement(self) -> Statement:
        """Parse a statement that starts with an identifier - could be function call or assignment."""
        line = self.current().line

        # Look ahead to determine what kind of statement this is
        # Could be: function call, assignment with 's, etc.

        # Try parsing as an expression first
        expr = self.parse_expression()

        # Check if this is actually an assignment
        if self.match(TokenType.TO, TokenType.IS, TokenType.EQUAL_TO):
            self.advance()
            value = self.parse_expression()
            return Assignment(target=expr, value=value, line=line)

        return ExpressionStmt(expression=expr, line=line)

    def parse_condition(self) -> Expression:
        """Parse a condition expression with comparison operators."""
        return self.parse_or_expression()

    def parse_or_expression(self) -> Expression:
        left = self.parse_and_expression()

        while self.match(TokenType.OR):
            self.advance()
            right = self.parse_and_expression()
            left = BinaryOp(left=left, operator="||", right=right, line=self.current_line)

        return left

    def parse_and_expression(self) -> Expression:
        left = self.parse_not_expression()

        while self.match(TokenType.AND):
            self.advance()
            right = self.parse_not_expression()
            left = BinaryOp(left=left, operator="&&", right=right, line=self.current_line)

        return left

    def parse_not_expression(self) -> Expression:
        if self.match(TokenType.NOT, TokenType.IT_IS_NOT_THE_CASE_THAT):
            self.advance()
            operand = self.parse_not_expression()
            return UnaryOp(operator="!", operand=operand, line=self.current_line)

        return self.parse_comparison()

    def parse_comparison(self) -> Expression:
        left = self.parse_expression()

        if self.match(TokenType.GREATER_THAN):
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left=left, operator=">", right=right, line=self.current_line)
        elif self.match(TokenType.LESS_THAN):
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left=left, operator="<", right=right, line=self.current_line)
        elif self.match(TokenType.EQUALS, TokenType.SAME_AS):
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left=left, operator="==", right=right, line=self.current_line)
        elif self.match(TokenType.NOT_EQUAL_TO):
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left=left, operator="!=", right=right, line=self.current_line)
        elif self.match(TokenType.AT_LEAST):
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left=left, operator=">=", right=right, line=self.current_line)
        elif self.match(TokenType.AT_MOST):
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left=left, operator="<=", right=right, line=self.current_line)
        elif self.match(TokenType.BETWEEN):
            self.advance()
            low = self.parse_expression()
            self.expect(TokenType.AND)
            high = self.parse_expression()
            # x is between a and b -> x >= a && x <= b
            return BinaryOp(
                left=BinaryOp(left=left, operator=">=", right=low),
                operator="&&",
                right=BinaryOp(left=left, operator="<=", right=high),
                line=self.current_line
            )
        elif self.match(TokenType.POSITIVE):
            self.advance()
            return BinaryOp(left=left, operator=">", right=NumberLiteral(value=0), line=self.current_line)
        elif self.match(TokenType.IS_NEGATIVE):
            self.advance()
            return BinaryOp(left=left, operator="<", right=NumberLiteral(value=0), line=self.current_line)
        elif self.match(TokenType.IS_ZERO):
            self.advance()
            return BinaryOp(left=left, operator="==", right=NumberLiteral(value=0), line=self.current_line)
        elif self.match(TokenType.IS_EVEN):
            self.advance()
            return BinaryOp(
                left=BinaryOp(left=left, operator="%", right=NumberLiteral(value=2)),
                operator="==",
                right=NumberLiteral(value=0),
                line=self.current_line
            )
        elif self.match(TokenType.IS_ODD):
            self.advance()
            return BinaryOp(
                left=BinaryOp(left=left, operator="%", right=NumberLiteral(value=2)),
                operator="!=",
                right=NumberLiteral(value=0),
                line=self.current_line
            )
        elif self.match(TokenType.IS_EMPTY):
            self.advance()
            # array is empty -> length == 0
            return BinaryOp(
                left=FunctionCall(name="__len__", arguments=[left]),
                operator="==",
                right=NumberLiteral(value=0),
                line=self.current_line
            )
        elif self.match(TokenType.CONTAINS):
            self.advance()
            right = self.parse_expression()
            return FunctionCall(name="strstr", arguments=[left, right], line=self.current_line)

        return left

    def parse_expression(self) -> Expression:
        return self.parse_additive()

    def parse_additive(self) -> Expression:
        left = self.parse_multiplicative()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = "+" if self.current().type == TokenType.PLUS else "-"
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left=left, operator=op, right=right, line=self.current_line)

        return left

    def parse_multiplicative(self) -> Expression:
        left = self.parse_power()

        while self.match(TokenType.TIMES, TokenType.DIVIDED_BY, TokenType.MODULO):
            if self.current().type == TokenType.TIMES:
                op = "*"
            elif self.current().type == TokenType.DIVIDED_BY:
                op = "/"
            else:
                op = "%"
            self.advance()
            right = self.parse_power()
            left = BinaryOp(left=left, operator=op, right=right, line=self.current_line)

        return left

    def parse_power(self) -> Expression:
        left = self.parse_unary()

        if self.match(TokenType.TO_THE_POWER_OF):
            self.advance()
            right = self.parse_unary()
            return FunctionCall(name="pow", arguments=[left, right], line=self.current_line)

        return left

    def parse_unary(self) -> Expression:
        if self.match(TokenType.NEGATIVE):
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(operator="-", operand=operand, line=self.current_line)
        elif self.match(TokenType.SQUARE_ROOT_OF):
            self.advance()
            operand = self.parse_unary()
            return FunctionCall(name="sqrt", arguments=[operand], line=self.current_line)
        elif self.match(TokenType.ABSOLUTE_VALUE_OF):
            self.advance()
            operand = self.parse_unary()
            return FunctionCall(name="abs", arguments=[operand], line=self.current_line)
        elif self.match(TokenType.THE_SUM_OF):
            self.advance()
            left = self.parse_primary()
            self.expect(TokenType.AND)
            right = self.parse_primary()
            return BinaryOp(left=left, operator="+", right=right, line=self.current_line)
        elif self.match(TokenType.ADDRESS_OF):
            self.advance()
            operand = self.parse_primary()
            return AddressOf(operand=operand, line=self.current_line)
        elif self.match(TokenType.VALUE_AT):
            self.advance()
            operand = self.parse_primary()
            if self.match(TokenType.POINTS_TO):
                self.advance()
            return Dereference(operand=operand, line=self.current_line)
        elif self.match(TokenType.RESULT_OF):
            self.advance()
            return self.parse_function_call()

        return self.parse_postfix()

    def parse_postfix(self) -> Expression:
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.APOSTROPHE_S):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberAccess(object=expr, member=member, line=self.current_line)
            else:
                break

        return expr

    def parse_primary(self) -> Expression:
        if self.match(TokenType.NUMBER_LITERAL):
            return NumberLiteral(value=int(self.advance().value), line=self.current_line)
        elif self.match(TokenType.DECIMAL_LITERAL):
            return DecimalLiteral(value=float(self.advance().value), line=self.current_line)
        elif self.match(TokenType.STRING_LITERAL):
            return StringLiteral(value=self.advance().value, line=self.current_line)
        elif self.match(TokenType.CHAR_LITERAL):
            return CharLiteral(value=self.advance().value, line=self.current_line)
        elif self.match(TokenType.YES):
            self.advance()
            return BoolLiteral(value=True, line=self.current_line)
        elif self.match(TokenType.NO):
            self.advance()
            return BoolLiteral(value=False, line=self.current_line)
        elif self.match(TokenType.NULL):
            self.advance()
            return NullLiteral(line=self.current_line)
        elif self.match(TokenType.FIRST_ITEM_IN):
            self.advance()
            array = self.parse_primary()
            return ArrayAccess(array=array, index=NumberLiteral(value=0), line=self.current_line)
        elif self.match(TokenType.LAST_ITEM_IN):
            self.advance()
            array = self.parse_primary()
            return ArrayAccess(array=array, index=NumberLiteral(value=-1), line=self.current_line)
        elif self.match(TokenType.ITEM_NUMBER):
            self.advance()
            index = self.parse_expression()
            self.skip_optional(TokenType.IN, TokenType.OF)
            array = self.parse_primary()
            return ArrayAccess(array=array, index=index, line=self.current_line)
        elif self.match(TokenType.LENGTH_OF, TokenType.SIZE_OF, TokenType.HOW_MANY_IN):
            self.advance()
            self.skip_optional(TokenType.THE)
            array = self.parse_primary()
            return FunctionCall(name="__len__", arguments=[array], line=self.current_line)
        elif self.match(TokenType.ALLOCATE):
            self.advance()
            count = self.parse_expression()
            alloc_type = self.parse_type()
            self.skip_optional(TokenType.AND)
            self.skip_optional(TokenType.CALLED)
            return Allocate(count=count, alloc_type=alloc_type, line=self.current_line)
        elif self.match(TokenType.RANDOM_NUMBER):
            self.advance()
            min_val = self.parse_expression()
            self.expect(TokenType.AND)
            max_val = self.parse_expression()
            return RandomNumber(min_val=min_val, max_val=max_val, line=self.current_line)
        elif self.match(TokenType.ANOTHER_LINE_IN):
            self.advance()
            file_var = self.parse_primary()
            return FunctionCall(name="__has_line__", arguments=[file_var], line=self.current_line)
        elif self.match(TokenType.READ_LINE_FROM):
            self.advance()
            file_var = self.parse_primary()
            self.skip_optional(TokenType.INTO)
            target = self.parse_primary()
            return FunctionCall(name="__read_line__", arguments=[file_var, target], line=self.current_line)
        elif self.match(TokenType.FAILED_TO_OPEN):
            self.advance()
            return BinaryOp(
                left=Identifier(name="__last_file__"),
                operator="==",
                right=NullLiteral(),
                line=self.current_line
            )
        # GUI expressions
        elif self.match(TokenType.WINDOW_SHOULD_CLOSE):
            self.advance()
            return WindowShouldClose(line=self.current_line)
        elif self.match(TokenType.MOUSE_X):
            self.advance()
            return MouseX(line=self.current_line)
        elif self.match(TokenType.MOUSE_Y):
            self.advance()
            return MouseY(line=self.current_line)
        elif self.match(TokenType.MOUSE_PRESSED):
            self.advance()
            return MousePressed(line=self.current_line)
        elif self.match(TokenType.THE):
            self.advance()
            return self.parse_primary()
        elif self.match(TokenType.A, TokenType.AN):
            self.advance()
            return self.parse_primary()
        elif self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            return Identifier(name=name, line=self.current_line)
        else:
            # Skip unknown tokens and return None equivalent
            self.advance()
            return NumberLiteral(value=0, line=self.current_line)

    def parse_function_call(self) -> Expression:
        """Parse a function call."""
        # Collect function name words and arguments
        name_parts = []
        arguments = []

        while not self.match(TokenType.NEWLINE, TokenType.EOF, TokenType.END,
                            TokenType.THEN, TokenType.AND, TokenType.PLUS, TokenType.MINUS,
                            TokenType.TIMES, TokenType.DIVIDED_BY):
            if self.match(TokenType.NUMBER_LITERAL, TokenType.DECIMAL_LITERAL,
                         TokenType.STRING_LITERAL):
                arguments.append(self.parse_primary())
            elif self.match(TokenType.IDENTIFIER):
                # Could be argument or part of function name
                # If next token suggests it's an argument context, treat as argument
                next_tok = self.peek(1)
                if next_tok.type in (TokenType.AND, TokenType.COMMA, TokenType.NEWLINE,
                                    TokenType.PLUS, TokenType.MINUS):
                    arguments.append(self.parse_primary())
                else:
                    name_parts.append(self.advance().value)
            elif self.match(TokenType.THE):
                self.advance()
            elif self.match(TokenType.OF, TokenType.WITH, TokenType.IN):
                name_parts.append(self.advance().value)
            else:
                break

        func_name = "_".join(name_parts) if name_parts else "unknown"
        return FunctionCall(name=func_name.lower(), arguments=arguments, line=self.current_line)


def parse(source: str) -> Program:
    """Convenience function to parse source code."""
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()


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

    program = parse(test_code)
    print("Parsed program:")
    print(f"  Includes: {[i.library for i in program.includes]}")
    print(f"  Functions: {[f.name for f in program.functions]}")
    for func in program.functions:
        print(f"    {func.name}: {len(func.body)} statements")
