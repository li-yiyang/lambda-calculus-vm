import re
import sys
from lib.compute import compute, normal
from lib.parse   import parse, make_church_number
from lib.utils   import AST, SyntaxError, UnknownToken

sys.setrecursionlimit(4096)

simplify_depth = -1
prettify = True
silent_p = False
normal_p = True
ans      = AST("λ", AST("x"), AST("x"))

class REPLUnknownCommands(Exception):
    def __init__(self, command : str) -> None:
        super().__init__(f"Unknown REPL command {command}")
        self.add_note("  Try command `.h' for help")

class REPLUnknownMacro(Exception):
    def __init__(self, macro : str) -> None:
        super().__init__(f"Unknown REPL macro `#{macro}'")
        self.add_note(f"Try define macro usng `.l({macro}) <expr>'. ")
        self.add_note("Or use built in macro for number `#<num>'. ")
        self.add_note("List all the macros via `.L'. ")

def print_manual(n : str | int = 0) -> None:
    """
    Print out manual.
    """
    print(open(f"./manual/{n}").read())

def print_task(n : str | int = 0) -> None:
    """
    Print out task.
    """
    print(open(f"./task/{n}").read())

def print_greeting_message() -> None:
    print("E HELLO LAMBDA CALCULUS VISUTAL MACHINE HELLO LAMBDA C",
          "N        L    V   V    M    M                        A",
          "I       L     V  V    M M  MM                        L",
          "H      L      V V    M  M M  M                       C",
          "C     LLLLLL   V    M   M    M          author: ryo  U",
          "AM LATUSIV SULUCLAC  ADBMAL OLLEH ENIHCAM LATUSIV SUL#",
          "",
          sep="\n")

def print_help() -> None:
    print("Usage: ",
          "  Commands:",
          "   * .m(n) -> print out LVM manual",
          "   * .t(n) -> print out UCATFLAGS task",
          "   * .f(x) <expr> -> test if x is free in <expr>",
          "   * .F(x) <expr> -> test if x is free for <expr> result",
          "   * .b(x) <expr> -> test if x is bounded in <expr>",
          "   * .B(x) <expr> -> test if x is bounded for <expr> result",
          "   * .l(s) <expr> -> set macro symbol with expr for replacement",
          "   * .L -> list all the macros and their bindings",
          "   * .a <expr> -> use application order to compute <expr>",
          f"   * .A -> toggle normal and application order reduction ({'NORMAL' if normal_p else 'APPLICATION'} ORDER)",
          # "   * .x <file-name> -> load macro definition file",
          f"   * .d(n) -> set max simplify iter depth (={ '∞' if simplify_depth == -1 else simplify_depth })",
          "   * .D <expr> -> compute only one step on <expr>",
          "   * .h -> print help message",
          "   * .? -> print quick help message",
          f"   * .p -> toggle prettify print ({'ON' if prettify else 'OFF'})",
          "   * .q -> quit LVM REPL",
          f"   * .s -> toggle REPL prompt ({'SILENT' if silent_p else 'ECHO'})",
          "",
          "  Lambda Calculus Expression:",
          "   * x -> symbol",
          "   * (f x) -> application",
          "   * (λ x | <expr>) -> lambda calculus (function)",
          "   * [<expr1> <expr2> ...] -> list",
          "   * \"[a-zA-Z]\" -> string (only alphabetic)",
          "",
          "  LVM REPL Macros:",
          "   * use `.l(s)' to define macros",
          "   * use `#s' to recall the macros",
          "   * use `#<num>' for church number macros",
          f"   * use `#*' for previous result ({ans.prettify() if prettify else str(ans)})",
          "   * Note that macros is replaced literally",
          "     during expression reading (not safe macro)",
          "",
          "  LVM REPL Comments: ",
          "   * anything after `->' will be ignored",
          "",
          "  More Tips: ",
          "   due to the limit of long line input, if you find",
          "   yourself unable to input long line to LVM REPL",
          "   you can try using pip or split the long line using",
          "   `\\' mark at the end of input line. ",
          "",
          sep="\n")

def print_quick_help() -> None:
    print("Usage: ",
          "  Input lambda calculus expression or .<command>. ",
          "        see more help infomation with .h command. ",
          sep="\n")

