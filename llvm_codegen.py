"""
Zinc LLVM Code Generator - Compiles bytecode to native code via LLVM.

This module takes a CompiledProgram and generates LLVM IR, which is then
compiled to native machine code using LLVM's JIT or AOT compilation.

Requires: llvmlite (pip install llvmlite)
"""

import sys
from typing import List, Dict, Optional, Tuple
from bytecode import (
    OpCode, Instruction, Function, StructDef, CompiledProgram,
    ValueType
)

try:
    from llvmlite import ir, binding
    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False


def check_llvm():
    """Check if LLVM is available."""
    if not LLVM_AVAILABLE:
        print("Error: llvmlite not installed. Install with: pip install llvmlite", file=sys.stderr)
        sys.exit(1)


# Initialize LLVM
def init_llvm():
    """Initialize the LLVM backend."""
    check_llvm()
    binding.initialize()
    binding.initialize_native_target()
    binding.initialize_native_asmprinter()


class LLVMCodeGenerator:
    """Generates LLVM IR from compiled Zinc bytecode."""

    def __init__(self):
        check_llvm()
        self.module: Optional[ir.Module] = None
        self.builder: Optional[ir.IRBuilder] = None
        self.func_map: Dict[str, ir.Function] = {}
        self.local_map: Dict[int, ir.AllocaInstr] = {}
        self.string_map: Dict[str, ir.GlobalVariable] = {}
        self.string_counter = 0

        # LLVM types
        self.i8 = ir.IntType(8)
        self.i32 = ir.IntType(32)
        self.i64 = ir.IntType(64)
        self.double = ir.DoubleType()
        self.void = ir.VoidType()
        self.i8_ptr = ir.PointerType(self.i8)
        self.bool_type = ir.IntType(1)

        # Value type enum values
        self.VAL_INT = 0
        self.VAL_FLOAT = 1
        self.VAL_STRING = 2
        self.VAL_CHAR = 3
        self.VAL_BOOL = 4
        self.VAL_NULL = 5
        self.VAL_ARRAY = 6

        # Value struct type: { i32 type, i64 data }
        # We use a simple tagged union representation
        self.value_type = ir.LiteralStructType([self.i32, self.i64])
        self.value_ptr = ir.PointerType(self.value_type)

        # Array struct: { Value* data, i32 len, i32 cap }
        self.array_type = ir.LiteralStructType([self.value_ptr, self.i32, self.i32])
        self.array_ptr = ir.PointerType(self.array_type)

    def generate(self, program: CompiledProgram) -> ir.Module:
        """Generate LLVM IR from a compiled program."""
        self.module = ir.Module(name="zinc_program")
        self.module.triple = binding.get_default_triple()

        self._declare_runtime_functions()
        self._generate_functions(program)

        return self.module

    def _declare_runtime_functions(self):
        """Declare external C runtime functions."""
        # printf
        printf_ty = ir.FunctionType(self.i32, [self.i8_ptr], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

        # puts
        puts_ty = ir.FunctionType(self.i32, [self.i8_ptr])
        self.puts = ir.Function(self.module, puts_ty, name="puts")

        # scanf
        scanf_ty = ir.FunctionType(self.i32, [self.i8_ptr], var_arg=True)
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")

        # malloc
        malloc_ty = ir.FunctionType(self.i8_ptr, [self.i64])
        self.malloc = ir.Function(self.module, malloc_ty, name="malloc")

        # free
        free_ty = ir.FunctionType(self.void, [self.i8_ptr])
        self.free = ir.Function(self.module, free_ty, name="free")

        # sqrt
        sqrt_ty = ir.FunctionType(self.double, [self.double])
        self.sqrt = ir.Function(self.module, sqrt_ty, name="sqrt")

        # fabs
        fabs_ty = ir.FunctionType(self.double, [self.double])
        self.fabs = ir.Function(self.module, fabs_ty, name="fabs")

        # pow
        pow_ty = ir.FunctionType(self.double, [self.double, self.double])
        self.pow = ir.Function(self.module, pow_ty, name="pow")

        # fmod
        fmod_ty = ir.FunctionType(self.double, [self.double, self.double])
        self.fmod = ir.Function(self.module, fmod_ty, name="fmod")

        # rand
        rand_ty = ir.FunctionType(self.i32, [])
        self.rand = ir.Function(self.module, rand_ty, name="rand")

        # srand
        srand_ty = ir.FunctionType(self.void, [self.i32])
        self.srand = ir.Function(self.module, srand_ty, name="srand")

        # time
        time_ty = ir.FunctionType(self.i64, [self.i8_ptr])
        self.time = ir.Function(self.module, time_ty, name="time")

        # getchar
        getchar_ty = ir.FunctionType(self.i32, [])
        self.getchar = ir.Function(self.module, getchar_ty, name="getchar")

        # fgets
        fgets_ty = ir.FunctionType(self.i8_ptr, [self.i8_ptr, self.i32, self.i8_ptr])
        self.fgets = ir.Function(self.module, fgets_ty, name="fgets")

        # stdin - declare as external global
        self.stdin_ptr = ir.GlobalVariable(self.module, self.i8_ptr, name="stdin")
        self.stdin_ptr.linkage = "external"

        # atoll
        atoll_ty = ir.FunctionType(self.i64, [self.i8_ptr])
        self.atoll = ir.Function(self.module, atoll_ty, name="atoll")

        # atof
        atof_ty = ir.FunctionType(self.double, [self.i8_ptr])
        self.atof = ir.Function(self.module, atof_ty, name="atof")

        # strlen
        strlen_ty = ir.FunctionType(self.i64, [self.i8_ptr])
        self.strlen = ir.Function(self.module, strlen_ty, name="strlen")

        # strcpy
        strcpy_ty = ir.FunctionType(self.i8_ptr, [self.i8_ptr, self.i8_ptr])
        self.strcpy = ir.Function(self.module, strcpy_ty, name="strcpy")

        # strcat
        strcat_ty = ir.FunctionType(self.i8_ptr, [self.i8_ptr, self.i8_ptr])
        self.strcat = ir.Function(self.module, strcat_ty, name="strcat")

        # strcmp
        strcmp_ty = ir.FunctionType(self.i32, [self.i8_ptr, self.i8_ptr])
        self.strcmp = ir.Function(self.module, strcmp_ty, name="strcmp")

        # strstr
        strstr_ty = ir.FunctionType(self.i8_ptr, [self.i8_ptr, self.i8_ptr])
        self.strstr = ir.Function(self.module, strstr_ty, name="strstr")

    def _get_string_constant(self, s: str) -> ir.GlobalVariable:
        """Get or create a global string constant."""
        if s in self.string_map:
            return self.string_map[s]

        # Create the string constant
        encoded = (s + '\0').encode('utf-8')
        str_type = ir.ArrayType(self.i8, len(encoded))
        str_const = ir.Constant(str_type, bytearray(encoded))

        name = f".str.{self.string_counter}"
        self.string_counter += 1

        global_str = ir.GlobalVariable(self.module, str_type, name=name)
        global_str.global_constant = True
        global_str.linkage = "private"
        global_str.initializer = str_const

        self.string_map[s] = global_str
        return global_str

    def _get_string_ptr(self, s: str) -> ir.Value:
        """Get a pointer to a string constant."""
        global_str = self._get_string_constant(s)
        zero = ir.Constant(self.i32, 0)
        return self.builder.gep(global_str, [zero, zero], inbounds=True)

    def _generate_functions(self, program: CompiledProgram):
        """Generate all functions."""
        # First pass: declare all functions
        for name, func in program.functions.items():
            self._declare_function(name, func)

        # Second pass: define all functions
        for name, func in program.functions.items():
            self._generate_function(name, func, program)

    def _declare_function(self, name: str, func: Function):
        """Declare a function."""
        # All Zinc functions take and return i64 (boxed values)
        param_types = [self.i64] * len(func.params)
        ret_type = self.i64

        if name == "main":
            # Main function signature for C compatibility
            func_type = ir.FunctionType(self.i32, [])
            llvm_func = ir.Function(self.module, func_type, name="main")
        else:
            func_type = ir.FunctionType(ret_type, param_types)
            c_name = f"_zinc_{self._mangle_name(name)}"
            llvm_func = ir.Function(self.module, func_type, name=c_name)

        self.func_map[name] = llvm_func

    def _mangle_name(self, name: str) -> str:
        """Mangle a name for C compatibility."""
        result = []
        for c in name:
            if c.isalnum() or c == '_':
                result.append(c)
            else:
                result.append('_')
        return ''.join(result) or '_unnamed'

    def _generate_function(self, name: str, func: Function, program: CompiledProgram):
        """Generate a function body."""
        llvm_func = self.func_map[name]
        entry = llvm_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry)

        self.local_map = {}
        self.block_map = {}

        # Allocate locals
        for i in range(func.locals_count):
            alloca = self.builder.alloca(self.i64, name=f"local_{i}")
            self.builder.store(ir.Constant(self.i64, 0), alloca)
            self.local_map[i] = alloca

        # Store parameters in locals
        if name != "main":
            for i, arg in enumerate(llvm_func.args):
                arg.name = f"arg_{i}"
                if i in self.local_map:
                    self.builder.store(arg, self.local_map[i])

        # Create a simple stack for expression evaluation
        self.stack = []
        self.stack_alloca = self.builder.alloca(ir.ArrayType(self.i64, 256), name="stack")
        self.sp_alloca = self.builder.alloca(self.i32, name="sp")
        self.builder.store(ir.Constant(self.i32, 0), self.sp_alloca)

        # Pre-create basic blocks for jump targets
        jump_targets = set()
        for i, instr in enumerate(func.code):
            if instr.opcode in (OpCode.JUMP, OpCode.JUMP_IF_FALSE, OpCode.JUMP_IF_TRUE):
                if instr.operand is not None:
                    jump_targets.add(instr.operand)

        for target in jump_targets:
            self.block_map[target] = llvm_func.append_basic_block(name=f"L{target}")

        # Generate instructions
        for i, instr in enumerate(func.code):
            # Check if this is a jump target - create new block
            if i in self.block_map:
                # If current block is not terminated, add branch
                if not self.builder.block.is_terminated:
                    self.builder.branch(self.block_map[i])
                self.builder.position_at_end(self.block_map[i])

            self._generate_instruction(instr, i, func, program)

        # Add default return if not terminated
        if not self.builder.block.is_terminated:
            if name == "main":
                self.builder.ret(ir.Constant(self.i32, 0))
            else:
                self.builder.ret(ir.Constant(self.i64, 0))

    def _push(self, value: ir.Value):
        """Push a value onto the expression stack."""
        sp = self.builder.load(self.sp_alloca)
        zero = ir.Constant(self.i32, 0)
        ptr = self.builder.gep(self.stack_alloca, [zero, sp], inbounds=True)
        self.builder.store(value, ptr)
        new_sp = self.builder.add(sp, ir.Constant(self.i32, 1))
        self.builder.store(new_sp, self.sp_alloca)

    def _pop(self) -> ir.Value:
        """Pop a value from the expression stack."""
        sp = self.builder.load(self.sp_alloca)
        new_sp = self.builder.sub(sp, ir.Constant(self.i32, 1))
        self.builder.store(new_sp, self.sp_alloca)
        zero = ir.Constant(self.i32, 0)
        ptr = self.builder.gep(self.stack_alloca, [zero, new_sp], inbounds=True)
        return self.builder.load(ptr)

    def _peek(self) -> ir.Value:
        """Peek at the top of the stack."""
        sp = self.builder.load(self.sp_alloca)
        idx = self.builder.sub(sp, ir.Constant(self.i32, 1))
        zero = ir.Constant(self.i32, 0)
        ptr = self.builder.gep(self.stack_alloca, [zero, idx], inbounds=True)
        return self.builder.load(ptr)

    def _generate_instruction(self, instr: Instruction, idx: int, func: Function, program: CompiledProgram):
        """Generate LLVM IR for a single bytecode instruction."""
        op = instr.opcode
        operand = instr.operand

        if op == OpCode.PUSH_INT:
            self._push(ir.Constant(self.i64, operand))

        elif op == OpCode.PUSH_FLOAT:
            # Store float bits as i64
            float_val = ir.Constant(self.double, operand)
            int_val = self.builder.bitcast(float_val, self.i64)
            self._push(int_val)

        elif op == OpCode.PUSH_STRING:
            str_ptr = self._get_string_ptr(operand or "")
            int_val = self.builder.ptrtoint(str_ptr, self.i64)
            self._push(int_val)

        elif op == OpCode.PUSH_CHAR:
            c = operand if operand else '\0'
            self._push(ir.Constant(self.i64, ord(c)))

        elif op == OpCode.PUSH_BOOL:
            self._push(ir.Constant(self.i64, 1 if operand else 0))

        elif op == OpCode.PUSH_NULL:
            self._push(ir.Constant(self.i64, 0))

        elif op == OpCode.POP:
            self._pop()

        elif op == OpCode.DUP:
            val = self._peek()
            self._push(val)

        elif op == OpCode.LOAD_LOCAL:
            val = self.builder.load(self.local_map[operand])
            self._push(val)

        elif op == OpCode.STORE_LOCAL:
            val = self._pop()
            self.builder.store(val, self.local_map[operand])

        elif op == OpCode.ADD:
            b = self._pop()
            a = self._pop()
            result = self.builder.add(a, b)
            self._push(result)

        elif op == OpCode.SUB:
            b = self._pop()
            a = self._pop()
            result = self.builder.sub(a, b)
            self._push(result)

        elif op == OpCode.MUL:
            b = self._pop()
            a = self._pop()
            result = self.builder.mul(a, b)
            self._push(result)

        elif op == OpCode.DIV:
            b = self._pop()
            a = self._pop()
            result = self.builder.sdiv(a, b)
            self._push(result)

        elif op == OpCode.MOD:
            b = self._pop()
            a = self._pop()
            result = self.builder.srem(a, b)
            self._push(result)

        elif op == OpCode.NEG:
            a = self._pop()
            result = self.builder.neg(a)
            self._push(result)

        elif op == OpCode.EQ:
            b = self._pop()
            a = self._pop()
            cmp = self.builder.icmp_signed('==', a, b)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.NE:
            b = self._pop()
            a = self._pop()
            cmp = self.builder.icmp_signed('!=', a, b)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.LT:
            b = self._pop()
            a = self._pop()
            cmp = self.builder.icmp_signed('<', a, b)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.LE:
            b = self._pop()
            a = self._pop()
            cmp = self.builder.icmp_signed('<=', a, b)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.GT:
            b = self._pop()
            a = self._pop()
            cmp = self.builder.icmp_signed('>', a, b)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.GE:
            b = self._pop()
            a = self._pop()
            cmp = self.builder.icmp_signed('>=', a, b)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.NOT:
            a = self._pop()
            zero = ir.Constant(self.i64, 0)
            cmp = self.builder.icmp_signed('==', a, zero)
            result = self.builder.zext(cmp, self.i64)
            self._push(result)

        elif op == OpCode.JUMP:
            target_block = self.block_map.get(operand)
            if target_block:
                self.builder.branch(target_block)

        elif op == OpCode.JUMP_IF_FALSE:
            cond = self._pop()
            zero = ir.Constant(self.i64, 0)
            is_false = self.builder.icmp_signed('==', cond, zero)

            target_block = self.block_map.get(operand)
            if target_block:
                # Create a fallthrough block
                fallthrough = self.func_map[func.name].append_basic_block(name=f"fall_{idx}")
                self.builder.cbranch(is_false, target_block, fallthrough)
                self.builder.position_at_end(fallthrough)

        elif op == OpCode.JUMP_IF_TRUE:
            cond = self._pop()
            zero = ir.Constant(self.i64, 0)
            is_true = self.builder.icmp_signed('!=', cond, zero)

            target_block = self.block_map.get(operand)
            if target_block:
                fallthrough = self.func_map[func.name].append_basic_block(name=f"fall_{idx}")
                self.builder.cbranch(is_true, target_block, fallthrough)
                self.builder.position_at_end(fallthrough)

        elif op == OpCode.CALL:
            func_name, arg_count = operand

            if func_name.startswith("__") and func_name.endswith("__"):
                self._generate_builtin_call(func_name, arg_count)
            elif func_name in self.func_map:
                # Collect arguments
                args = []
                for _ in range(arg_count):
                    args.insert(0, self._pop())

                result = self.builder.call(self.func_map[func_name], args)
                self._push(result)
            else:
                # Unknown function - push 0
                self._push(ir.Constant(self.i64, 0))

        elif op == OpCode.RETURN:
            if func.name == "main":
                self.builder.ret(ir.Constant(self.i32, 0))
            else:
                self.builder.ret(ir.Constant(self.i64, 0))

        elif op == OpCode.RETURN_VALUE:
            val = self._pop()
            if func.name == "main":
                result = self.builder.trunc(val, self.i32)
                self.builder.ret(result)
            else:
                self.builder.ret(val)

        elif op == OpCode.PRINT:
            val = self._pop()
            # Print as integer
            fmt_str = self._get_string_ptr("%lld")
            self.builder.call(self.printf, [fmt_str, val])

        elif op == OpCode.PRINT_NEWLINE:
            fmt_str = self._get_string_ptr("\n")
            self.builder.call(self.printf, [fmt_str])

        elif op == OpCode.INPUT_INT:
            # Allocate buffer and read
            buf = self.builder.alloca(ir.ArrayType(self.i8, 256))
            buf_ptr = self.builder.bitcast(buf, self.i8_ptr)
            stdin_val = self.builder.load(self.stdin_ptr)
            self.builder.call(self.fgets, [buf_ptr, ir.Constant(self.i32, 256), stdin_val])
            result = self.builder.call(self.atoll, [buf_ptr])
            self._push(result)

        elif op == OpCode.INPUT_STRING:
            buf = self.builder.alloca(ir.ArrayType(self.i8, 256))
            buf_ptr = self.builder.bitcast(buf, self.i8_ptr)
            stdin_val = self.builder.load(self.stdin_ptr)
            self.builder.call(self.fgets, [buf_ptr, ir.Constant(self.i32, 256), stdin_val])
            int_val = self.builder.ptrtoint(buf_ptr, self.i64)
            self._push(int_val)

        elif op == OpCode.SQRT:
            val = self._pop()
            float_val = self.builder.sitofp(val, self.double)
            result = self.builder.call(self.sqrt, [float_val])
            int_result = self.builder.fptosi(result, self.i64)
            self._push(int_result)

        elif op == OpCode.ABS:
            val = self._pop()
            zero = ir.Constant(self.i64, 0)
            is_neg = self.builder.icmp_signed('<', val, zero)
            neg_val = self.builder.neg(val)
            result = self.builder.select(is_neg, neg_val, val)
            self._push(result)

        elif op == OpCode.POW:
            b = self._pop()
            a = self._pop()
            fa = self.builder.sitofp(a, self.double)
            fb = self.builder.sitofp(b, self.double)
            result = self.builder.call(self.pow, [fa, fb])
            int_result = self.builder.fptosi(result, self.i64)
            self._push(int_result)

        elif op == OpCode.RANDOM:
            max_val = self._pop()
            min_val = self._pop()
            # Initialize random
            null_ptr = ir.Constant(self.i8_ptr, None)
            time_val = self.builder.call(self.time, [null_ptr])
            time_i32 = self.builder.trunc(time_val, self.i32)
            self.builder.call(self.srand, [time_i32])
            # Get random value
            rand_val = self.builder.call(self.rand, [])
            rand_i64 = self.builder.sext(rand_val, self.i64)
            range_val = self.builder.sub(max_val, min_val)
            range_val = self.builder.add(range_val, ir.Constant(self.i64, 1))
            mod_val = self.builder.srem(rand_i64, range_val)
            result = self.builder.add(min_val, mod_val)
            self._push(result)

        elif op == OpCode.CREATE_ARRAY:
            size = self._pop()
            # Allocate array memory
            elem_size = ir.Constant(self.i64, 8)  # sizeof(i64)
            total_size = self.builder.mul(size, elem_size)
            ptr = self.builder.call(self.malloc, [total_size])
            int_ptr = self.builder.ptrtoint(ptr, self.i64)
            self._push(int_ptr)

        elif op == OpCode.ARRAY_LITERAL:
            count = operand
            # Allocate and populate
            elem_size = ir.Constant(self.i64, 8)
            total_size = ir.Constant(self.i64, count * 8)
            ptr = self.builder.call(self.malloc, [total_size])
            arr_ptr = self.builder.bitcast(ptr, ir.PointerType(self.i64))

            # Pop elements and store (in reverse)
            for i in range(count - 1, -1, -1):
                val = self._pop()
                idx = ir.Constant(self.i32, i)
                elem_ptr = self.builder.gep(arr_ptr, [idx])
                self.builder.store(val, elem_ptr)

            int_ptr = self.builder.ptrtoint(ptr, self.i64)
            self._push(int_ptr)

        elif op == OpCode.ARRAY_GET:
            idx = self._pop()
            arr_ptr_int = self._pop()
            arr_ptr = self.builder.inttoptr(arr_ptr_int, ir.PointerType(self.i64))
            idx_i32 = self.builder.trunc(idx, self.i32)
            elem_ptr = self.builder.gep(arr_ptr, [idx_i32])
            val = self.builder.load(elem_ptr)
            self._push(val)

        elif op == OpCode.ARRAY_SET:
            val = self._pop()
            idx = self._pop()
            arr_ptr_int = self._pop()
            arr_ptr = self.builder.inttoptr(arr_ptr_int, ir.PointerType(self.i64))
            idx_i32 = self.builder.trunc(idx, self.i32)
            elem_ptr = self.builder.gep(arr_ptr, [idx_i32])
            self.builder.store(val, elem_ptr)

        elif op == OpCode.ARRAY_LENGTH:
            # For simplicity, length is stored before array data
            # This is a stub - real implementation would need proper array struct
            self._pop()
            self._push(ir.Constant(self.i64, 0))

        elif op == OpCode.HALT:
            if func.name == "main":
                self.builder.ret(ir.Constant(self.i32, 0))
            else:
                self.builder.ret(ir.Constant(self.i64, 0))

        elif op == OpCode.NOP:
            pass

        # Other opcodes can be added as needed

    def _generate_builtin_call(self, name: str, arg_count: int):
        """Generate code for built-in function calls."""
        if name == "__strstr__":
            b = self._pop()
            a = self._pop()
            a_ptr = self.builder.inttoptr(a, self.i8_ptr)
            b_ptr = self.builder.inttoptr(b, self.i8_ptr)
            result = self.builder.call(self.strstr, [a_ptr, b_ptr])
            null = ir.Constant(self.i8_ptr, None)
            is_found = self.builder.icmp_signed('!=', result, null)
            int_result = self.builder.zext(is_found, self.i64)
            self._push(int_result)
        else:
            # Pop arguments and push null for unknown builtins
            for _ in range(arg_count):
                self._pop()
            self._push(ir.Constant(self.i64, 0))


