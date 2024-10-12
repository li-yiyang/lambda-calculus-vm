import re
from lib.utils import SyntaxError, UnknownToken, AST

# Syntax of Lambda Calculus (BNF)
#
#     <identifier>    := a|b|c|d|e... A|B|C|D|E...
#     <number>        := # (0|1|2|3...9)+
#     <function>      := ( λ <identifier>+ "|" <expression>+ )
#     <application>   := ( <expression> <expression>+ )
#     <expression>    := <identifier> | <number> | <function> | <application> | <list> | <string>
#     <top-level>     := <expression>+   ;; parsed as nested application
#
# Note: here symbol `|' stands for the meaning of "OR".

LVM_TOKEN_PATTERN      = re.compile("[a-zA-Z|λ\\(\\)|\\[\\]\"\"]")
LVM_SPACE_PATTERN      = re.compile("\\s+")
LVM_IDENTIFIER_PATTERN = re.compile("^[a-zA-Z]$")
LVM_NUMBER_PATTERN     = re.compile("^#[1-9][0-9]*$")

def tokenrize(code      : str,
              pattern   : re.Pattern = LVM_TOKEN_PATTERN,
              space     : re.Pattern = LVM_SPACE_PATTERN,
              err_trace : int        = 5) -> list[str]:
    """
    Split input `code' into token list.
    Return a list of splited tokens.

    Para:
    + `code': the input string, could be read from file;
    + `pattern': regexp for scanning token;
    + `space': regexp for stripping white space;
    + `err_trace': size to show context around err position
    """
    start, ends = 0, len(code)
    tokens = []

    while start < ends:
        # match for tokens
        match = pattern.match(code, start, ends)
        if match:
            token_start, start = match.span()
            tokens.append(code[token_start:start])
            continue

        # match for white spaces
        match = space.match(code, start, ends)
        if match:
            _, start = match.span()
            continue

        # fails to match all
        raise UnknownToken(code, start, err_trace)

    return tokens

# How this parser works:
# this parser is like a LR (left-to-right) parser,
# or you may say it is a top down parser.
#
# it is defined using iterator, which, is apparently
# slower than bottom up parser. also, it may be faulty
# when dealing with some extremely deep nested structure.
#
# so use it with caution and without guarantee
#
# Note: you can also try to find some 0 Day bug in this
# parser.

# (λ A B | (λ x | x A B))
CONS_AST = AST("λ", AST("J"),
               AST("λ", AST("K"),
                   AST("λ", AST("x"),
                       AST("←", AST("←", AST("x"), AST("J")), AST("K")))))

# (λ x A B | A)
NIL_AST  = AST("λ", AST("x"),
               AST("λ", AST("J"),
                   AST("λ", AST("K"), AST("J"))))

def token_at(tokens : list[str], pos : int) -> str:
    """
    Return token at position safely.
    If index `pos' is beyond `tokens' length, return empty string.
    """
    return tokens[pos] if pos < len(tokens) else ""

def parse_identifier(tokens    : list[str],
                     pos       : int) -> (AST | bool, int):
    """
    Parse Lambda Calculus for identifier.

    Lambda Calculus BNF Definition:

        <identifier>    := a|b|c|d|e... A|B|C|D|E...

    Return a LVM identifier or `False' and next pos.
    """
    token = token_at(tokens, pos)
    if token and LVM_IDENTIFIER_PATTERN.match(token):
        return AST(token), pos + 1
    else:
        return False, pos