LVM_REPL_MACRO_TABLE = {}
LVM_REPL_MACRO_REGEXP = re.compile("#(0|[1-9][0-9]*|[^\\s#]|\\*)")
LVM_REPL_NUMBER_REGEXP = re.compile("0|[1-9][0-9]*")

def print_macro_table():
    print("LVM REPL Macro Table:")
    for key, val in LVM_REPL_MACRO_TABLE.items():
        print(f"  * {key} {val.prettify() if prettify else str(val)}")
    print("Note: ",
          "  * macros for real number: `#<num>'",
          "      for example: `#1', `#2', and so on",
          sep="\n")

def register_macro(symbol : str, expr : AST):
    if LVM_REPL_MACRO_TABLE[symbol]:
        print(f"Warning: `{symbol}' already defined as macro",
              "  replacing old definition:",
              f"     {LVM_REPL_MACRO_TABLE[symbol]}",
              sep="\n")
    LVM_REPL_MACRO_TABLE[symbol] = expr

def get_whole_input(prompt : str = ">>> ", wait_prompt : str = "... ") -> str:
    def try_read(prompt):
        try:
            if silent_p:
                return input()
            else:
                return input(prompt)
        except EOFError:
            exit()
    part = re.split("->", try_read(prompt))[0].strip()

    if len(part) != 0 and part[-1] == "\\":
        read = part[:-1]
    else:
        read = part

    while len(read) == 0 or part[-1] == "\\":
        part = re.split("->", try_read(wait_prompt))[0].strip()
        if len(part) != 0 and part[-1] == "\\":
            read += part[:-1]
        else:
            read += part
            part = " "

    return read.strip()

def read_input(prompt : str = ">>> ") -> str:
    global ans

    try:
        read = get_whole_input(prompt)
    except KeyboardInterrupt:
        print("Breaking... ")
        read = read_input(prompt)

    match = LVM_REPL_MACRO_REGEXP.search(read)
    while match:
        start, end = match.span()
        macro, ast = read[start + 1:end], None
        if LVM_REPL_MACRO_TABLE.get(macro):
            ast = LVM_REPL_MACRO_TABLE.get(macro)
        elif macro == "*":
            ast = ans
        elif LVM_REPL_NUMBER_REGEXP.match(macro):
            number = int(macro)
            ast = make_church_number(number)
        else:
            raise REPLUnknownMacro(macro)
        read = read[:start] + str(ast) + read[end:]
        match = LVM_REPL_MACRO_REGEXP.search(read)
    return read

def simplify(ast : AST, depth : int) -> AST:
    global ans
    res = ans
    try:
        if normal_p:
            res = normal(ast, depth)
        else:
            res = compute(ast, depth)
        ans = res
    except KeyboardInterrupt:
        ans = AST("λ", AST("x"), AST("λ", AST("y"), AST("y")))
    return ans

