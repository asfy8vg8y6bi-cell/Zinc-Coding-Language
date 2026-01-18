# Zinc Language Reference

Complete guide to the Zinc programming language - natural English syntax with C semantics.

## Table of Contents

1. [Data Types](#data-types)
2. [Variables](#variables)
3. [Changing Values](#changing-values)
4. [Displaying Output](#displaying-output)
5. [Functions](#functions)
6. [Conditions](#conditions)
7. [Loops](#loops)
8. [Math Operations](#math-operations)
9. [Arrays](#arrays)
10. [Structures](#structures)
11. [Pointers](#pointers)
12. [Input](#input)
13. [Comments](#comments)
14. [Including Libraries](#including-libraries)
15. [Complete Examples](#complete-examples)

---

## Data Types

| C Type | Zinc Type |
|--------|-----------|
| `int` | `number` |
| `float/double` | `decimal` |
| `char` | `letter` |
| `char*` | `text` |
| `bool` | `yes or no` / `boolean` |
| `void` | `nothing` |

---

## Variables

### Creating Variables

```zinc
there is a number called x
there is a number called age which is 25
there is text called name which is "Alice"
there is a decimal called price which is 19.99
there is a yes or no called found which is no
```

### Short Forms

```zinc
let x be 5
let name be "Bob"
number x is 5
```

---

## Changing Values

```zinc
change x to 10
set x to 20
now x is 30
make x equal to 40
add 5 to x
subtract 3 from x
multiply x by 2
divide x by 4
increase x
decrease x
```

---

## Displaying Output

```zinc
say "Hello, World!"
say "The answer is " and then answer
say "Name: " followed by name followed by " Age: " followed by age
print the value of x
show x
display "Done!"
```

---

## Functions

### Defining Functions

```zinc
to calculate the sum of number a and number b and return a number:
    let result be a plus b
    return result
end

to greet someone with text name:
    say "Hello, " and then name and then "!"
end

to do the main thing:
    say "Program starting..."
end
```

### Calling Functions

```zinc
calculate the sum of 5 and 3
greet someone with "Alice"
let answer be the result of calculate the sum of 10 and 20
```

---

## Conditions

### Simple If

```zinc
if x is greater than 10 then
    say "x is big"
end

if name equals "Alice" then
    say "Hello Alice!"
end
```

### If with Otherwise

```zinc
if x is greater than 100 then
    say "very big"
otherwise if x is greater than 50 then
    say "medium"
otherwise
    say "small"
end
```

### Condition Words

```zinc
if x is greater than y then ...
if x is less than y then ...
if x equals y then ...
if x is the same as y then ...
if x is not equal to y then ...
if x is at least 10 then ...
if x is at most 10 then ...
if x is between 5 and 10 then ...
if name contains "test" then ...
if list is empty then ...
if found is yes then ...
if done is no then ...
```

### Combining Conditions

```zinc
if x is greater than 5 and x is less than 10 then
    say "x is between 5 and 10"
end

if x equals 0 or y equals 0 then
    say "one of them is zero"
end

if it is not the case that x equals 0 then
    say "x is not zero"
end
```

---

## Loops

### Simple Repetition

```zinc
repeat 10 times:
    say "Hello!"
end
```

### While Loops

```zinc
while x is greater than 0:
    say x
    subtract 1 from x
end
```

### For Loops

```zinc
for each number i from 1 to 10:
    say i
end

for each number i from 10 down to 1:
    say i
end

for each item in the list:
    say the item
end
```

### Loop Control

```zinc
stop the loop
skip to the next one
leave the loop
continue with the next iteration
```

---

## Math Operations

```zinc
let result be 5 plus 3
let result be 10 minus 4
let result be 6 times 7
let result be 20 divided by 4
let result be 17 modulo 5

let result be a plus b times c
let result be the sum of a and b
let result be a to the power of 2
let result be the square root of 16
let result be the absolute value of negative 5
```

---

## Arrays

### Creating Arrays

```zinc
there is a list of numbers called scores
there is a list of 10 numbers called grades
there is a list of numbers called ages containing 25, 30, 35, 40
```

### Accessing Arrays

```zinc
the first item in scores
the last item in scores
item number 3 in scores
```

### Modifying Arrays

```zinc
set item number 0 in scores to 95
set the first item in scores to 100
```

### Array Info

```zinc
the length of scores
the size of the list
how many items are in scores
```

---

## Structures

### Defining

```zinc
define a Person as having:
    text called name
    number called age
    text called email
end
```

### Using

```zinc
there is a Person called bob
set bob's name to "Bob Smith"
set bob's age to 30

say bob's name
say "Age: " and then bob's age
```

---

## Pointers

```zinc
there is a pointer to a number called ptr
set ptr to the address of x
say the value that ptr points to
change the value at ptr to 100

allocate space for 10 numbers and call it data
free the memory at data
```

---

## Input

```zinc
ask the user for a number and store it in x
ask the user for text and store it in name
read a number into x
read text into name
```

---

## Comments

```zinc
note: this is a comment that explains the next line

notes:
    this is a longer comment
    that spans multiple lines
end notes

reminder: don't forget to handle edge cases
```

---

## Including Libraries

```zinc
include the standard input and output
include the standard math functions
include the file called "helpers"
use the string functions
```

---

## Complete Examples

### Example 1: Hello World

```zinc
include the standard input and output

to do the main thing:
    say "Hello, World!"
end
```

### Example 2: Ask for Name

```zinc
include the standard input and output

to do the main thing:
    there is text called name
    say "What is your name? "
    ask the user for text and store it in name
    say "Hello, " and then name and then "!"
end
```

### Example 3: Add Two Numbers

```zinc
include the standard input and output

to do the main thing:
    there is a number called a
    there is a number called b

    say "Enter first number: "
    ask the user for a number and store it in a

    say "Enter second number: "
    ask the user for a number and store it in b

    there is a number called sum which is a plus b
    say "The sum is " and then sum
end
```

### Example 4: Check Even or Odd

```zinc
include the standard input and output

to do the main thing:
    there is a number called n
    say "Enter a number: "
    ask the user for a number and store it in n

    if n modulo 2 equals 0 then
        say "The number is even"
    otherwise
        say "The number is odd"
    end
end
```

### Example 5: Factorial

```zinc
include the standard input and output

to calculate factorial of number n and return a number:
    if n is at most 1 then
        return 1
    end
    return n times the result of calculate factorial of n minus 1
end

to do the main thing:
    there is a number called n
    say "Enter a number: "
    ask the user for a number and store it in n

    there is a number called result
    set result to the result of calculate factorial of n

    say "Factorial is " and then result
end
```

### Example 6: Fibonacci Sequence

```zinc
include the standard input and output

to calculate fibonacci of number n and return a number:
    if n is at most 0 then
        return 0
    end
    if n equals 1 then
        return 1
    end
    there is a number called a which is the result of calculate fibonacci of n minus 1
    there is a number called b which is the result of calculate fibonacci of n minus 2
    return a plus b
end

to do the main thing:
    say "Fibonacci sequence:"
    for each number i from 0 to 10:
        there is a number called fib which is the result of calculate fibonacci of i
        say fib
    end
end
```

### Example 7: Count Down

```zinc
include the standard input and output

to do the main thing:
    there is a number called count which is 10

    say "Counting down..."

    while count is greater than 0:
        say count
        subtract 1 from count
    end

    say "Blast off!"
end
```

### Example 8: Sum of Array

```zinc
include the standard input and output

to do the main thing:
    there is a list of numbers called scores containing 85, 92, 78, 95, 88
    there is a number called total which is 0

    for each number score in scores:
        add score to total
    end

    say "The total is " and then total
end
```

### Example 9: Find Maximum

```zinc
include the standard input and output

to do the main thing:
    there is a list of numbers called data containing 34, 67, 23, 89, 12, 45
    there is a number called max which is the first item in data

    for each number value in data:
        if value is greater than max then
            set max to value
        end
    end

    say "The maximum value is " and then max
end
```

### Example 10: Simple Calculator

```zinc
include the standard input and output

to do the main thing:
    there is a number called a
    there is a number called b
    there is a number called choice

    say "Enter first number: "
    ask the user for a number and store it in a

    say "Enter second number: "
    ask the user for a number and store it in b

    say "1. Add"
    say "2. Subtract"
    say "3. Multiply"
    say "4. Divide"
    say "Enter choice: "
    ask the user for a number and store it in choice

    if choice equals 1 then
        say "Result: " and then a plus b
    otherwise if choice equals 2 then
        say "Result: " and then a minus b
    otherwise if choice equals 3 then
        say "Result: " and then a times b
    otherwise if choice equals 4 then
        say "Result: " and then a divided by b
    otherwise
        say "Invalid choice"
    end
end
```

### Example 11: Prime Number Check

```zinc
include the standard input and output
include the standard math functions

to check if number n is prime and return a number:
    if n is less than 2 then
        return 0
    end

    there is a number called i which is 2
    while i times i is at most n:
        if n modulo i equals 0 then
            return 0
        end
        increase i
    end

    return 1
end

to do the main thing:
    there is a number called n
    say "Enter a number: "
    ask the user for a number and store it in n

    there is a number called result which is the result of check if n is prime
    if result equals 1 then
        say "The number is prime"
    otherwise
        say "The number is not prime"
    end
end
```

### Example 12: Bubble Sort

```zinc
include the standard input and output

to do the main thing:
    there is a list of numbers called data containing 64, 34, 25, 12, 22, 11, 90
    there is a number called n which is 7

    say "Before sorting:"
    for each number x in data:
        say x
    end

    for each number i from 0 to n minus 2:
        for each number j from 0 to n minus i minus 2:
            if item number j in data is greater than item number j plus 1 in data then
                there is a number called temp which is item number j in data
                set item number j in data to item number j plus 1 in data
                set item number j plus 1 in data to temp
            end
        end
    end

    say "After sorting:"
    for each number x in data:
        say x
    end
end
```

### Example 13: Using Structures

```zinc
include the standard input and output

define a Student as having:
    number called age
    number called grade
end

to do the main thing:
    there is a Student called alice
    set alice's age to 20
    set alice's grade to 95

    say "Student age: " and then alice's age
    say "Student grade: " and then alice's grade
end
```

### Example 14: Guessing Game

```zinc
include the standard input and output
include the random functions

to do the main thing:
    there is a number called secret which is a random number between 1 and 100
    there is a number called guess which is 0
    there is a number called attempts which is 0

    say "I am thinking of a number between 1 and 100."

    while guess is not equal to secret:
        say "Enter your guess: "
        ask the user for a number and store it in guess
        increase attempts

        if guess is less than secret then
            say "Too low! Try again."
        otherwise if guess is greater than secret then
            say "Too high! Try again."
        otherwise
            say "Correct!"
        end
    end

    say "You got it in " and then attempts and then " attempts!"
end
```

### Example 15: Repeat Example

```zinc
include the standard input and output

to do the main thing:
    say "Repeating 5 times:"
    repeat 5 times:
        say "Hello!"
    end
end
```

### Example 16: Pointers Example

```zinc
include the standard input and output

to do the main thing:
    there is a number called x which is 5
    there is a number called y which is 10

    say "Before: x = " and then x and then ", y = " and then y

    there is a number called temp which is x
    set x to y
    set y to temp

    say "After: x = " and then x and then ", y = " and then y
end
```

### Example 17: Temperature Converter

```zinc
include the standard input and output

to do the main thing:
    there is a number called choice
    there is a decimal called temp

    say "Temperature Converter"
    say "1. Fahrenheit to Celsius"
    say "2. Celsius to Fahrenheit"
    say "Enter choice: "
    ask the user for a number and store it in choice

    if choice equals 1 then
        say "Enter temperature in Fahrenheit: "
        ask the user for a number and store it in temp
        there is a decimal called result which is temp minus 32 times 5 divided by 9
        say "Celsius: " and then result
    otherwise if choice equals 2 then
        say "Enter temperature in Celsius: "
        ask the user for a number and store it in temp
        there is a decimal called result which is temp times 9 divided by 5 plus 32
        say "Fahrenheit: " and then result
    otherwise
        say "Invalid choice"
    end
end
```

### Example 18: Countdown Loop

```zinc
include the standard input and output

to do the main thing:
    for each number i from 10 down to 1:
        say i
    end
    say "Blast off!"
end
```

### Example 19: Nested Loops

```zinc
include the standard input and output

to do the main thing:
    say "Multiplication table (1-5):"
    for each number i from 1 to 5:
        for each number j from 1 to 5:
            there is a number called product which is i times j
            say product
        end
    end
end
```

### Example 20: Break and Continue

```zinc
include the standard input and output

to do the main thing:
    say "Finding first number divisible by 7 (from 1 to 100):"

    for each number i from 1 to 100:
        if i modulo 7 equals 0 then
            say "Found: " and then i
            stop the loop
        end
    end

    say "Done!"
end
```

---

## Compiler Usage

```bash
python zinc.py examples/hello.zn              # Compile and create executable
python zinc.py examples/hello.zn -o hello     # Specify output name
python zinc.py examples/hello.zn --emit-c     # Output C code only
python zinc.py examples/hello.zn --run        # Compile and run immediately
python zinc.py examples/hello.zn --keep-c     # Keep intermediate C file
```
