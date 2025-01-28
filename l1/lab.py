"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

# import doctest # optional import
# import typing  # optional import
# import pprint  # optional import

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    result = []
    token = ""
    for line in source.splitlines():
        for char in line.split(";", 1)[0].strip():
            if char in "()":  # Paranthesizes for new tokens
                if token:
                    result.append(token)
                    token = ""
                result.append(char)
            elif char.isspace():  # seperate w/ whitespace
                if token:
                    result.append(token)
                    token = ""
            else:
                token += char
        # Add reminaing tokens to end
        if token:
            result.append(token)
            token = ""
    return result


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if not tokens:
        raise SchemeEvaluationError("There are no tokens")
    token = tokens.pop(0)
    if token == "(":
        expr = []
        while tokens[0] != ")":
            expr.append(parse(tokens))
        tokens.pop(0)  # remove the )
        return expr
    elif token == ")":
        raise SchemeEvaluationError()
    else:
        return number_or_symbol(token)


######################
# Built-in Functions #
######################


def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins["+"](*rest_nums)


scheme_builtins = {
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": lambda *args: (
        1
        if not args
        else args[0] if len(args) == 1 else args[0] * scheme_builtins["*"](*args[1:])
    ),
    "/": lambda *args: (
        args[0] if len(args) == 1 else args[0] / scheme_builtins["*"](*args[1:])
    ),
}


class Function:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise SchemeEvaluationError("Incorrect")
        new_frame = Frame(parent=self.env)

        for param, arg in zip(self.params, args):
            new_frame.define(param, arg)

        return evaluate(self.body, new_frame)

    def __str__(self):
        return f"<Function params={self.parameters}>"


##############
# Evaluation #
##############


class Frame:
    def __init__(self, parent=None):
        self.bind = {}
        self.parent = parent

    def define(self, symbol, value):
        self.bind[symbol] = value

    def lookup(self, symbol):
        if symbol in self.bind:
            return self.bind[symbol]
        elif self.parent:
            return self.parent.lookup(symbol)
        else:
            raise SchemeNameError("Rip")


def make_initial_frame():
    global_f = Frame()
    for name, func in scheme_builtins.items():
        global_f.define(name, func)
    return Frame(parent=global_f)


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # Initialize the frame
    if frame is None:
        frame = make_initial_frame()

    # Numbers are themselves
    if isinstance(tree, int) or isinstance(tree, float):
        return tree

    # Symbols are looked up in the curr frame
    elif isinstance(tree, str):
        return frame.lookup(tree)

    # S expressions
    elif isinstance(tree, list):
        # S-expr
        if not tree:
            raise SchemeEvaluationError("Empty list")
        # Define
        if tree[0] == "define":
            if len(tree) != 3:
                raise SchemeEvaluationError()
            symbol = tree[1]
            expr = tree[2]
            if isinstance(symbol, list):
                func_n = symbol[0]
                params = symbol[1:]
                body = expr
                lambda_expr = ["lambda", params, body]
                func_val = evaluate(lambda_expr, frame)
                frame.define(func_n, func_val)
                return func_val
            elif isinstance(symbol, str):
                value = evaluate(expr, frame)
                frame.define(symbol, value)
                return value
            else:
                raise SchemeEvaluationError("Invalid")
        # Lambda function
        elif tree[0] == "lambda":
            if len(tree) != 3:
                raise SchemeEvaluationError("lambda error")
            params = tree[1]
            body = tree[2]
            if not isinstance(params, list):
                raise SchemeEvaluationError("Parameters")
            return Function(params, body, frame)
        # Functions
        else:
            func = evaluate(tree[0], frame)
            args = [evaluate(arg, frame) for arg in tree[1:]]
            if callable(func):  # Built in functions
                return func(*args)
            else:
                raise SchemeEvaluationError()

    # Invalid
    else:
        raise SchemeEvaluationError()


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False
    ).cmdloop()
    """inp = "(cat (dog (tomato)))"
    tokens = ['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']
    output = tokenize(inp)
    print(parse(tokens))"""
