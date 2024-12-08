from lib.utils import AST
from lib.parse import parse
from lib.compute import compute
from lvm_repl import make_church_number
import re
expr_ast = parse("(λA|(λB|(λC|(λD|(λE|(λF|(λG|(λH|(λI|(λJ|(λK|(λL|((((λw|((w(λ" + \
                 "x|(λy|y)))(λx|(λy|x))))(((λa|(λb|(((λw|(λz|((wz)(λx|(λy|y)))" + \
                 "))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|" + \
                 "(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|" + \
                 "z))(λu|u))))))x)))a)b)))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|" + \
                 "y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x" + \
                 "(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))b)a)))))((λb|(((λx|(" + \
                 "λy|((y(λx|(λy|(λz|(y((xy)z))))))x)))(((λx|(λy|(λs|(x(ys)))))" + \
                 "b)(λs|(λz|(sz)))))(λs|(λz|(s(s(sz)))))))(λs|(λz|(s(s(s(s(sz)" + \
                 "))))))))K))(λx|(λy|y)))((((λw|((w(λx|(λy|y)))(λx|(λy|x))))((" + \
                 "(λa|(λb|(((λw|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λ" + \
                 "w|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx" + \
                 "|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))(" + \
                 "(λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy" + \
                 "|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))" + \
                 "(λu|u))))))x)))b)a)))))((λb|(((λx|(λy|((y(λx|(λy|(λz|(y((xy)" + \
                 "z))))))x)))(((λx|(λy|(λs|(x(ys)))))b)(λs|(λz|(sz)))))(λs|(λz" + \
                 "|(s(s(s(sz))))))))(λs|(λz|(s(s(s(s(s(s(s(s(sz)))))))))))))C)" + \
                 ")(λx|(λy|y)))((((λw|((w(λx|(λy|y)))(λx|(λy|x))))(((λa|(λb|((" + \
                 "(λw|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(" + \
                 "λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(" + \
                 "((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((x(λ" + \
                 "x|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λ" + \
                 "x|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u)))))" + \
                 ")x)))b)a)))))((λb|(λs|(λz|(s(s(s(s(s(s(sz))))))))))(λs|(λz|(" + \
                 "s(s(s(s(s(s(s(s(sz)))))))))))))J))(λx|(λy|y)))(((((λa|(λb|((" + \
                 "(λw|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(" + \
                 "λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(" + \
                 "((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((x(λ" + \
                 "x|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λ" + \
                 "x|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u)))))" + \
                 ")x)))b)a)))))((λb|(((λx|(λy|((y(λx|(λy|(λz|(y((xy)z))))))x))" + \
                 ")(λs|(λz|(s(s(sz))))))(((λx|(λy|(λs|(x(ys)))))b)(λs|(λz|(sz)" + \
                 ")))))(λs|(λz|(s(s(s(s(s(sz))))))))))I)(((((λa|(λb|(((λw|(λz|" + \
                 "((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(" + \
                 "λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(" + \
                 "λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((x(λx|(λy|y)" + \
                 "))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((" + \
                 "y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))b)a" + \
                 ")))))((λb|(((λx|(λy|((y(λx|(λy|(λz|(y((xy)z))))))x)))(((λx|(" + \
                 "λy|(λs|(x(ys)))))b)(((λx|(λy|((y(λx|(λy|(λz|(y((xy)z))))))x)" + \
                 "))(λs|(λz|(sz))))(((λx|(λy|(λs|(x(ys)))))b)(λs|(λz|(sz))))))" + \
                 ")(λs|(λz|(s(sz))))))(λs|(λz|(s(s(sz)))))))H)(((((λa|(λb|(((λ" + \
                 "w|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy" + \
                 "|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((" + \
                 "x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((x(λx|" + \
                 "(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|" + \
                 "(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x" + \
                 ")))b)a)))))((λb|(λs|(λz|(s(s(s(sz)))))))(λs|(λz|(s(s(s(s(s(s" + \
                 "(sz)))))))))))E)((((λw|((w(λx|(λy|y)))(λx|(λy|x))))(((λa|(λb" + \
                 "|(((λw|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λ" + \
                 "x|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λ" + \
                 "z|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((" + \
                 "x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(" + \
                 "((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))" + \
                 "))))x)))b)a)))))((λb|(λs|(λz|(sz))))(λs|(λz|(s(s(s(sz)))))))" + \
                 ")B))(λx|(λy|y)))(((((λa|(λb|(((λw|(λz|((wz)(λx|(λy|y)))))((λ" + \
                 "x|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y" + \
                 "))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λ" + \
                 "u|u))))))x)))a)b)))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(" + \
                 "λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(" + \
                 "λh|(h(gs)))))(λu|z))(λu|u))))))x)))b)a)))))((λb|(((λx|(λy|((" + \
                 "y(λx|(λy|(λz|(y((xy)z))))))x)))(((λx|(λy|(λs|(x(ys)))))b)(λs" + \
                 "|(λz|(s(s(sz)))))))(λs|(λz|(s(sz))))))(λs|(λz|(s(s(s(s(s(sz)" + \
                 ")))))))))L)((((λw|((w(λx|(λy|y)))(λx|(λy|x))))(((λa|(λb|(((λ" + \
                 "w|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy" + \
                 "|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((" + \
                 "x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((x(λx|" + \
                 "(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|" + \
                 "(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x" + \
                 ")))b)a)))))((λb|(((λx|(λy|((y(λx|(λy|(λz|(y((xy)z))))))x)))(" + \
                 "((λx|(λy|(λs|(x(ys)))))b)(λs|(λz|(s(sz))))))(λs|(λz|z))))(λs" + \
                 "|(λz|(s(s(s(s(s(sz))))))))))A))(λx|(λy|y)))(((((λa|(λb|(((λw" + \
                 "|(λz|((wz)(λx|(λy|y)))))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|" + \
                 "y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x" + \
                 "(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))a)b)))((λx|(((x(λx|(" + \
                 "λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y))))(((λx|(" + \
                 "λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λu|u))))))x)" + \
                 "))b)a)))))((λb|(λs|(λz|(s(sz)))))(λs|(λz|(s(s(s(s(s(s(s(s(s(" + \
                 "sz))))))))))))))D)(((((λa|(λb|(((λw|(λz|((wz)(λx|(λy|y)))))(" + \
                 "(λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy" + \
                 "|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))" + \
                 "(λu|u))))))x)))a)b)))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y))" + \
                 ")(λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg" + \
                 "|(λh|(h(gs)))))(λu|z))(λu|u))))))x)))b)a)))))((λb|(((λx|(λy|" + \
                 "((y(λx|(λy|(λz|(y((xy)z))))))x)))(((λx|(λy|(λs|(x(ys)))))b)(" + \
                 "λs|(λz|(sz)))))(λs|(λz|(sz)))))(λs|(λz|(s(s(s(s(s(s(s(s(s(sz" + \
                 "))))))))))))))G)(((((λa|(λb|(((λw|(λz|((wz)(λx|(λy|y)))))((λ" + \
                 "x|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(λx|(λy|x)))))(λx|(λy|y" + \
                 "))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(λh|(h(gs)))))(λu|z))(λ" + \
                 "u|u))))))x)))a)b)))((λx|(((x(λx|(λy|y)))(λw|((w(λx|(λy|y)))(" + \
                 "λx|(λy|x)))))(λx|(λy|y))))(((λx|(λy|((y(λx|(λs|(λz|(((x(λg|(" + \
                 "λh|(h(gs)))))(λu|z))(λu|u))))))x)))b)a)))))((λb|(λs|(λz|(sz)" + \
                 ")))(λs|(λz|(s(s(s(sz))))))))F)(λx|(λy|x)))(λx|(λy|y))))(λx|(" + \
                 "λy|y))))(λx|(λy|y)))))(λx|(λy|y)))))(λx|(λy|y))))(λx|(λy|y))" + \
                 "))(λx|(λy|y))))))))))))))))))") # the task lambda expr

