from llvmlite import ir
import Errors

class Number():
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self):
        i = ir.Constant(ir.IntType(32), int(self.value))
        return i

class String_utf8():
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self):
        i = ir.Constant(ir.ArrayType(ir.IntType(8), len(self.value)),
                            bytearray(self.value.encode("utf8")))
        return i


class BinaryOp():
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module = module
        self.left = left
        self.right = right


class Sum(BinaryOp):
    def eval(self):
        i = self.builder.add(self.left.eval(), self.right.eval())
        return i


class Sub(BinaryOp):
    def eval(self):
        i = self.builder.sub(self.left.eval(), self.right.eval())
        return i


class StandardFunction():
    def __init__(self, program, printf, value, lineno):
        self.builder = program.builder
        self.module = program.module
        self.printf = printf
        self.args = value
        self.program = program
        self.lineno = lineno

    def eval(self):
        if len(self.args)>self.argNum:
            Errors.Error.Invalid_Arguement_Count(self.lineno,len(self.args), self.argNum)

class Print(StandardFunction):
    def eval(self):
        self.argNum = 1
        super().eval()
        #print(self.value)
        value = self.args.eval()[0]

        # Declare argument list
        voidptr_ty = ir.IntType(8).as_pointer()
        
        fmt_arg = self.builder.bitcast(self.program.global_fmt_int, voidptr_ty)

        # Call Print Function
        self.builder.call(self.printf, [fmt_arg, value])

class Println(StandardFunction):
    def eval(self):
        self.argNum = 1
        super().eval()
        #print(self.value)
        value = self.args.eval()[0]

        # Declare argument list
        voidptr_ty = ir.IntType(8).as_pointer()
        
        fmt_arg = self.builder.bitcast(self.program.global_fmt_int_n, voidptr_ty)

        # Call Print Function
        self.builder.call(self.printf, [fmt_arg, value])

class Parenth():
    def __init__(self,*args):
        self.stuff = []
    
    def eval(self):
        output = []
        for x in self.stuff:
            output.append(x.eval())
        return output
    
    def __len__(self):
        return len(self.stuff)
    
    def append(self,thing):
        self.stuff.append(thing)


class Program:
    def __init__(self,builder,module):
        self.stuff = []
        self.builder = builder
        self.module = module
        self.value=""
        
        #printing integers using a bitcast requires a string constant.

        fmt = "%i \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        self.global_fmt_int_n = ir.GlobalVariable(self.module, c_fmt.type, name="fstr_int_n")
        self.global_fmt_int_n.linkage = 'internal'
        self.global_fmt_int_n.global_constant = True
        self.global_fmt_int_n.initializer = c_fmt

        fmt = "%i \0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        self.global_fmt_int = ir.GlobalVariable(self.module, c_fmt.type, name="fstr_int")
        self.global_fmt_int.linkage = 'internal'
        self.global_fmt_int.global_constant = True
        self.global_fmt_int.initializer = c_fmt
    
    def eval(self):
        output = []
        for x in self.stuff:
            output.append(x.eval())
        return output
    
    def append(self,thing):
        self.stuff.append(thing)