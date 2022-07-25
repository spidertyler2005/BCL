from llvmlite import ir

from .Nodes import AST_NODE, Block

class FunctionDef(AST_NODE):
    def init(self, name: str, block: Block):
        self.name = name
        self.type = "Function"

        self.builder = None
        self.block = block
    
    def eval(self, module):
        fnty = ir.FunctionType(ir.VoidType(), [], False)

        self.function_ir = ir.Function(module, fnty, name=self.name)
        block = self.function_ir.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)

        for instr in self.block.children:
            instr.eval(self)