# Note: this is not a good code, it is growing urglier
# during the addition of LVM REPL functionalities.
# Please don't learn the code here.
if __name__ == "__main__":
    print_greeting_message()
    read = ".?"
    while read != ".q":
        cmd, arg = None, None

        try:
            # pre-processing the readed command:
            #   * read and apply macro
            #   * parse commands and apply commands
            if read[0] == ".":
                if read[1] == "f" or read[1] == "b" or \
                   read[1] == "F" or read[1] == "B" or \
                   read[1] == "l":
                    cmd, arg, read = read[1], read[3], read[5:]
                elif read[1] == "p":
                    prettify = not prettify
                    print(f"Prettify printing now {'ON' if prettify else 'OFF'}")
                    read = read_input()
                    continue
                elif read[1] == "m":
                    try:
                        part = read[3]
                        print_manual(part)
                    except:
                        print(f"Unknown manual command {read}",
                              "  assuming using `.m(0)': ",
                              sep="\n")
                        print_manual(0)

                    read = read_input()
                    continue
                elif read[1] == "t":
                    try:
                        part = read[3]
                        print_task(part)
                    except:
                        print(f"Unknown task command {read}",
                              "  assuming using `.t(0)': ",
                              sep="\n")
                        print_task(0)

                    read = read_input()
                    continue
                elif read[1] == "d":
                    try:
                        depth, i = "", 3
                        while read[i] != ")":
                            depth = depth + read[i]
                            i += 1
                        if depth == "*":
                            simplify_depth = -1
                        else:
                            simplify_depth = int(depth)
                        print(f"Simplify depth set to be {'∞' if simplify_depth == -1 else simplify_depth}")
                    except:
                        print("Unknown simplify depth command calling",
                              "  assuming using `.d(1)': ",
                              sep="\n")
                        simplify_depth = 1

                    read = read_input()
                    continue
                elif read[1] == "D":
                    ast = simplify(parse(read[2:]), 1)
                    print(ast.prettify() if prettify else str(ast))
                    read = read_input()
                    continue
                elif read[1] == "h":
                    print_help()
                    read = read_input()
                    continue
                elif read[1] == "L":
                    print_macro_table()
                    read = read_input()
                    continue
                elif read[1] == "?":
                    print_quick_help()
                    read = read_input()
                    continue
                elif read[1] == "q":
                    exit()
                elif read[1] == "s":
                    silent_p = not silent_p
                    print(f"Now silent is {'ON' if silent_p else 'OFF'}")
                    read = read_input()
                    continue
                elif read[1] == "a":
                    normal_p, tmp = False, normal_p
                    if simplify_depth == -1:
                        print("Warning: Simplify depth is `∞'. ")
                        print("It may be too larget and could possiblely breaks")
                        print("poor Python's recursion limit. ")
                        c = input("Continue? [N/y]: ").strip()
                        if not (c == "y" or c == "Y"):
                            print("Breaks. ")
                            print("Try with smaller `.d(<simplify_depth>)' like `.d(512)'. ")
                            read = read_input()
                            continue
                    if simplify_depth == 0:
                        print("Warning: Simplify depth is `0', assuming it to be `10'. ")
                        print("If you are insisted to use `0', toggle to application ")
                        print("reduction order via `.A' command and set `.d(0)'. ")
                    if simplify_depth > 1024:
                        print(f"Warning: Simplify depth is `{simplify_depth}'. ")
                        print("It may be too larget and could possiblely breaks")
                        print("poor Python's recursion limit. ")
                        c = input("Continue? [N/y]: ").strip()
                        if not (c == "y" or c == "Y"):
                            print("Breaks. ")
                            print("Try with smaller `.d(<simplify_depth>)' like `.d(512)'. ")
                            read = read_input()
                            continue
                    ast = simplify(parse(read[2:]), simplify_depth)
                    print(ast.prettify() if prettify else str(ast))
                    normal_p = tmp
                    read = read_input()
                    continue
                elif read[1] == "A":
                    normal_p = not normal_p
                    print(f"Now using {'NORMAL' if normal_p else 'APPLICATION'} reduction method")
                    if not normal_p and (simplify_depth > 1024 or simplify_depth == -1):
                        print(f"Warning: Simplify depth is `{simplify_depth if simplify_depth > 0 else '∞'}'. ")
                        print("It may be too larget and could possiblely breaks")
                        print("poor Python's recursion limit. ")
                        print("Adviced to try with smaller `.d(<simplify_depth>)' like `.d(512)'. ")
                    read = read_input()
                    continue
                else:
                    raise REPLUnknownCommands(read)

            ast = parse(read)
            if cmd == "f":
                print(ast.free_p(arg))
            elif cmd == "F":
                ast = simplify(ast, simplify_depth)
                print(ast.free_p(arg))
            elif cmd == "b":
                print(ast.bounded_p(arg))
            elif cmd == "B":
                ast = simplify(ast, simplify_depth)
                print(simplify(ast, simplify_depth).bounded_p(arg))
            elif cmd == "l":
                if LVM_REPL_MACRO_TABLE.get(arg):
                    print(f"Warning: redefining macro `#{arg}'")
                    print("previous macro expression value -> `#*'. ")
                    ans = LVM_REPL_MACRO_TABLE.get(arg)
                if arg == "*" or LVM_REPL_NUMBER_REGEXP.match(arg):
                    print(f"Warning: `#{arg}' was locked. ")
                    print("Skipped... ")
                else:
                    LVM_REPL_MACRO_TABLE.update({ arg: ast })
            else:
                ast = simplify(ast, simplify_depth)
                print(ast.prettify() if prettify else str(ast))
            read = read_input()
        except (SyntaxError, UnknownToken,
                REPLUnknownMacro, REPLUnknownCommands) as err:
            print(err)
            print('\n'.join(err.__notes__))
            print("")
            read = ".?"
