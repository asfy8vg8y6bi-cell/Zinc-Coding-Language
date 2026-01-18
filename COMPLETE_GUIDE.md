# Zinc Programming Language - Complete Reference Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Philosophy & Design Principles](#philosophy--design-principles)
3. [Getting Started](#getting-started)
4. [C Syntax Fallback](#c-syntax-fallback)
5. [Program Structure](#program-structure)
6. [Data Types](#data-types)
7. [Variables](#variables)
8. [Constants & Literals](#constants--literals)
9. [Operators](#operators)
10. [Output Commands](#output-commands)
11. [Input Commands](#input-commands)
12. [Assignment Commands](#assignment-commands)
13. [Arithmetic Commands](#arithmetic-commands)
14. [Comparison Operators](#comparison-operators)
15. [Logical Operators](#logical-operators)
16. [Conditional Statements](#conditional-statements)
17. [Loops](#loops)
18. [Loop Control](#loop-control)
19. [Functions](#functions)
20. [Arrays](#arrays)
21. [Structures](#structures)
22. [Pointers & Memory](#pointers--memory)
23. [File Operations](#file-operations)
24. [GUI Operations (Raylib)](#gui-operations-raylib)
25. [Comments](#comments)
26. [Include Statements](#include-statements)
27. [Program Control](#program-control)
28. [Complete Syntax Reference Table](#complete-syntax-reference-table)
29. [Error Messages](#error-messages)
30. [Best Practices](#best-practices)
31. [Examples](#examples)

---

## Introduction

**Zinc** is a programming language designed to read like natural English while maintaining the power and performance of C. Zinc code is transpiled (converted) to C code, which is then compiled with GCC to produce native executables.

### Key Features
- Natural English syntax
- Compiles to efficient C code
- Full C interoperability
- No special symbols required (except for strings and numbers)
- Beginner-friendly while remaining powerful

---

## Philosophy & Design Principles

### Core Philosophy
1. **Readability First**: Code should read like instructions you'd give to a person
2. **No Cryptic Symbols**: Avoid `{}`, `()`, `&&`, `||` where possible
3. **Multiple Ways to Say Things**: Natural language has synonyms, so does Zinc
4. **C Compatibility**: When Zinc syntax doesn't exist, C syntax works

### Design Rules
- Keywords are case-insensitive (`Say` = `say` = `SAY`)
- Identifiers (variable names) are case-sensitive
- Whitespace is flexible (indentation is stylistic, not required)
- Line breaks separate statements
- Colons (`:`) are optional after control structures

---

## Getting Started

### Installation Requirements
- Python 3.6 or higher
- GCC (GNU C Compiler)
- For GUI: Raylib library

### Basic Usage

```bash
# Compile and create executable
python zinc.py program.zn

# Compile with custom output name
python zinc.py program.zn -o myprogram

# Output C code only (don't compile)
python zinc.py program.zn --emit-c

# Compile and run immediately
python zinc.py program.zn --run

# Keep intermediate C file
python zinc.py program.zn --keep-c
```

### File Extension
Zinc source files use the `.zn` extension.

---

## C Syntax Fallback

### IMPORTANT: C Compatibility Rule

**When Zinc doesn't have syntax for something, you can use C syntax directly.**

The Zinc transpiler passes through any unrecognized identifiers and function calls to the C compiler. This means:

```zinc
include the standard input and output

to do the main thing:
    // C-style comments work
    printf("Direct C call works!\n");

    int x = 5;  // C variable declaration

    // Mix Zinc and C freely
    there is a number called y which is 10
    printf("x = %d, y = %d\n", x, y);
end
```

### What C Syntax You Can Use

| C Feature | Example | Notes |
|-----------|---------|-------|
| Function calls | `printf("hello")` | Any C function |
| Variable declarations | `int x = 5;` | C-style declarations |
| Expressions | `x = (a + b) * c;` | C operators work |
| Pointer operations | `int *p = &x;` | Full pointer support |
| Array access | `arr[i] = 5;` | C-style indexing |
| Struct access | `obj.field` or `ptr->field` | Both syntaxes |
| Type casting | `(float)x` | C casts |
| Sizeof | `sizeof(int)` | Size operator |
| Ternary | `x ? a : b` | Conditional expression |
| Preprocessor | Won't work | Use Zinc includes |

### When to Use C Syntax
- Complex mathematical expressions
- Calling external C libraries
- Low-level memory operations
- Features not yet in Zinc
- Performance-critical sections

---

## Program Structure

### Basic Program Structure

```zinc
include the standard input and output

to do the main thing:
    say "Hello, World!"
end
```

### Full Program Structure

```zinc
// Include statements (at top)
include the standard input and output
include the standard math functions

// Structure definitions
define a Person as having:
    text called name
    number called age
end

// Function definitions
to greet with text name:
    say "Hello, " and then name
end

// Main function (required)
to do the main thing:
    // Program code here
end
```

### Rules
1. Include statements must come first
2. Structure definitions come before functions
3. Every program needs a `to do the main thing:` block
4. Functions can be defined in any order (forward declarations are automatic)

---

## Data Types

### Zinc Types and C Equivalents

| Zinc Type | C Type | Description | Default Value |
|-----------|--------|-------------|---------------|
| `number` | `int` | Whole numbers | `0` |
| `numbers` | `int` | Same as number (plural form) | `0` |
| `decimal` | `double` | Floating-point numbers | `0.0` |
| `decimals` | `double` | Same as decimal (plural form) | `0.0` |
| `letter` | `char` | Single character | `'\0'` |
| `letters` | `char` | Same as letter (plural form) | `'\0'` |
| `text` | `char*` | String of characters | `NULL` |
| `yes or no` | `int` | Boolean (1 or 0) | `0` |
| `boolean` | `int` | Same as yes or no | `0` |
| `nothing` | `void` | No value (for functions) | N/A |
| `pointer to X` | `X*` | Pointer to type X | `NULL` |
| `list of X` | `X[]` | Array of type X | `{0}` |

### Type Modifiers

| Modifier | Usage | Example |
|----------|-------|---------|
| `pointer to` | Creates pointer type | `pointer to number` → `int*` |
| `list of` | Creates array type | `list of numbers` → `int[]` |
| `list of N` | Fixed-size array | `list of 10 numbers` → `int[10]` |

---

## Variables

### Variable Declaration Syntax

#### Full Form
```zinc
there is a number called x
there is a number called age which is 25
there is an number called count which is 0
there is a decimal called price which is 19.99
there is text called name which is "Alice"
there is a yes or no called found which is no
there is a letter called grade which is 'A'
```

#### Short Forms
```zinc
let x be 5
let name be "Bob"
let found be yes
```

#### Type-First Form
```zinc
number x is 5
decimal pi is 3.14159
text greeting is "Hello"
```

### Variable Declaration Rules

| Rule | Correct | Incorrect |
|------|---------|-----------|
| Names start with letter | `count`, `x1` | `1count`, `_x` |
| No reserved words | `myNumber` | `number`, `if` |
| Case sensitive | `Name` ≠ `name` | - |
| No spaces in names | `firstName` | `first name` |

### All Declaration Variations

```zinc
// With "there is"
there is a number called x
there is an number called x
there is number called x

// With initial value
there is a number called x which is 5
there is a number called x which is 5 plus 3

// Short form
let x be 5
let x be 5 plus 3

// Type-first
number x is 5
```

---

## Constants & Literals

### Number Literals
```zinc
42          // positive integer
-17         // negative integer
0           // zero
```

### Decimal Literals
```zinc
3.14        // positive decimal
-2.5        // negative decimal
0.001       // small decimal
```

### String Literals
```zinc
"Hello, World!"           // basic string
"Line 1\nLine 2"          // with newline
"Tab\there"               // with tab
"She said \"Hi\""         // with escaped quote
""                        // empty string
```

### Character Literals
```zinc
'A'         // letter
'7'         // digit character
'\n'        // newline
'\t'        // tab
'\\'        // backslash
'\''        // single quote
```

### Boolean Literals
```zinc
yes         // true (1)
no          // false (0)
```

### Null Literal
```zinc
null        // null pointer
```

---

## Operators

### Arithmetic Operators (Natural English)

| Operation | Zinc Syntax | Example | Result |
|-----------|-------------|---------|--------|
| Addition | `plus` | `5 plus 3` | `8` |
| Subtraction | `minus` | `10 minus 4` | `6` |
| Multiplication | `times` | `6 times 7` | `42` |
| Division | `divided by` | `20 divided by 4` | `5` |
| Modulo | `modulo` | `17 modulo 5` | `2` |
| Power | `to the power of` | `2 to the power of 3` | `8` |
| Negation | `negative` | `negative 5` | `-5` |

### Arithmetic Functions

| Function | Zinc Syntax | Example |
|----------|-------------|---------|
| Square root | `the square root of X` | `the square root of 16` → `4` |
| Absolute value | `the absolute value of X` | `the absolute value of negative 5` → `5` |
| Sum | `the sum of X and Y` | `the sum of 3 and 4` → `7` |

### C Arithmetic Operators (Also Supported)

| Operation | C Syntax | Example |
|-----------|----------|---------|
| Addition | `+` | `5 + 3` |
| Subtraction | `-` | `10 - 4` |
| Multiplication | `*` | `6 * 7` |
| Division | `/` | `20 / 4` |
| Modulo | `%` | `17 % 5` |
| Increment | `++` | `x++` |
| Decrement | `--` | `x--` |

---

## Output Commands

### All Output Variations

| Command | Example | Notes |
|---------|---------|-------|
| `say` | `say "Hello"` | Primary output command |
| `print` | `print "Hello"` | Alias for say |
| `show` | `show x` | Alias for say |
| `display` | `display "Done"` | Alias for say |
| `print the value of` | `print the value of x` | Explicit value print |

### Concatenation in Output

```zinc
// Using "and then"
say "Hello, " and then name and then "!"

// Using "followed by"
say "Value: " followed by x followed by " units"

// Multiple and then
say "a=" and then a and then ", b=" and then b
```

### Output Rules
- Strings must be in double quotes
- Numbers are automatically converted to strings
- A newline is automatically added after each say/print
- Variables are printed according to their type

### Output Type Formatting

| Variable Type | Format | Example Output |
|---------------|--------|----------------|
| number | `%d` | `42` |
| decimal | `%f` | `3.140000` |
| text | `%s` | `Hello` |
| letter | `%c` | `A` |
| boolean | `%d` | `1` or `0` |

---

## Input Commands

### All Input Variations

| Command | Type | Example |
|---------|------|---------|
| `ask the user for a number and store it in X` | number | `ask the user for a number and store it in age` |
| `ask the user for a decimal and store it in X` | decimal | `ask the user for a decimal and store it in price` |
| `ask the user for text and store it in X` | text | `ask the user for text and store it in name` |
| `ask the user for a letter and store it in X` | letter | `ask the user for a letter and store it in grade` |
| `read a number into X` | number | `read a number into count` |
| `read text into X` | text | `read text into input` |
| `get input from the user as X` | text | `get input from the user as response` |

### Input Examples

```zinc
// Numbers
there is a number called age
say "Enter your age: "
ask the user for a number and store it in age

// Decimals
there is a decimal called price
say "Enter price: "
ask the user for a decimal and store it in price

// Text
there is text called name
say "Enter your name: "
ask the user for text and store it in name

// Letters
there is a letter called grade
say "Enter grade (A-F): "
ask the user for a letter and store it in grade
```

---

## Assignment Commands

### All Assignment Variations

| Command | Example | C Equivalent |
|---------|---------|--------------|
| `change X to Y` | `change x to 10` | `x = 10;` |
| `set X to Y` | `set x to 20` | `x = 20;` |
| `now X is Y` | `now x is 30` | `x = 30;` |
| `make X equal to Y` | `make x equal to 40` | `x = 40;` |
| `let X be Y` | `let x be 50` | `x = 50;` |

### Compound Assignment Commands

| Command | Example | C Equivalent |
|---------|---------|--------------|
| `add X to Y` | `add 5 to count` | `count = count + 5;` |
| `subtract X from Y` | `subtract 3 from count` | `count = count - 3;` |
| `multiply X by Y` | `multiply count by 2` | `count = count * 2;` |
| `divide X by Y` | `divide count by 4` | `count = count / 4;` |
| `increase X` | `increase count` | `count = count + 1;` |
| `decrease X` | `decrease count` | `count = count - 1;` |

### Assignment Examples

```zinc
there is a number called x which is 10

// All these do the same thing (set x to 20)
change x to 20
set x to 20
now x is 20
make x equal to 20

// Compound operations
add 5 to x          // x = x + 5
subtract 3 from x   // x = x - 3
multiply x by 2     // x = x * 2
divide x by 4       // x = x / 4
increase x          // x = x + 1
decrease x          // x = x - 1
```

---

## Comparison Operators

### All Comparison Variations

| Comparison | Zinc Syntax | C Equivalent |
|------------|-------------|--------------|
| Greater than | `X is greater than Y` | `X > Y` |
| Less than | `X is less than Y` | `X < Y` |
| Equal to | `X equals Y` | `X == Y` |
| Equal to | `X is the same as Y` | `X == Y` |
| Not equal | `X is not equal to Y` | `X != Y` |
| Not equal | `X is not Y` | `X != Y` |
| Greater or equal | `X is at least Y` | `X >= Y` |
| Less or equal | `X is at most Y` | `X <= Y` |
| Range check | `X is between A and B` | `X >= A && X <= B` |

### Special Comparisons

| Comparison | Zinc Syntax | C Equivalent |
|------------|-------------|--------------|
| Is positive | `X is positive` | `X > 0` |
| Is negative | `X is negative` | `X < 0` |
| Is zero | `X is zero` | `X == 0` |
| Is even | `X is even` | `X % 2 == 0` |
| Is odd | `X is odd` | `X % 2 != 0` |
| Is empty | `list is empty` | `length == 0` |
| Contains | `text contains "sub"` | `strstr(text, "sub")` |

### Boolean Value Checks

| Check | Zinc Syntax | Meaning |
|-------|-------------|---------|
| Is yes/true | `X is yes` | `X == 1` |
| Is no/false | `X is no` | `X == 0` |
| Equals yes | `X equals yes` | `X == 1` |
| Equals no | `X equals no` | `X == 0` |

---

## Logical Operators

### All Logical Operators

| Operation | Zinc Syntax | C Equivalent |
|-----------|-------------|--------------|
| AND | `X and Y` | `X && Y` |
| OR | `X or Y` | `X \|\| Y` |
| NOT | `not X` | `!X` |
| NOT (verbose) | `it is not the case that X` | `!X` |

### Combining Conditions

```zinc
// AND
if x is greater than 5 and x is less than 10 then
    say "x is between 5 and 10"
end

// OR
if x equals 0 or y equals 0 then
    say "one of them is zero"
end

// NOT
if not found then
    say "not found"
end

// Verbose NOT
if it is not the case that x equals 0 then
    say "x is not zero"
end

// Complex combinations
if x is greater than 0 and y is greater than 0 or z equals 0 then
    say "complex condition met"
end
```

---

## Conditional Statements

### If Statement

```zinc
if condition then
    // code
end
```

### If-Otherwise (If-Else)

```zinc
if condition then
    // code if true
otherwise
    // code if false
end
```

### If-Otherwise If-Otherwise (If-Else If-Else)

```zinc
if condition1 then
    // code if condition1 is true
otherwise if condition2 then
    // code if condition2 is true
otherwise if condition3 then
    // code if condition3 is true
otherwise
    // code if all conditions are false
end
```

### Nested Conditions

```zinc
if x is greater than 0 then
    if y is greater than 0 then
        say "both positive"
    otherwise
        say "x positive, y not"
    end
otherwise
    say "x not positive"
end
```

### Condition Examples

```zinc
// Simple comparison
if age is at least 18 then
    say "Adult"
end

// With otherwise
if score is at least 60 then
    say "Pass"
otherwise
    say "Fail"
end

// Multiple conditions
if grade is at least 90 then
    say "A"
otherwise if grade is at least 80 then
    say "B"
otherwise if grade is at least 70 then
    say "C"
otherwise if grade is at least 60 then
    say "D"
otherwise
    say "F"
end

// Compound conditions
if age is at least 18 and hasLicense is yes then
    say "Can drive"
end
```

---

## Loops

### While Loop

```zinc
while condition:
    // code
end
```

#### While Loop Variations
```zinc
// Standard while
while x is greater than 0:
    say x
    subtract 1 from x
end

// Keep doing while (alternative syntax)
keep doing this while condition:
    // code
end
```

### For Loop (For Each)

```zinc
// Ascending
for each number i from 1 to 10:
    say i
end

// Descending
for each number i from 10 down to 1:
    say i
end

// Iterating over array
for each number item in myList:
    say item
end
```

### Repeat Loop

```zinc
repeat 10 times:
    say "Hello!"
end

// With variable count
repeat n times:
    say "Repeating..."
end
```

### Loop Examples

```zinc
// Countdown
there is a number called count which is 10
while count is greater than 0:
    say count
    decrease count
end
say "Blast off!"

// Sum 1 to 100
there is a number called sum which is 0
for each number i from 1 to 100:
    add i to sum
end
say "Sum: " and then sum

// Print array
there is a list of numbers called data containing 1, 2, 3, 4, 5
for each number x in data:
    say x
end

// Repeat greeting
repeat 3 times:
    say "Hello!"
end
```

---

## Loop Control

### Break Statements (Exit Loop)

| Command | Effect |
|---------|--------|
| `stop the loop` | Exit the current loop |
| `leave the loop` | Exit the current loop |

### Continue Statements (Skip to Next Iteration)

| Command | Effect |
|---------|--------|
| `skip to the next one` | Skip to next iteration |
| `continue with the next iteration` | Skip to next iteration |

### Examples

```zinc
// Finding first match and stopping
for each number i from 1 to 100:
    if i modulo 7 equals 0 then
        say "First multiple of 7: " and then i
        stop the loop
    end
end

// Skipping even numbers
for each number i from 1 to 10:
    if i is even then
        skip to the next one
    end
    say i  // Only prints odd numbers
end
```

---

## Functions

### Function Definition Syntax

```zinc
to function_name_words:
    // code
end

to function_name with parameters:
    // code
end

to function_name with parameters and return a type:
    // code
    return value
end
```

### Function Variations

#### No Parameters, No Return
```zinc
to greet the user:
    say "Hello!"
end
```

#### With Parameters
```zinc
to greet someone with text name:
    say "Hello, " and then name
end

to add numbers number a and number b:
    there is a number called sum which is a plus b
    say sum
end
```

#### With Return Value
```zinc
to calculate the sum of number a and number b and return a number:
    return a plus b
end

to check if number n is even and return a yes or no:
    if n modulo 2 equals 0 then
        return yes
    end
    return no
end
```

### Calling Functions

```zinc
// Simple call
greet the user

// With arguments
greet someone with "Alice"

// Getting return value
there is a number called result
set result to the result of calculate the sum of 5 and 3

// Or using let
let answer be the result of calculate the sum of 10 and 20
```

### Function Rules

1. Function names can be multiple words
2. Parameters must have types specified
3. Return type comes after `and return a/an`
4. Use `the result of` to capture return values
5. Functions are automatically forward-declared

### Main Function

Every program must have a main function:

```zinc
to do the main thing:
    // Program entry point
end
```

---

## Arrays

### Array Declaration

```zinc
// Empty array (dynamic)
there is a list of numbers called scores

// Fixed size array
there is a list of 10 numbers called grades

// Array with initial values
there is a list of numbers called ages containing 25, 30, 35, 40

// Multiple types
there is a list of decimals called prices containing 1.99, 2.49, 3.99
there is a list of letters called vowels containing 'a', 'e', 'i', 'o', 'u'
```

### Array Access

| Operation | Zinc Syntax | C Equivalent |
|-----------|-------------|--------------|
| First element | `the first item in arr` | `arr[0]` |
| Last element | `the last item in arr` | `arr[length-1]` |
| By index | `item number 3 in arr` | `arr[3]` |
| By index | `the 5th element of arr` | `arr[5]` |

### Array Modification

```zinc
// Set by index
set item number 0 in scores to 95
set the first item in scores to 100

// Using expressions
set item number i in data to i times 2
```

### Array Properties

| Property | Zinc Syntax | C Equivalent |
|----------|-------------|--------------|
| Length | `the length of arr` | `sizeof(arr)/sizeof(arr[0])` |
| Size | `the size of arr` | Same as length |
| Count | `how many items are in arr` | Same as length |

### Array Examples

```zinc
// Initialize and use
there is a list of numbers called data containing 10, 20, 30, 40, 50

// Access elements
say the first item in data    // 10
say the last item in data     // 50
say item number 2 in data     // 30

// Iterate
for each number x in data:
    say x
end

// Sum array
there is a number called total which is 0
for each number value in data:
    add value to total
end
say "Total: " and then total

// Modify
set item number 0 in data to 100
set the first item in data to 999
```

---

## Structures

### Structure Definition

```zinc
define a Person as having:
    text called name
    number called age
    text called email
end

define a Point as having:
    number called x
    number called y
end

define a Rectangle as having:
    number called x
    number called y
    number called width
    number called height
end
```

### Structure Usage

```zinc
// Declare struct variable
there is a Person called bob

// Set fields using possessive
set bob's name to "Bob Smith"
set bob's age to 30
set bob's email to "bob@example.com"

// Access fields
say bob's name
say "Age: " and then bob's age

// Initialize with values (limited support)
there is a Person called alice which has name "Alice" and age 25
```

### Structure Examples

```zinc
define a Student as having:
    text called name
    number called id
    decimal called gpa
end

to do the main thing:
    there is a Student called s1
    set s1's name to "John"
    set s1's id to 12345
    set s1's gpa to 3.75

    say "Student: " and then s1's name
    say "ID: " and then s1's id
    say "GPA: " and then s1's gpa
end
```

---

## Pointers & Memory

### Pointer Declaration

```zinc
there is a pointer to a number called ptr
there is a pointer to text called strPtr
there is a pointer to a Person called personPtr
```

### Pointer Operations

| Operation | Zinc Syntax | C Equivalent |
|-----------|-------------|--------------|
| Get address | `the address of x` | `&x` |
| Dereference | `the value at ptr` | `*ptr` |
| Dereference | `the value that ptr points to` | `*ptr` |
| Set via pointer | `set the value at ptr to 10` | `*ptr = 10` |

### Dynamic Memory

```zinc
// Allocate
allocate space for 10 numbers and call it data

// Use
set item number 0 in data to 42

// Free
free the memory at data
```

### Pointer Examples

```zinc
to do the main thing:
    there is a number called x which is 5
    there is a pointer to a number called ptr

    // Get address
    set ptr to the address of x

    // Read via pointer
    say the value at ptr  // prints 5

    // Write via pointer
    set the value at ptr to 100
    say x  // prints 100
end

// Dynamic allocation
to do the main thing:
    there is a number called size which is 5
    allocate space for size numbers and call it arr

    for each number i from 0 to size minus 1:
        set item number i in arr to i times 10
    end

    for each number i from 0 to size minus 1:
        say item number i in arr
    end

    free the memory at arr
end
```

---

## File Operations

### File Declaration

```zinc
there is a file called input which opens "data.txt" for reading
there is a file called output which opens "result.txt" for writing
```

### File Operations

| Operation | Zinc Syntax |
|-----------|-------------|
| Open for reading | `opens "file.txt" for reading` |
| Open for writing | `opens "file.txt" for writing` |
| Check if open failed | `if input failed to open then` |
| Check for more lines | `while there is another line in input` |
| Read line | `read a line from input into line` |
| Close file | `close the file input` |

### File Examples

```zinc
include the standard input and output
include the file functions

to do the main thing:
    there is a file called input which opens "data.txt" for reading

    if input failed to open then
        say "Could not open file!"
        stop the program
    end

    there is text called line

    while there is another line in input:
        read a line from input into line
        say line
    end

    close the file input
end
```

---

## GUI Operations (Raylib)

### Include Graphics Library

```zinc
include the graphics library
// or
include raylib graphics
```

### Window Operations

| Operation | Zinc Syntax | Raylib Equivalent |
|-----------|-------------|-------------------|
| Open window | `open a window sized W by H called "Title"` | `InitWindow(W, H, "Title")` |
| Close window | `close the window` | `CloseWindow()` |
| Check close | `the window should close` | `WindowShouldClose()` |

### Drawing Operations

| Operation | Zinc Syntax | Raylib Equivalent |
|-----------|-------------|-------------------|
| Begin drawing | `begin drawing` | `BeginDrawing()` |
| End drawing | `end drawing` | `EndDrawing()` |
| Clear screen | `clear the screen with COLOR` | `ClearBackground(COLOR)` |
| Draw rectangle | `draw a rectangle at X, Y sized W by H in COLOR` | `DrawRectangle(X,Y,W,H,COLOR)` |
| Draw text | `draw text "str" at X, Y size S in COLOR` | `DrawText("str",X,Y,S,COLOR)` |

### Input Operations

| Operation | Zinc Syntax | Raylib Equivalent |
|-----------|-------------|-------------------|
| Mouse X | `the mouse x position` | `GetMouseX()` |
| Mouse Y | `the mouse y position` | `GetMouseY()` |
| Mouse click | `the mouse was clicked` | `IsMouseButtonPressed(MOUSE_LEFT_BUTTON)` |

### Available Colors

`BLACK`, `WHITE`, `GRAY`, `DARKGRAY`, `LIGHTGRAY`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `ORANGE`, `PINK`, `PURPLE`, `RAYWHITE`

### GUI Example

```zinc
include the standard input and output
include the graphics library

to do the main thing:
    open a window sized 800 by 600 called "My App"

    there is a number called running which is 1

    while running equals 1:
        if the window should close then
            set running to 0
        end

        begin drawing
        clear the screen with RAYWHITE
        draw text "Hello, GUI!" at 300, 250 size 40 in BLACK
        draw a rectangle at 100, 100 sized 200 by 100 in BLUE
        end drawing
    end

    close the window
end
```

---

## Comments

### Single-Line Comments

```zinc
note: this is a comment

reminder: don't forget to handle edge cases

// C-style comments also work
```

### Multi-Line Comments

```zinc
notes:
    This is a longer comment
    that spans multiple lines
    explaining something complex
end notes

/* C-style multi-line
   comments also work */
```

---

## Include Statements

### All Include Variations

| Include | Zinc Syntax | C Header |
|---------|-------------|----------|
| Standard I/O | `include the standard input and output` | `<stdio.h>` |
| Math | `include the standard math functions` | `<math.h>` |
| Strings | `include the string functions` | `<string.h>` |
| Files | `include the file functions` | `<stdio.h>` |
| Random | `include the random functions` | `<stdlib.h>` |
| Graphics | `include the graphics library` | `"raylib.h"` |
| Custom | `include the file called "myfile"` | `"myfile.h"` |

### Alternative Syntax

```zinc
use the standard input and output
use the string functions
```

---

## Program Control

### Exit Program

```zinc
stop the program    // Equivalent to return 1 from main
```

### Return from Function

```zinc
return              // Return void
return value        // Return a value
```

---

## Complete Syntax Reference Table

### Variables

| Action | Zinc Syntax |
|--------|-------------|
| Declare number | `there is a number called X` |
| Declare with value | `there is a number called X which is Y` |
| Short declaration | `let X be Y` |
| Type-first | `number X is Y` |

### Assignment

| Action | Zinc Syntax |
|--------|-------------|
| Assign | `set X to Y` |
| Assign | `change X to Y` |
| Assign | `now X is Y` |
| Assign | `make X equal to Y` |
| Add | `add Y to X` |
| Subtract | `subtract Y from X` |
| Multiply | `multiply X by Y` |
| Divide | `divide X by Y` |
| Increment | `increase X` |
| Decrement | `decrease X` |

### Output

| Action | Zinc Syntax |
|--------|-------------|
| Print | `say "text"` |
| Print | `print "text"` |
| Print | `show X` |
| Print | `display "text"` |
| Concatenate | `say X and then Y` |
| Concatenate | `say X followed by Y` |

### Input

| Action | Zinc Syntax |
|--------|-------------|
| Read number | `ask the user for a number and store it in X` |
| Read decimal | `ask the user for a decimal and store it in X` |
| Read text | `ask the user for text and store it in X` |
| Read letter | `ask the user for a letter and store it in X` |

### Conditions

| Action | Zinc Syntax |
|--------|-------------|
| If | `if COND then ... end` |
| If-else | `if COND then ... otherwise ... end` |
| Else-if | `otherwise if COND then` |

### Comparisons

| Comparison | Zinc Syntax |
|------------|-------------|
| Greater | `X is greater than Y` |
| Less | `X is less than Y` |
| Equal | `X equals Y` |
| Not equal | `X is not equal to Y` |
| >= | `X is at least Y` |
| <= | `X is at most Y` |
| Range | `X is between A and B` |

### Loops

| Loop | Zinc Syntax |
|------|-------------|
| While | `while COND: ... end` |
| For | `for each number I from A to B: ... end` |
| For down | `for each number I from A down to B: ... end` |
| For each | `for each number X in LIST: ... end` |
| Repeat | `repeat N times: ... end` |

### Loop Control

| Action | Zinc Syntax |
|--------|-------------|
| Break | `stop the loop` |
| Break | `leave the loop` |
| Continue | `skip to the next one` |
| Continue | `continue with the next iteration` |

### Functions

| Action | Zinc Syntax |
|--------|-------------|
| Define | `to NAME: ... end` |
| With params | `to NAME with TYPE PARAM: ... end` |
| With return | `to NAME and return a TYPE: ... end` |
| Call | `NAME` or `the result of NAME` |

### Arrays

| Action | Zinc Syntax |
|--------|-------------|
| Declare | `there is a list of numbers called X` |
| With size | `there is a list of N numbers called X` |
| With values | `there is a list of numbers called X containing A, B, C` |
| First | `the first item in X` |
| Last | `the last item in X` |
| Index | `item number I in X` |
| Length | `the length of X` |

### Pointers

| Action | Zinc Syntax |
|--------|-------------|
| Declare | `there is a pointer to a number called X` |
| Address | `the address of X` |
| Dereference | `the value at X` |
| Allocate | `allocate space for N numbers and call it X` |
| Free | `free the memory at X` |

---

## Error Messages

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Unexpected token at top level` | Code outside function | Put code inside `to do the main thing:` |
| `Expected THEN` | Missing `then` after condition | Add `then` after if condition |
| `Expected IDENTIFIER` | Using reserved word as variable | Choose different variable name |
| `Unterminated string literal` | Missing closing quote | Add `"` at end of string |
| `gcc not found` | No C compiler | Install GCC |

---

## Best Practices

### Naming Conventions
- Use descriptive variable names: `totalScore` not `ts`
- Use camelCase for variables: `firstName`, `lastValue`
- Avoid single letters except for loop counters

### Code Organization
- Put includes at the top
- Define structures before functions
- Group related functions together
- Comment complex logic

### Performance Tips
- Use C syntax for complex math expressions
- Avoid unnecessary string concatenations in loops
- Use fixed-size arrays when size is known
- Free dynamically allocated memory

### Debugging Tips
- Use `--emit-c` to see generated C code
- Add `say` statements to trace execution
- Check variable types match operations
- Verify loop bounds

---

## Examples

### Example 1: Hello World
```zinc
include the standard input and output

to do the main thing:
    say "Hello, World!"
end
```

### Example 2: Temperature Converter
```zinc
include the standard input and output

to do the main thing:
    there is a decimal called fahrenheit
    say "Enter temperature in Fahrenheit: "
    ask the user for a decimal and store it in fahrenheit

    there is a decimal called celsius which is fahrenheit minus 32 times 5 divided by 9
    say "Celsius: " and then celsius
end
```

### Example 3: Factorial
```zinc
include the standard input and output

to calculate factorial of number n and return a number:
    if n is at most 1 then
        return 1
    end
    there is a number called prev which is n minus 1
    there is a number called sub which is the result of calculate factorial of prev
    return n times sub
end

to do the main thing:
    there is a number called n
    say "Enter a number: "
    ask the user for a number and store it in n

    there is a number called result which is the result of calculate factorial of n
    say "Factorial: " and then result
end
```

### Example 4: FizzBuzz
```zinc
include the standard input and output

to do the main thing:
    for each number i from 1 to 100:
        if i modulo 15 equals 0 then
            say "FizzBuzz"
        otherwise if i modulo 3 equals 0 then
            say "Fizz"
        otherwise if i modulo 5 equals 0 then
            say "Buzz"
        otherwise
            say i
        end
    end
end
```

### Example 5: Bubble Sort
```zinc
include the standard input and output

to do the main thing:
    there is a list of numbers called arr containing 64, 34, 25, 12, 22, 11, 90
    there is a number called n which is 7

    for each number i from 0 to n minus 2:
        for each number j from 0 to n minus i minus 2:
            if item number j in arr is greater than item number j plus 1 in arr then
                there is a number called temp which is item number j in arr
                set item number j in arr to item number j plus 1 in arr
                set item number j plus 1 in arr to temp
            end
        end
    end

    say "Sorted array:"
    for each number x in arr:
        say x
    end
end
```

### Example 6: Using C Syntax Fallback
```zinc
include the standard input and output
include the standard math functions

to do the main thing:
    // Mix of Zinc and C
    there is a decimal called x which is 2.5

    // C function calls work directly
    double result = sin(x) + cos(x);
    printf("sin(%.2f) + cos(%.2f) = %.4f\n", x, x, result);

    // Complex C expressions
    int arr[5] = {1, 2, 3, 4, 5};
    for (int i = 0; i < 5; i++) {
        printf("%d ", arr[i] * arr[i]);
    }
    printf("\n");

    // Back to Zinc
    say "Done with mixed syntax!"
end
```

---

## Appendix: Reserved Words

The following words cannot be used as variable names:

```
a, add, allocate, an, and, ask, at, be, begin, boolean, by, called,
change, close, containing, decimal, decrease, define, display, divide,
do, down, drawing, each, end, equals, file, first, for, free, from,
get, greater, has, having, if, in, include, increase, input, is, item,
last, least, length, less, let, list, loop, main, make, modulo, most,
mouse, multiply, negative, next, no, not, nothing, notes, now, null,
number, of, open, or, otherwise, output, plus, pointer, print, random,
read, reminder, repeat, result, return, say, screen, set, show, size,
sized, skip, space, standard, stop, store, subtract, text, than, the,
then, there, thing, times, to, user, value, which, while, window, with,
yes
```

---

*Zinc Programming Language - Version 1.0*
*Created for natural, readable programming*
