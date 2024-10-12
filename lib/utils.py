import sys

# Python's trace back is useless here, disable it, using my version.

sys.tracebacklimit = 10

# this is not good habit to write something like this,
# but i'm hurry to write this code and cannot have enough time
# to prettify this code
class AST:
    pass

class AST:
    """
    Make a AST (Abstract Syntax Tree) for Lambda Calculus.

    Para:
    + `root': root node name, if only pass root name, the AST node
      will be considered as a termination node;
    + `nodes': reset arguments shall be considered as AST nodes,
      the nodes shall be AST instance for each
    """
    def __init__(self, root : str, *nodes : list) -> None:
        self.root  = root
        self.nodes = nodes

    def terminate_p(self) -> bool:
        """
        Test if a AST node is termination node.
        Return True if AST instance only have root part, otherwise, False.
        """
        return len(self.nodes) == 0

    def function_p(self) -> bool:
        """
        Test if a AST node is function node.
        Return True if AST instance root is λ, otherwise, False.
        """
        return self.root == "λ"

    def var_names(self) -> list[str]:
        """
        Return a list of all var names in AST.
        """
        if self.terminate_p():
            return [self.root]
        if self.function_p():
            return [self.identifier()] + self.fn_body().var_names()
        if self.application_p():
            return self.fn_expr().var_names() + self.arg_expr().var_names()

    def gen_var(self) -> str:
        """
        Generate a new var name in AST.
        """
        names = self.var_names()
        for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if c not in names:
                return c

    def application_p(self) -> bool:
        """
        Test if a AST node is application node.
        Return True if AST instance root is ←, otherwise, False.
        """
        return self.root == "←"

    def free_p(self, identifier : str) -> bool:
        """
        Test if `identifier' is free in whole AST.
        Return True if free, otherwise False.
        """
        if self.terminate_p():
            return self.root == identifier

        if self.function_p() and self.identifier() != identifier:
            return self.fn_body().free_p(identifier)

        if self.application_p():
            return self.fn_expr().free_p(identifier) or \
                self.arg_expr().free_p(identifier)

        return False

    def bounded_p(self, identifier : str) -> bool:
        """
        Test if `identifier' is bounded within toplevel AST.
        Return True if bounded, otherwise False.
        """
        if self.application_p():
            return self.fn_expr().bounded_p(identifier) or \
                self.arg_expr().bounded_p(identifier)

        if self.function_p():
            if self.identifier() == identifier:
                return identifier in self.fn_body().var_names()
            else:
                return self.fn_body().bounded_p(identifier)

        return False

    def identifier(self) -> str:
        """
        Return function identifier if AST node is a function node.
        """
        assert self.function_p()
        identify = self.nodes[0]
        assert identify.terminate_p()
        return identify.root

    def fn_body(self) -> AST:
        """
        Return function body if AST node is a function node.
        """
        assert self.function_p()
        return self.nodes[1]

    def fn_expr(self) -> AST:
        """
        Return function expression if AST node is an application node.
        """
        assert self.application_p()
        return self.nodes[0]

    def arg_expr(self) -> AST:
        """
        Return argument expression if AST node is an application node.
        """
        assert self.application_p()
        return self.nodes[1]

    def prettify(self, depth : int = 0) -> str:
        """
        Return a prettify string representing the AST.

        Para:
        + `depth': depth of application level
        """
        if self.terminate_p():
            return self.root

        if self.function_p():
            identifiers, fn_body = [self.identifier()], self.fn_body()
            while fn_body.function_p() and fn_body.identifier() not in identifiers:
                identifiers.append(fn_body.identifier())
                fn_body = fn_body.fn_body()
            return f"(λ{''.join(identifiers)}|{fn_body.prettify(1)})"

        if self.application_p():
            if depth > 0:
                return f"{self.nodes[0].prettify(depth + 1)}{self.nodes[1].prettify()}"
            else:
                return f"({self.nodes[0].prettify(depth + 1)}{self.nodes[1].prettify()})"

    def __str__(self) -> str:
        # make AST node into input string form
        if self.terminate_p():
            return self.root
        if self.function_p():
            return f"(λ{self.nodes[0]}|{self.nodes[1]})"
        if self.application_p():
            return f"({self.nodes[0]}{self.nodes[1]})"

    def __repr__(self) -> str:
        # show AST node in Python REPL (for debug usage)
        if self.terminate_p():
            return self.root
        else:
            return f"[{self.root} {' '.join([node.__repr__() for node in self.nodes])}]"

class UnknownToken(Exception):
    """
    Raise error when input pattern is not a valid token.

    Ref: see function `tokenrize' for details.

    Para:
    + `code': the input string, used to show err_tracing info;
    + `position': position relative to `code' to point out error position;
    + `half': context size to show around error position.
    """
    def __init__(self,
                 code : str,
                 position : int,
                 half : int = 5) -> None:
        left, right = max(0, position - half), min(len(code) - 1, position + half)
        super().__init__("LVM Unknown Token Error! ")
        self.add_note(f"  Got:   `{code[position]}' at pos {position}. ")
        self.add_note(f"  Trace: {code[left:right]}")
        self.add_note(f"         {' ' * (position - left)}^")

class SyntaxError(Exception):
    """
    Raise error when input token stream is not a valid pattern.

    Ref: see functions `parse_*' for details.

    Para:
    + `expect': which pattern to expect, for instruction usage;
    + `tokens': list of token strings;
    + `position': position relative to `tokens' to point out error position;
    + `half': context size to show around error position.
    """
    def __init__(self,
                 expect : str,
                 tokens : list[str],
                 position : int,
                 half : int = 2) -> None:
        left, right = max(0, position - half), min(len(tokens) - 1, position + half)
        super().__init__("LVM Syntax Error! ")
        self.add_note(f"  Expect: {expect} form. ")
        if position < len(tokens):
            self.add_note(f"  Got:    token `{tokens[position]}' at pos {position}. ")
        else:
            self.add_note( "  Missing token at the end of input. ")
        self.add_note(f"  Trace:  {' '.join(tokens[left:right+1])}")

        clip = tokens[left:position]
        leng = len(clip)
        size = 0 if leng <= 1 else 1
        size += len(' '.join(clip))
        self.add_note(f"        {' ' * size}^")

        self.depth = 0

    def traceback(self, caller : str, *messages : list[str]) -> None:
        # use this to add traceback to parser stack
        if self.depth == 0:
            self.add_note("Traceback: ")

        self.depth += 1
        self.add_note(f"  {'-' * self.depth}> {caller}: {' '.join(messages)}")
