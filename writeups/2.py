from lib.utils import AST
from lib.parse import parse
from helper_scripts.split_long_line import split_long_line
from random import random, shuffle

TRUE_AST  = parse("(λxy|x)")
FALSE_AST = parse("(λxy|y)")
def if_ast(ast : AST, t : AST, f : AST) -> AST:
    return AST("←", AST("←", ast, t), f)

def make_church_number(number : int) -> AST:
    ast = AST("z")
    while number > 0:
        ast = AST("←", AST("s"), ast)
        number -= 1
    return AST("λ", AST("s"), AST("λ", AST("z"), ast))

ADD_AST = parse("(λxy|y(λxyz|y(xyz))x)")
MUL_AST = parse("(λxys|x(ys))")
def num_to_p_base(num : int, base : int = 10) -> list[int]:
    assert num > 0
    p_list = []
    while num > 0:
        p_list.append(num % base)
        num = num // base
    return list(reversed(p_list))

def obfuscate_int_ast(num : int, base_max : int = 10) -> AST:
    assert base_max > 1
    p_base, base = int(2 + random() * (base_max - 1)), AST("b")
    bits = [make_church_number(n) for n in num_to_p_base(num, p_base)]
    ast = bits[0]
    for n in bits[1:]:
        if random() < 0.5:
            ast = AST("←",
                      AST("←", ADD_AST, n),
                      AST("←", AST("←", MUL_AST, base), ast))
        else:
            ast = AST("←",
                      AST("←", ADD_AST, AST("←", AST("←", MUL_AST, base), ast)),
                      n)
    return AST("←", AST("λ", base, ast), make_church_number(p_base))

EQ_AST = parse("(λab|(λwz|wz(λxy|y))((λx|x(λxy|y)(λw|w(λxy|y)(λxy|x))(λxy|y))((λxy|y(λxsz|x(λgh|h(gs))(λu|z)(λu|u))x)ab))((λx|x(λxy|y)(λw|w(λxy|y)(λxy|x))(λxy|y))((λxy|y(λxsz|x(λgh|h(gs))(λu|z)(λu|u))x)ba)))")
NOT_AST = parse("(λw|w(λxy|y)(λxy|x))")
def eq_ast(a : AST, b : AST):
    return AST("←", AST("←", EQ_AST, a), b)
def neq_ast(a : AST, b : AST):
    return AST("←", NOT_AST, eq_ast(a, b))

def obfuscate_str_ast(flag : str) -> AST:
    assert len(flag) < 24
    syms = [AST(chr(i + ord("A"))) for i in range(len(flag))]
    encs = [ord(c) - ord("a") + 1 for c in flag]
    ptrs = [i for i in range(len(flag))]
    shuffle(ptrs)
    ast  = TRUE_AST
    for ptr in ptrs:
        if random() < 0.5:
            test = eq_ast(obfuscate_int_ast(encs[ptr]), syms[ptr])
            ast = if_ast(test, ast, FALSE_AST)
        else:
            test = neq_ast(obfuscate_int_ast(encs[ptr]), syms[ptr])
            ast = if_ast(test, FALSE_AST, ast)
    for sym in reversed(syms):
        ast = AST("λ", sym, ast)
    return ast

# The code is generated like below:
# note that the result may not be the same each time, but
# the flag is always same.
# print(split_long_line(obfuscate_str_ast("lambdaknight"), 60, False))

# use this code like:
#   cd lambda_machine # cd to root
#   python -m writeups.2 | python -m writeups.2-solve
print(obfuscate_str_ast("lambdaknight"))
