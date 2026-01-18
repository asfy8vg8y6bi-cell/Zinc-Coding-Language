"""
Zinc Lexer - Tokenizes natural English syntax into tokens for parsing.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Tuple

class TokenType(Enum):
    # Keywords - declarations
    THERE_IS = auto()
    LET = auto()
    BE = auto()
    WHICH_IS = auto()
    CALLED = auto()
    IS = auto()

    # Types
    NUMBER = auto()
    DECIMAL = auto()
    LETTER = auto()
    TEXT = auto()
    YES_OR_NO = auto()
    BOOLEAN = auto()
    NOTHING = auto()
    POINTER_TO = auto()
    LIST_OF = auto()

    # Values
    YES = auto()
    NO = auto()
    NULL = auto()

    # Assignment
    CHANGE = auto()
    SET = auto()
    NOW = auto()
    MAKE = auto()
    TO = auto()
    EQUAL_TO = auto()

    # Arithmetic operations
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    INCREASE = auto()
    DECREASE = auto()
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDED_BY = auto()
    MODULO = auto()
    TO_THE_POWER_OF = auto()

    # Math functions
    SQUARE_ROOT_OF = auto()
    ABSOLUTE_VALUE_OF = auto()
    THE_SUM_OF = auto()
    NEGATIVE = auto()

    # Comparisons
    GREATER_THAN = auto()
    LESS_THAN = auto()
    EQUALS = auto()
    SAME_AS = auto()
    NOT_EQUAL_TO = auto()
    AT_LEAST = auto()
    AT_MOST = auto()
    BETWEEN = auto()
    POSITIVE = auto()
    IS_NEGATIVE = auto()
    IS_ZERO = auto()
    IS_EVEN = auto()
    IS_ODD = auto()
    CONTAINS = auto()
    IS_EMPTY = auto()

    # Logic
    AND = auto()
    OR = auto()
    NOT = auto()
    IT_IS_NOT_THE_CASE_THAT = auto()

    # Control flow
    IF = auto()
    THEN = auto()
    OTHERWISE = auto()
    END = auto()

    # Loops
    REPEAT = auto()
    TIMES_LOOP = auto()
    WHILE = auto()
    FOR_EACH = auto()
    FROM = auto()
    DOWN_TO = auto()
    IN = auto()
    STOP_THE_LOOP = auto()
    SKIP_TO_NEXT = auto()
    LEAVE_THE_LOOP = auto()
    CONTINUE_NEXT = auto()
    KEEP_DOING = auto()

    # Functions
    TO_FUNC = auto()
    RETURN = auto()
    RESULT_OF = auto()
    AND_RETURN = auto()

    # Output
    SAY = auto()
    PRINT = auto()
    SHOW = auto()
    DISPLAY = auto()
    AND_THEN = auto()
    FOLLOWED_BY = auto()
    THE_VALUE_OF = auto()

    # Input
    ASK_USER_FOR = auto()
    STORE_IN = auto()
    READ = auto()
    INTO = auto()
    GET_INPUT = auto()

    # Arrays
    CONTAINING = auto()
    FIRST_ITEM_IN = auto()
    LAST_ITEM_IN = auto()
    ITEM_NUMBER = auto()
    LENGTH_OF = auto()
    SIZE_OF = auto()
    HOW_MANY_IN = auto()
    ADD_TO_LIST = auto()
    REMOVE_FROM = auto()
    ELEMENT_OF = auto()

    # Structures
    DEFINE = auto()
    AS_HAVING = auto()
    HAS = auto()
    APOSTROPHE_S = auto()

    # Pointers/Memory
    ADDRESS_OF = auto()
    VALUE_AT = auto()
    POINTS_TO = auto()
    ALLOCATE = auto()
    FREE = auto()
    SPACE_FOR = auto()

    # Includes
    INCLUDE = auto()
    USE = auto()
    STANDARD_IO = auto()
    STANDARD_MATH = auto()
    STRING_FUNCTIONS = auto()
    FILE_FUNCTIONS = auto()
    RANDOM_FUNCTIONS = auto()
    RAYLIB_GRAPHICS = auto()

    # GUI operations
    OPEN_WINDOW = auto()
    CLOSE_WINDOW = auto()
    WINDOW_SHOULD_CLOSE = auto()
    BEGIN_DRAWING = auto()
    END_DRAWING = auto()
    CLEAR_SCREEN = auto()
    DRAW_RECTANGLE = auto()
    DRAW_TEXT = auto()
    MOUSE_X = auto()
    MOUSE_Y = auto()
    MOUSE_PRESSED = auto()
    COLOR = auto()

    FILE_CALLED = auto()

    # File operations
    OPENS = auto()
    FOR_READING = auto()
    FOR_WRITING = auto()
    FAILED_TO_OPEN = auto()
    CLOSE_FILE = auto()
    ANOTHER_LINE_IN = auto()
    READ_LINE_FROM = auto()

    # Program control
    STOP_PROGRAM = auto()
    DO_MAIN = auto()

    # Comments
    NOTE = auto()
    NOTES = auto()
    END_NOTES = auto()
    REMINDER = auto()

    # Random
    RANDOM_NUMBER = auto()

    # Literals and identifiers
    STRING_LITERAL = auto()
    NUMBER_LITERAL = auto()
    DECIMAL_LITERAL = auto()
    CHAR_LITERAL = auto()
    IDENTIFIER = auto()

    # Punctuation that we keep
    COLON = auto()
    COMMA = auto()
    NEWLINE = auto()

    # Special
    A = auto()
    AN = auto()
    THE = auto()
    OF = auto()
    WITH = auto()

    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


# Multi-word phrases mapped to token types (order matters - longer phrases first)
PHRASES = [
    # Long phrases first
    ("it is not the case that", TokenType.IT_IS_NOT_THE_CASE_THAT),
    ("ask the user for a number and store it in", TokenType.ASK_USER_FOR),
    ("ask the user for a decimal and store it in", TokenType.ASK_USER_FOR),
    ("ask the user for a letter and store it in", TokenType.ASK_USER_FOR),
    ("ask the user for text and store it in", TokenType.ASK_USER_FOR),
    ("the standard input and output", TokenType.STANDARD_IO),
    ("the standard math functions", TokenType.STANDARD_MATH),
    ("the string functions", TokenType.STRING_FUNCTIONS),
    ("the file functions", TokenType.FILE_FUNCTIONS),
    ("the random functions", TokenType.RANDOM_FUNCTIONS),
    ("the graphics library", TokenType.RAYLIB_GRAPHICS),
    ("raylib graphics", TokenType.RAYLIB_GRAPHICS),
    ("open a window sized", TokenType.OPEN_WINDOW),
    ("open window sized", TokenType.OPEN_WINDOW),
    ("close the window", TokenType.CLOSE_WINDOW),
    ("the window should close", TokenType.WINDOW_SHOULD_CLOSE),
    ("window should close", TokenType.WINDOW_SHOULD_CLOSE),
    ("begin drawing", TokenType.BEGIN_DRAWING),
    ("start drawing", TokenType.BEGIN_DRAWING),
    ("end drawing", TokenType.END_DRAWING),
    ("stop drawing", TokenType.END_DRAWING),
    ("clear the screen with", TokenType.CLEAR_SCREEN),
    ("clear screen with", TokenType.CLEAR_SCREEN),
    ("draw a rectangle at", TokenType.DRAW_RECTANGLE),
    ("draw rectangle at", TokenType.DRAW_RECTANGLE),
    ("draw text", TokenType.DRAW_TEXT),
    ("the mouse x position", TokenType.MOUSE_X),
    ("mouse x", TokenType.MOUSE_X),
    ("the mouse y position", TokenType.MOUSE_Y),
    ("mouse y", TokenType.MOUSE_Y),
    ("the mouse was clicked", TokenType.MOUSE_PRESSED),
    ("mouse is pressed", TokenType.MOUSE_PRESSED),
    ("mouse was pressed", TokenType.MOUSE_PRESSED),
    ("a random number between", TokenType.RANDOM_NUMBER),
    ("continue with the next iteration", TokenType.CONTINUE_NEXT),
    ("skip to the next one", TokenType.SKIP_TO_NEXT),
    ("leave the loop", TokenType.LEAVE_THE_LOOP),
    ("stop the loop", TokenType.STOP_THE_LOOP),
    ("stop the program", TokenType.STOP_PROGRAM),
    ("do the main thing", TokenType.DO_MAIN),
    ("the absolute value of", TokenType.ABSOLUTE_VALUE_OF),
    ("the square root of", TokenType.SQUARE_ROOT_OF),
    ("to the power of", TokenType.TO_THE_POWER_OF),
    ("the sum of", TokenType.THE_SUM_OF),
    ("there is another line in", TokenType.ANOTHER_LINE_IN),
    ("read a line from", TokenType.READ_LINE_FROM),
    ("failed to open", TokenType.FAILED_TO_OPEN),
    ("close the file", TokenType.CLOSE_FILE),
    ("for reading", TokenType.FOR_READING),
    ("for writing", TokenType.FOR_WRITING),
    ("the file called", TokenType.FILE_CALLED),
    ("the result of", TokenType.RESULT_OF),
    ("the value that", TokenType.VALUE_AT),
    ("the value of", TokenType.THE_VALUE_OF),
    ("the value at", TokenType.VALUE_AT),
    ("the address of", TokenType.ADDRESS_OF),
    ("points to", TokenType.POINTS_TO),
    ("allocate space for", TokenType.ALLOCATE),
    ("free the memory at", TokenType.FREE),
    ("space for", TokenType.SPACE_FOR),
    ("and call it", TokenType.CALLED),
    ("pointer to", TokenType.POINTER_TO),
    ("list of", TokenType.LIST_OF),
    ("is greater than", TokenType.GREATER_THAN),
    ("is less than", TokenType.LESS_THAN),
    ("is the same as", TokenType.SAME_AS),
    ("is not equal to", TokenType.NOT_EQUAL_TO),
    ("not equal to", TokenType.NOT_EQUAL_TO),
    ("is at least", TokenType.AT_LEAST),
    ("is at most", TokenType.AT_MOST),
    ("is between", TokenType.BETWEEN),
    ("is positive", TokenType.POSITIVE),
    ("is negative", TokenType.IS_NEGATIVE),
    ("is zero", TokenType.IS_ZERO),
    ("is even", TokenType.IS_EVEN),
    ("is odd", TokenType.IS_ODD),
    ("is empty", TokenType.IS_EMPTY),
    ("is not", TokenType.NOT_EQUAL_TO),
    ("is yes", TokenType.YES),
    ("is no", TokenType.NO),
    ("equals yes", TokenType.YES),
    ("equals no", TokenType.NO),
    ("yes or no", TokenType.YES_OR_NO),
    ("divided by", TokenType.DIVIDED_BY),
    ("and then", TokenType.AND_THEN),
    ("followed by", TokenType.FOLLOWED_BY),
    ("down to", TokenType.DOWN_TO),
    ("for each", TokenType.FOR_EACH),
    ("there is a file called", TokenType.THERE_IS),
    ("there is a", TokenType.THERE_IS),
    ("there is an", TokenType.THERE_IS),
    ("there is", TokenType.THERE_IS),
    ("which is", TokenType.WHICH_IS),
    ("which has", TokenType.HAS),
    ("which opens", TokenType.OPENS),
    ("equal to", TokenType.EQUAL_TO),
    ("make equal to", TokenType.EQUAL_TO),
    ("the first item in", TokenType.FIRST_ITEM_IN),
    ("first item in", TokenType.FIRST_ITEM_IN),
    ("the last item in", TokenType.LAST_ITEM_IN),
    ("last item in", TokenType.LAST_ITEM_IN),
    ("item number", TokenType.ITEM_NUMBER),
    ("the length of", TokenType.LENGTH_OF),
    ("length of", TokenType.LENGTH_OF),
    ("the size of", TokenType.SIZE_OF),
    ("how many items are in", TokenType.HOW_MANY_IN),
    ("add to", TokenType.ADD_TO_LIST),
    ("remove the last item from", TokenType.REMOVE_FROM),
    ("element of", TokenType.ELEMENT_OF),
    ("as having", TokenType.AS_HAVING),
    ("and return", TokenType.AND_RETURN),
    ("the character at position", TokenType.ITEM_NUMBER),
    ("keep doing this while", TokenType.KEEP_DOING),
    ("get input from the user as", TokenType.GET_INPUT),
    ("read a number into", TokenType.READ),
    ("read text into", TokenType.READ),
    ("print the value of", TokenType.PRINT),
    ("end notes", TokenType.END_NOTES),
]

# Single-word keywords
KEYWORDS = {
    "include": TokenType.INCLUDE,
    "use": TokenType.USE,
    "let": TokenType.LET,
    "be": TokenType.BE,
    "called": TokenType.CALLED,
    "is": TokenType.IS,
    "number": TokenType.NUMBER,
    "numbers": TokenType.NUMBER,
    "decimal": TokenType.DECIMAL,
    "decimals": TokenType.DECIMAL,
    "letter": TokenType.LETTER,
    "letters": TokenType.LETTER,
    "text": TokenType.TEXT,
    "boolean": TokenType.BOOLEAN,
    "nothing": TokenType.NOTHING,
    "yes": TokenType.YES,
    "no": TokenType.NO,
    "null": TokenType.NULL,
    "change": TokenType.CHANGE,
    "set": TokenType.SET,
    "now": TokenType.NOW,
    "make": TokenType.MAKE,
    "to": TokenType.TO,
    "add": TokenType.ADD,
    "subtract": TokenType.SUBTRACT,
    "multiply": TokenType.MULTIPLY,
    "divide": TokenType.DIVIDE,
    "increase": TokenType.INCREASE,
    "decrease": TokenType.DECREASE,
    "plus": TokenType.PLUS,
    "minus": TokenType.MINUS,
    "times": TokenType.TIMES,
    "modulo": TokenType.MODULO,
    "negative": TokenType.NEGATIVE,
    "equals": TokenType.EQUALS,
    "contains": TokenType.CONTAINS,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "otherwise": TokenType.OTHERWISE,
    "end": TokenType.END,
    "repeat": TokenType.REPEAT,
    "while": TokenType.WHILE,
    "from": TokenType.FROM,
    "in": TokenType.IN,
    "return": TokenType.RETURN,
    "say": TokenType.SAY,
    "print": TokenType.PRINT,
    "show": TokenType.SHOW,
    "display": TokenType.DISPLAY,
    "containing": TokenType.CONTAINING,
    "define": TokenType.DEFINE,
    "has": TokenType.HAS,
    "a": TokenType.A,
    "an": TokenType.AN,
    "the": TokenType.THE,
    "of": TokenType.OF,
    "with": TokenType.WITH,
    "note": TokenType.NOTE,
    "notes": TokenType.NOTES,
    "reminder": TokenType.REMINDER,
    "into": TokenType.INTO,
    "opens": TokenType.OPENS,
    "store": TokenType.STORE_IN,
    "by": TokenType.TIMES,  # "multiply x by 2"
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def error(self, msg: str):
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {msg}")

    def peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return '\0'

    def advance(self) -> str:
        ch = self.peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def skip_whitespace(self):
        while self.peek() in ' \t\r':
            self.advance()

    def read_string(self) -> str:
        quote = self.advance()  # consume opening quote
        result = ""
        while self.peek() != quote and self.peek() != '\0':
            if self.peek() == '\\':
                self.advance()
                ch = self.advance()
                if ch == 'n':
                    result += '\n'
                elif ch == 't':
                    result += '\t'
                elif ch == '\\':
                    result += '\\'
                elif ch == '"':
                    result += '"'
                elif ch == "'":
                    result += "'"
                else:
                    result += ch
            else:
                result += self.advance()
        if self.peek() == '\0':
            self.error("Unterminated string literal")
        self.advance()  # consume closing quote
        return result

    def read_number(self) -> Tuple[str, bool]:
        result = ""
        is_decimal = False

        # Handle negative
        if self.peek() == '-':
            result += self.advance()

        while self.peek().isdigit():
            result += self.advance()

        if self.peek() == '.' and self.peek(1).isdigit():
            is_decimal = True
            result += self.advance()  # consume '.'
            while self.peek().isdigit():
                result += self.advance()

        return result, is_decimal

    def read_word(self) -> str:
        result = ""
        while self.peek().isalnum() or self.peek() == '_':
            result += self.advance()
        return result

    def try_match_phrase(self) -> Optional[Tuple[str, TokenType]]:
        """Try to match a multi-word phrase at the current position."""
        remaining = self.source[self.pos:].lower()

        for phrase, token_type in PHRASES:
            if remaining.startswith(phrase):
                # Make sure it's a word boundary
                next_pos = len(phrase)
                if next_pos < len(remaining):
                    next_char = remaining[next_pos]
                    if next_char.isalnum() or next_char == '_':
                        continue
                return phrase, token_type
        return None

    def add_token(self, token_type: TokenType, value: str):
        self.tokens.append(Token(token_type, value, self.line, self.column))

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()

            if self.pos >= len(self.source):
                break

            ch = self.peek()
            start_line = self.line
            start_col = self.column

            # Newlines
            if ch == '\n':
                self.advance()
                self.add_token(TokenType.NEWLINE, '\n')
                continue

            # Comments - skip lines starting with note:, notes:, reminder:
            if ch == '#':
                while self.peek() != '\n' and self.peek() != '\0':
                    self.advance()
                continue

            # String literals
            if ch == '"':
                value = self.read_string()
                self.add_token(TokenType.STRING_LITERAL, value)
                continue

            # Possessive 's - must check BEFORE character literals
            if ch == "'" and self.peek(1) == 's' and (self.peek(2) == ' ' or self.peek(2) == '\n' or self.peek(2) == '\0' or not self.peek(2).isalnum()):
                self.advance()
                self.advance()
                self.add_token(TokenType.APOSTROPHE_S, "'s")
                continue

            # Character literals
            if ch == "'":
                self.advance()  # opening quote
                if self.peek() == '\\':
                    self.advance()
                    char = self.advance()
                    if char == 'n':
                        value = '\n'
                    elif char == 't':
                        value = '\t'
                    else:
                        value = char
                else:
                    value = self.advance()
                if self.peek() != "'":
                    self.error("Unterminated character literal")
                self.advance()  # closing quote
                self.add_token(TokenType.CHAR_LITERAL, value)
                continue

            # Numbers
            if ch.isdigit() or (ch == '-' and self.peek(1).isdigit()):
                value, is_decimal = self.read_number()
                if is_decimal:
                    self.add_token(TokenType.DECIMAL_LITERAL, value)
                else:
                    self.add_token(TokenType.NUMBER_LITERAL, value)
                continue

            # Colon
            if ch == ':':
                self.advance()
                self.add_token(TokenType.COLON, ':')
                continue

            # Comma
            if ch == ',':
                self.advance()
                self.add_token(TokenType.COMMA, ',')
                continue

            # Try multi-word phrases first
            phrase_match = self.try_match_phrase()
            if phrase_match:
                phrase, token_type = phrase_match
                # Advance past the phrase
                for _ in phrase:
                    self.advance()
                self.add_token(token_type, phrase)
                continue

            # Words and keywords
            if ch.isalpha() or ch == '_':
                word = self.read_word()
                word_lower = word.lower()

                # Check for ordinals like "1st", "2nd", "3rd", "4th", etc.
                # These would have been caught earlier, so just handle words

                if word_lower in KEYWORDS:
                    self.add_token(KEYWORDS[word_lower], word)
                else:
                    self.add_token(TokenType.IDENTIFIER, word)
                continue

            # Skip unknown characters
            self.advance()

        self.add_token(TokenType.EOF, '')
        return self.tokens


def tokenize(source: str) -> List[Token]:
    """Convenience function to tokenize source code."""
    lexer = Lexer(source)
    return lexer.tokenize()


if __name__ == "__main__":
    # Test the lexer
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

    tokens = tokenize(test_code)
    for token in tokens:
        if token.type != TokenType.NEWLINE:
            print(token)