def compile_to_llvm(program: CompiledProgram) -> ir.Module:
    """Compile a program to LLVM IR."""
    gen = LLVMCodeGenerator()
    return gen.generate(program)


def compile_to_object(program: CompiledProgram, output_file: str, opt_level: int = 2):
    """Compile a program to an object file."""
    init_llvm()
    module = compile_to_llvm(program)

    # Verify the module
    llvm_ir = str(module)
    mod = binding.parse_assembly(llvm_ir)
    mod.verify()

    # Create target machine
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(opt=opt_level)

    # Compile to object code
    obj_code = target_machine.emit_object(mod)

    with open(output_file, 'wb') as f:
        f.write(obj_code)


def compile_to_executable(program: CompiledProgram, output_file: str, opt_level: int = 2):
    """Compile a program to a native executable."""
    import subprocess
    import tempfile
    import os

    init_llvm()
    module = compile_to_llvm(program)

    # Verify the module
    llvm_ir = str(module)
    mod = binding.parse_assembly(llvm_ir)
    mod.verify()

    # Create target machine
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(opt=opt_level)

    # Compile to object code
    obj_code = target_machine.emit_object(mod)

    # Write to temp file and link
    with tempfile.NamedTemporaryFile(suffix='.o', delete=False) as obj_file:
        obj_file.write(obj_code)
        obj_path = obj_file.name

    try:
        # Link with system linker (gcc/clang)
        linker = 'gcc'
        # Try clang first
        try:
            subprocess.run(['clang', '--version'], capture_output=True, check=True)
            linker = 'clang'
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        subprocess.run([linker, obj_path, '-o', output_file, '-lm'], check=True)
    finally:
        os.unlink(obj_path)


def get_llvm_ir(program: CompiledProgram) -> str:
    """Get LLVM IR as a string."""
    module = compile_to_llvm(program)
    return str(module)
