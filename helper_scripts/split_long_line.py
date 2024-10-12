from lib.utils import AST

def split_long_line(expr : AST | str,
                    width : int = 80,
                    pretty_p : bool = False) -> str:
    expr = expr if isinstance(expr, str) else \
        expr.prettify() if pretty_p else str(expr)
    line = ""
    while len(expr) > width:
        line = line + expr[:width] + "\\\n"
        expr = expr[width:]
    if len(expr) > 0:
        line = line + expr
    return line