def parse_identifier_plus(tokens : list[str],
                          pos    : int,
                          err_trace : int = 5,
                          at_least : int = -1) -> (list[AST] | bool, int):
    """
    Parse identifier list.
    Return a list of identifier or False if fails.

    Para:
    + `tokens': token list
    + `pos': current start position
    + `at_least': minimum length that the identifier list should has,
      if `at_least' is less than or equal zero, ignore length check;
      otherwise, raise SyntaxError when parsing.
    """
    identifiers, tmp, count = [], pos, 0
    identifier, pos = parse_identifier(tokens, pos)
    symbol = identifier.root
    symbols = []
    while identifier and symbol not in symbols:
        identifiers.append(identifier)
        symbols.append(symbol)
        identifier, pos = parse_identifier(tokens, pos)
        symbol = identifier.root if identifier else tokens[pos]
        count += 1

    if symbol in symbols:
        err = SyntaxError("unique identifier", tokens, pos - 1, err_trace)
        err.add_note( "  Why:")
        err.add_note(f"    `{symbol}' has been seen before in lambda args:")
        err.add_note(f"        {', '.join(symbols)}")
        err.add_note( "  Advice:")
        err.add_note(f"     Try using `(λ{''.join(symbols)}|(λ{symbol}|...))' form.")
        raise err

    if at_least > 0 and count < at_least:
        raise SyntaxError("identifier", tokens, pos, err_trace)
    elif count == 0:
        return False, tmp
    else:
        return identifiers, pos

def parse_function(tokens    : list[str],
                   pos       : int,
                   err_trace : int = 5) -> (AST | bool, int):
    """
    Parse Lambda Calculus for function.

    Lambda Calculus BNF Definition:

        <function>      := ( λ <identifier> "|" <expression> )
        <function+>     := ( λ <identifier>+ "|" <expression> )

    Return a LVM function (lambda) data or `False' and next pos.
    """
    if token_at(tokens, pos) != "(" or token_at(tokens, pos + 1) != "λ":
        return False, pos
    pos += 2

    identifiers, pos = parse_identifier_plus(tokens, pos, err_trace, 1)

    if token_at(tokens, pos) != "|":
        raise SyntaxError("|", tokens, pos, err_trace)
    pos += 1

    expressions, pos = parse_expression_plus(tokens, pos, err_trace, 1)
    expression  = expression_list_to_application(expressions)

    if token_at(tokens, pos) != ")":
        raise SyntaxError(")", tokens, pos, err_trace)
    pos += 1

    # restore the identifiers (function+) to normal function form
    # Example:
    # ids = [x, y, z]
    # => AST(λ, x, AST(λ, y, AST(λ, z, ...)))
    ast = expression
    for identifier in reversed(identifiers):
        ast = AST("λ", identifier, ast)

    return ast, pos

def parse_application(tokens : list[str],
                      pos : int,
                      err_trace : int = 5) -> (AST | bool, int):
    """
    Parse Lambda Calculus for application.

    Lambda Calculus BNF Definition:

        <application>   := ( <expression> <expression> )
        <application+>  := <expression> <expression>

    Return a LVM apply data or False and next pos.
    """
    if token_at(tokens, pos) != "(":
        return False, pos
    pos += 1

    expressions, pos = parse_expression_plus(tokens, pos, err_trace, 2)

    if token_at(tokens, pos) != ")":
        raise SyntaxError(")", tokens, pos, err_trace)
    pos += 1

    return expression_list_to_application(expressions), pos

def parse_expression(tokens : list[str],
                     pos : int = 0,
                     err_trace : int = 5) -> (AST | bool, int):
    """
    Parse Lambda Calculus for expression.

    Lambda Calculus BNF Definition:

        <expression>    := <identifier> | <function> | <application>

    Return a LVM expression data or `False' and next pos.
    """
    tmp = pos

    try:
        res, tmp = parse_identifier(tokens, pos)
        if res:
            return res, tmp
    except SyntaxError as err:
        err.traceback("parse_expression", "identifier")
        raise err

    try:
        res, tmp = parse_function(tokens, pos, err_trace)
        if res:
            return res, tmp
    except SyntaxError as err:
        err.traceback("parse_expression", "function")
        raise err

    try:
        res, tmp = parse_application(tokens, pos, err_trace)
        if res:
            return res, tmp
    except SyntaxError as err:
        err.traceback("parse_expression", "application")
        raise err

    try:
        res, tmp = parse_list(tokens, pos, err_trace)
        if res:
            return res, tmp
    except SyntaxError as err:
        err.traceback("parse_expression", "list")
        raise err

    try:
        res, tmp = parse_string(tokens, pos, err_trace)
        if res:
            return res, tmp
    except SyntaxError as err:
        err.traceback("parse_expression", "string")
        raise err


    return False, pos

