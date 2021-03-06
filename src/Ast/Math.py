from llvmlite import ir

from collections import deque

from . import Types
from .Nodes import *

def shunt(node: AST_NODE, op_stack = None, output_queue = None, has_parent=False):
    '''shunt Expressions to rearrange them based on the Order of Operations'''

    # * create stack and queue
    if op_stack == None:
        op_stack = deque()
    if output_queue==None:
        output_queue = []
    

    # * shunt thru the AST
    input_list = [node.children[0], node, node.children[1]] # node: R,M,L
    for item in input_list:
        if not item.is_operator:
            output_queue.append(item)
        if item.is_operator:
            if item != node:
                shunt(item, op_stack, output_queue, True)
            if item == node:
                while len(op_stack) > 0:
                    x = op_stack.pop()
                    if x[1] > item.operator_precendence:
                        output_queue.append(x[0])
                    else:
                        op_stack.append(x)
                        break
                op_stack.append([item.op_type,item.operator_precendence])
    
    # * push remaining operators to Queue
    while (not has_parent) and len(op_stack)>0:
        output_queue.append(op_stack.pop()[0])

    # * Create new Expression AST from output Queue
    while (not has_parent) and len(output_queue) > 1:
        stack = deque()
        for c,x in enumerate(output_queue):
            if isinstance(x, str):
                r,l = stack.pop(), stack.pop()
                if x == "sum":
                    p = Sum((-1,-1), '',  [l[0],r[0]], True)
                elif x == "sub":
                    p = Sub((-1,-1), '',  [l[0],r[0]], True)
                elif x == "mul":
                    p = Mul((-1,-1), '',  [l[0],r[0]], True)
                elif x == "div":
                    p = Div((-1,-1), '',  [l[0],r[0]], True)
                output_queue.pop(c)
                output_queue.pop(r[1])
                output_queue.pop(l[1])
                output_queue.insert(c-2, p)
                break
            else:
                stack.append([x,c])
    

    if (not has_parent):return output_queue[0]

class Sum(AST_NODE):
    '''Basic sum operation. It acts as an `expr`'''
    __slots__ = ["ir_type", "operator_precendence", "op_type", "shunted"]

    def init(self, shunted = False):
        self.ret_type = Types.type_conversion(self.children[0], self.children[1])
        self.shunted = shunted

        self.ir_type = Types.types[self.ret_type].ir_type
        self.is_operator = True
        self.op_type = "sum"
        self.operator_precendence = 1

    def eval_math(self, func):
        # * do conversions on args
        lhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[0].eval(func))
        rhs = Types.types[self.ret_type].convert_from(self.children[1].ret_type, self.children[1].eval(func))

        # * do correct add function
        match self.ret_type:
            case 'i32':
                return func.builder.add(lhs, rhs)
            case 'f64':
                return func.builder.fadd(lhs, rhs)
    
    def eval(self, func):
        if not self.shunted:
            return shunt(self).eval_math(func)
        else:
            return self.eval_math(func)

class Sub(AST_NODE):
    '''Basic sub operation. It acts as an `expr`'''
    __slots__ = ["ir_type", "operator_precendence", "op_type", "shunted"]
    
    def init(self, shunted = False):
        self.ret_type = Types.type_conversion(self.children[0], self.children[1])
        self.shunted = shunted

        self.ir_type = Types.types[self.ret_type].ir_type
        self.is_operator = True
        self.op_type = "sub"
        self.operator_precendence = 1

    def eval_math(self, func):
        # * do conversions on args
        lhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[0].eval(func))
        rhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[1].eval(func))

        # * do correct add function
        match self.ret_type:
            case 'i32':
                return func.builder.sub(lhs, rhs)
            case 'f64':
                return func.builder.fsub(lhs, rhs)
    
    def eval(self, func):
        if not self.shunted:
            return shunt(self).eval(func)
        else:
            return self.eval_math(func)


class Mul(AST_NODE):
    '''Basic sub operation. It acts as an `expr`'''
    __slots__ = ["ir_type", "operator_precendence", "op_type", "shunted"]
    
    def init(self, shunted = False):
        self.ret_type = Types.type_conversion(self.children[0], self.children[1])

        self.shunted = shunted
        self.ir_type = Types.types[self.ret_type].ir_type
        self.is_operator = True
        self.op_type = "mul"
        self.operator_precendence = 2

    def eval_math(self, func):
        # * do conversions on args
        lhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[0].eval(func))
        rhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[1].eval(func))

        # * do correct add function
        match self.ret_type:
            case 'i32':
                return func.builder.mul(lhs, rhs)
            case 'f64':
                return func.builder.fmul(lhs, rhs)

    def eval(self, func):
        if not self.shunted:
            return shunt(self).eval(func)
        else:
            return self.eval_math(func)

class Div(AST_NODE):
    '''Basic sub operation. It acts as an `expr`'''
    __slots__ = ["ir_type", "operator_precendence", "op_type", "shunted"]
    
    def init(self, shunted = False):
        self.ret_type = Types.type_conversion(self.children[0], self.children[1])

        self.shunted = shunted
        self.ir_type = Types.types[self.ret_type].ir_type
        self.is_operator = True
        self.op_type = "div"
        self.operator_precendence = 2

    def eval_math(self, func):
        # * do conversions on args
        lhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[0].eval(func))
        rhs = Types.types[self.ret_type].convert_from(self.children[0].ret_type, self.children[1].eval(func))

        # * do correct add function
        match self.ret_type:
            case 'i32':
                return func.builder.sdiv(lhs, rhs)
            case 'f64':
                return func.builder.fdiv(lhs, rhs)

    def eval(self, func):
        if not self.shunted:
            return shunt(self).eval(func)
        else:
            return self.eval_math(func)