# if you use stdin for input expr ast
# expr_ast = parse(input())

syms = []
def search(ast : AST) -> None:
    if ast.terminate_p() and re.match("[A-Z]", ast.root):
        syms.append(ast.root)
    elif ast.application_p():
        search(ast.fn_expr())
        search(ast.arg_expr())
    elif ast.function_p():
        search(ast.fn_body())
search(expr_ast)
print(f"sym sequence: {''.join(syms)}")

def reorder_fn_ast(order : list) -> AST:
    """
    (λFabcdefg|Fgfedcba) #F -> reorder the argument
    """
    in_order = [AST(chr(i + ord("A"))) for i in range(len(order))]
    ast = AST("f")
    for sym in in_order:
        ast = AST("←", ast, sym)
    for sym in reversed(order):
        ast = AST("λ", AST(sym), ast)
    return AST("λ", AST("f"), ast)
reorder_ast = reorder_fn_ast(syms)
print("reordered:", reorder_ast.prettify())

flag = [char for char in "************"]
ast = AST("←", reorder_ast, expr_ast)
for j in syms:
    max_len, max_i, max_res = 0, 0, None
    for i in range(26):
        res = compute(AST("←", ast, make_church_number(i + 1)), 512)
        if len(str(res)) > max_len:
            max_len, max_i, max_res = len(str(res)), i, res
        elif len(str(res)) == max_len and max_len != 0:
            res = compute(AST("←", AST("←", res, AST("t")), AST("f")), 512)
            if res.terminate_p() and res.root == "t":
                max_i = i
                break
    ast, flag[ord(j) - ord("A")] = max_res, chr(max_i + ord("a"))
    print(f"flag: {"".join(flag)}")

print(''.join(flag))