def parse_list(tokens : list[str],
               pos : int = 0,
               err_trace : int = 5) -> (AST | bool, int):
    if token_at(tokens, pos) != "[":
        return False, pos
    pos += 1
    expression_list, pos = parse_expression_plus(tokens, pos, err_trace)
    if token_at(tokens, pos) != "]":
        raise SyntaxError("]", tokens, pos, err_trace)
    pos += 1
    return expression_list_to_cons(expression_list or []), pos

def make_church_number(number : int) -> AST:
    ast = AST("z")
    while number > 0:
        ast = AST("←", AST("s"), ast)
        number -= 1
    return AST("λ", AST("s"), AST("λ", AST("z"), ast))

def parse_string(tokens : list[str],
                 pos : int = 0,
                 err_trace : int = 5) -> (AST | bool, int):
    if token_at(tokens, pos) != "\"":
        return False, pos
    pos += 1

    identifiers = []
    identifier, pos = parse_identifier(tokens, pos)
    while identifier:
        identifiers.append(identifier)
        identifier, pos = parse_identifier(tokens, pos)

    if token_at(tokens, pos) != "\"":
        raise SyntaxError("\"", tokens, pos, err_trace)
    pos += 1

    expressions = []
    for identifier in identifiers:
        sym = identifier.root
        if "a" <= sym and sym <= "z":
            expressions.append(make_church_number(ord(sym) - ord("a") + 1))
        else:
            expressions.append(make_church_number(ord(sym) - ord("A") + 1 + 26))

    return expression_list_to_cons(expressions), pos

def parse_expression_plus(tokens : list[str],
                          pos    : int,
                          err_trace : int = 5,
                          at_least : int = -1) -> (list[AST] | bool, int):
    """
    Parse a list of expression AST.

    Para:
    + `tokens': token list
    + `pos': current start position
    + `at_least': minimum length that the expression list should has,
      if `at_least' is less than or equal zero, ignore length check;
      otherwise, raise SyntaxError when parsing.
    """
    expressions, tmp, count = [], pos, 0
    expression, pos = parse_expression(tokens, pos, err_trace)
    while expression:
        expressions.append(expression)
        expression, pos = parse_expression(tokens, pos, err_trace)
        count += 1

    if at_least > 0 and count < at_least:
        raise SyntaxError("expression", tokens, pos, err_trace)
    elif count == 0:
        return False, tmp
    else:
        return expressions, pos

def cons_ast(car : AST, cdr : AST) -> AST:
    return AST("←", AST("←", CONS_AST, car), cdr)

def expression_list_to_cons(expressions : list[AST]) -> AST:
    """
    Return a cons expression on expression.
    """
    if len(expressions) == 0:
        return NIL_AST
    ast = cons_ast(expressions[-1], NIL_AST)
    if len(expressions) == 1:
        return ast
    for elem in reversed(expressions[:-1]):
        ast = cons_ast(elem, ast)
    return ast

def expression_list_to_application(expressions : list[AST]) -> AST:
    """
    Return a nested expression application on expression list.

    Para:
    + `expressions': an AST element list

    Example:
    >>> expression_list_to_application([AST("x"), AST("y"), AST("z")])
    [← [← x y] z]
    """
    if len(expressions) < 2:
        return expressions[0]
    else:
        expr1, expr2 = expressions[0], expressions[1]
        ast = AST("←", expr1, expr2)
        for expr in expressions[2:]:
            ast = AST("←", ast, expr)
        return ast

def parse_top_level(tokens : list[str], err_trace : int = 5) -> AST:
    expressions, _ = parse_expression_plus(tokens, 0, err_trace, 1)
    return expression_list_to_application(expressions)

def parse(code : str, err_trace : int = 5) -> AST:
    """
    Parse input `code', return ast structure.

    A top level grammar could be <expression> <expression> as application,
    aka. application without brace ().
    """
    return parse_top_level(tokenrize(code), err_trace)

# Note:
# what if you want some more automated parser?
# for example, if you want to update to a more wiser grammar,
# or debug with a BNF definition form?
#
# of course you could do it by editing those parse_* functions,
# slow and painful, though.
#
# however, you could consider write a BNF parser and corresponding
# parser upon the BNF rule, which shall be a general solution for
# almost all the BNF rules, right?
