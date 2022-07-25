import sys, os

def make_project(args):
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

if __name__ == "__main__":
    args = sys.argv
    if args[0]=="src/Main.py": args=args[1::]

    if len(args)==0:
        print("Valid sub-commands: build, run, make, publish")

    elif args[0] == "make": make_project(args)

    else:
        example = '''
define main {
    x=9+2;
    x=x+2;
}
'''
        from Lexer import Lexer
        import Parser
        import Codegen
        lexer = Lexer().get_lexer()
        tokens = lexer.lex(example)
        codegen = Codegen.CodeGen()

        module = codegen.module
        # builder = codegen.builder
        printf = codegen.printf
        output = []
        for x in tokens:
            output.append({"name":x.name,"value":x.value,"source_pos":x.source_pos})
        pg = Parser.parser(output, module, printf)
        # x = pg.parse()
        parsed = pg.parse()
        print(parsed)
        for x in parsed:
            x["value"].eval(module)
        print(module, type(module))
