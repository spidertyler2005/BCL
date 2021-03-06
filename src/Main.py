import os
import sys
from typing import List
from Ast import Function

def make_project(args: List[str]):
    '''setup project files'''
    if not os.path.isdir(args[1]): os.mkdir(args[1])
    os.mkdir(f"{args[1]}/src")
    os.mkdir(f"{args[1]}/lib")
    with open(f"{args[1]}/project.toml",'w+') as f:
        f.write(f'''[info]
name = "{args[1].split("/")[-1]}"
author = "{os.getlogin()}"
version = "1.0"

[compile]

GC = true
include = [] # include paths, ex: {args[1].split("/")[-1]}/resources/
''')
    with open(f"{args[1]}/src/Main.bcl",'w+') as f:
        f.write('''define main() {
    println("Hello World!");
}
''')
    with open(f"{args[1]}/.gitignore",'w+') as f:
        f.write('''# BCL ignored files
lib/

# other files
''')


def compile(source_code: str, output_loc: str):
    '''compile source code'''
    import Codegen
    import Parser
    from Lexer import Lexer
    import Ast.Standard_Functions
    lexer = Lexer().get_lexer()
    tokens = lexer.lex(example)
    codegen = Codegen.CodeGen()

    module = codegen.module
    Ast.Standard_Functions.declare_printf(module)
    # printf = codegen.printf
    output = []
    for x in tokens:
        output.append({"name":x.name,"value":x.value,"source_pos":[x.source_pos.lineno, x.source_pos.colno]})
    pg = Parser.parser(output, module)
    parsed = pg.parse()

    Function.process_func_call()
    for x in parsed:
        x["value"].eval()

    print(module, type(module))
    codegen.save_ir(output_loc)



if __name__ == "__main__":
    args = sys.argv
    if args[0]=="src/Main.py": args=args[1::]

    if len(args)==0:
        print("Valid sub-commands: build, run, make, publish")

    elif args[0] == "make": 
        make_project(args)

    else:
        example = '''
define main {
    x=9+2-3;
    y = 8;
    x=x+y/12-6*2;
    (89+(2-3))*2;
    test();
    print_int x;
    print_int y;
}

define test {
    x=3+4;
}
'''
        compile(example, "test.ll")
