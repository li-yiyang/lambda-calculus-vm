from lib.utils import AST

# General Model of Computation
#
# for any lambda expression:
# 1. Find all possible application subexpressions in the expression;
# 2. Pick one where the function object is neither a simple identifier
#    nor an application expression, but a function expression of the
#    form `(λx|E)', where `E' is some arbitrary expression;
# 3. Assume that the expression to the right of this function is some
#    arbitray expression `A';
# 4. Now perform the **substitution**: identify all occurrences of the
#    identifier `x' in the expression `E' and replace them by the
#    expression `A';
# 5. Replace the entire application by the result of this subsititution
#    and loop back to step 1.
#
# ref: The Architecture of Symbolic Computers, Peter Kogge

# deprecated (use it if you are debugging with the lambda calculus)
def var_bounded_p(ast : AST, var : str) -> bool:
    """
    Test if `var' is bounded within `ast'.
    Return True if bounded, otherwise, False.

    Para:
    + `ast': AST of the expression
    + `var': variable name in string
    """
    if ast.terminate_p():
        return ast.root == var
    if ast.function_p():
        return (not ast.identifier() == var) and var_bounded_p(ast.fn_body(), var)
    if ast.application_p():
        return var_bounded_p(ast.fn_expr(), var) or var_bounded_p(ast.arg_expr(), var)
    raise f"Unknown AST type with AST root {ast.root}"

def subsitute_ast(ast : AST, var : str, val : AST | str) -> AST:
    """
    Subsitute `var' in `ast' with `val'.
    Note that `var' shall be free variable in `ast'.

    Para:
    + `ast': AST of the expression
    + `var': variable name in string
    + `val': AST or new symbol name to replace the `var' in `ast'
    """
    if isinstance(val, str):
        val = AST(val)

    if ast.terminate_p():
        return val if ast.root == var else ast
    if ast.application_p():
        return AST("←",
                   subsitute_ast(ast.fn_expr(),  var, val),
                   subsitute_ast(ast.arg_expr(), var, val))
    if ast.function_p():
        identifier = ast.identifier()
        if identifier == var:
            return ast
        elif identifier != var and not val.free_p(identifier):
            return AST("λ", AST(identifier), subsitute_ast(ast.fn_body(), var, val))
        else:
            new_var = val.gen_var()
            ast = subsitute_ast(ast.fn_body(), identifier, AST(new_var))
            ast = subsitute_ast(ast, var, val)
            return AST("λ", AST(new_var), ast)

    raise Exception(f"Unknown type ast with root {ast.root}")

def beta_conversion(ast : AST) -> (AST, bool):
    if ast.application_p() and ast.fn_expr().function_p():
        fn, arg = ast.fn_expr(), ast.arg_expr()
        return subsitute_ast(fn.fn_body(), fn.identifier(), arg), True
    return ast, False

def eta_conversion(ast : AST) -> (AST, bool):
    if ast.function_p() and ast.fn_body().application_p() \
       and ast.fn_body().arg_expr().terminate_p() \
       and ast.fn_body().arg_expr().root == ast.identifier():
        return ast.fn_body().fn_expr(), True
    return ast, False

def normal(ast : AST, max_times : int = 0) -> AST:
    """
    Compute on AST `ast' and return the result as computed (reduced) AST.
    Note: the computation follows the Normal Reduction Rule.

    Para:
    + `ast': AST node for expression to be expanded
    + `max_depth': max depth for simplify iteration
    """
    def simplify_ast(ast : AST) -> (AST, bool):
        # return simplified ast and whether simplified bool
        if ast.application_p(): # beta conversion
            ast, simp_p = beta_conversion(ast)
            if simp_p:
                return ast, True

            fn, simp_p = simplify_ast(ast.fn_expr())
            if simp_p:
                return AST("←", fn, ast.arg_expr()), True

            arg, simp_p = simplify_ast(ast.arg_expr())
            if simp_p:
                return AST("←", ast.fn_expr(), arg), True
        if ast.function_p(): # eta conversion
            # ast, simp_p = eta_conversion(ast)
            # if simp_p:
            #     return ast, True
            body, simp_p = simplify_ast(ast.fn_body())
            if simp_p:
                return AST("λ", AST(ast.identifier()), body), True
        return ast, False
    if max_times == 0:
        return ast

    if max_times < 0:
        ast, simp_p = simplify_ast(ast)
        while simp_p:
            ast, simp_p = simplify_ast(ast)
    else:
        ast, simp_p = simplify_ast(ast)
        max_times -= 1
        while simp_p and max_times > 0:
            ast, simp_p = simplify_ast(ast)
            max_times -= 1
    if simp_p:
        print("Warning: simplify reaches max iteration. ")
    return ast

def compute(ast : AST, max_depth : int = 0) -> AST:
    """
    Compute on AST `ast' and return the result as computed (reduced) AST.
    Note: the computation follows the Application Reduction Rule.

    Para:
    + `ast': AST node for expression to be simplified
    + `max_depth': max depth for simplify iteration
    """
    SIMPLIFY_WARNING_P = False
    def simplify_ast(ast : AST, max_depth : int = 1) -> AST:
        nonlocal SIMPLIFY_WARNING_P
        if (not ast.terminate_p()) and max_depth == 0:
            if not SIMPLIFY_WARNING_P:
                print("Warning: simplify reaches max iteration. ")
                SIMPLIFY_WARNING_P = True
            return ast
        # only compute application, other AST will return itself
        if ast.function_p():
            return AST("λ",
                       AST(ast.identifier()),
                       simplify_ast(ast.fn_body(), max_depth))
        if ast.application_p():
            fn  = simplify_ast(ast.fn_expr(),  max_depth)
            arg = simplify_ast(ast.arg_expr(), max_depth)
            if fn.function_p():
                return simplify_ast(subsitute_ast(fn.fn_body(), fn.identifier(), arg),
                                    max_depth - 1)
            else:
                return AST("←", fn, arg)
        return ast
    if max_depth == 0:
        return ast
    return simplify_ast(ast, max_depth)
