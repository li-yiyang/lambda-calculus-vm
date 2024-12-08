from lib.utils import AST
from lib.parse import parse

def church_number_to_integer_bad_one(expr : str, sym : str = "y") -> int:
    count = 0
    for char in expr:   # for all the characters in `expr'
        if char == sym: # if has `sym' symbol appearance
            count += 1   # increase count for `sym'
    return count - 1    # remove `sym' count in identifier list

def church_number_to_integer(expr : str | AST) -> int:
    ast = parse(expr) if isinstance(expr, str) else expr
    if not ast.function_p() or not ast.fn_body().function_p():
        raise Exception(f"{ast} not simplified church number value")
    inc, zero = ast.identifier(), ast.fn_body().identifier()
    count = 0
    ast = ast.fn_body().fn_body()
    while True:
        if ast.terminate_p():
            if ast.root == zero:
                return count
            else:
                raise Exception(f"{ast} not {zero}")
        elif ast.application_p():
            if ast.fn_expr().terminate_p() and ast.fn_expr().root == inc:
                count += 1
                ast = ast.arg_expr()
            else:
                print(ast.fn_expr().terminate_p() and ast.fn_expr().root == inc)
                raise Exception(f"{ast} not {inc}")
        else:
            raise Exception(f"{ast} not ({inc}{zero}) like")

if __name__ == "__main__":
    print(church_number_to_integer(input("church number expr > ")))
