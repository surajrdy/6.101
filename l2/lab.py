"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)


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


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
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
    # this is when the #t or #f is utilized
    if value == "#t":
        return True
    elif value == "#f":
        return False
    else:
        # normal number or symbol
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
            elif char == " ":  # seperate w/ whitespace
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

    #Needed to make a helper function to make the code work!x
    def _parse():
        if not tokens:
            raise SchemeEvaluationError()

        curr_token = tokens.pop(0)

        if curr_token == "(":
            expr = []

            # empty list
            if tokens[0] == ")":
                tokens.pop(0)
                return expr

            # nested within the parens
            while tokens:
                if tokens[0] == ")":
                    tokens.pop(0)
                    return expr

                expr.append(_parse())

            raise SchemeSyntaxError()

        elif curr_token == ")":
            raise SchemeSyntaxError()

        else:
            return number_or_symbol(curr_token)

    result = _parse()
    return result


######################
# Built-in Functions #
######################


def calc_sub(*args):
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins["+"](*rest_nums)


def decreasing(*args):
    for i in range(len(args) - 1):
        if args[i] <= args[i + 1]:
            return False
    return True


def nonincr(*args):
    for i in range(len(args) - 1):
        if args[i] < args[i + 1]:
            return False
    return True


def increasing(*args):
    for i in range(len(args) - 1):
        if args[i] >= args[i + 1]:
            return False
    return True


def nondec(*args):
    for i in range(len(args) - 1):
        if args[i] > args[i + 1]:
            return False
    return True


def equalf(*args):
    if not args:
        return True
    first = args[0]
    for arg in args[1:]:
        if arg != first:
            return False
    return True


def not_f(*args):
    if len(args) != 1:
        raise SchemeEvaluationError()
    return True if args[0] is False else False


def cons(*args):
    if len(args) != 2:
        raise SchemeEvaluationError()
    car = args[0]
    cdr = args[1]
    return Pair(car, cdr)


def car(*args):
    if len(args) != 1:
        raise SchemeEvaluationError()
    if not isinstance(args[0], Pair):
        raise SchemeEvaluationError()
    return args[0].car


def cdr(*args):
    if len(args) != 1:
        raise SchemeEvaluationError()
    if not isinstance(args[0], Pair):
        raise SchemeEvaluationError()
    return args[0].cdr


def lists(*args):
    result = None
    for element in reversed(args or []):
        result = Pair(element, result)
    return result


def listobj(*args):
    if len(args) != 1:
        raise SchemeEvaluationError()
    obj = args[0]
    return scheme_list(obj)


def scheme_list(obj):
    if obj is None:
        return True
    elif isinstance(obj, Pair):
        return scheme_list(obj.cdr)
    else:
        return False


def scheme_length(*args):
    if len(args) != 1:
        raise SchemeEvaluationError()
    obj = args[0]
    if not scheme_list(obj):
        raise SchemeEvaluationError()
    return length(obj)


def length(args):
    if args is None:
        return 0
    else:
        return 1 + length(args.cdr)


def list_ref(*args):
    if len(args) != 2:
        raise SchemeEvaluationError()

    obj, index = args
    if not isinstance(index, int):
        raise SchemeEvaluationError()
    curr = obj

    while index > 0:
        if isinstance(curr, Pair):
            curr = curr.cdr
            index += -1
        elif not curr:
            raise SchemeEvaluationError()
    if isinstance(curr, Pair):
        return curr.car
    else:
        raise SchemeEvaluationError()


def s_append(*args):
    if args is None:
        return None
    for arg in args:
        if not scheme_list(arg):
            raise SchemeEvaluationError()
    result = None
    for lst in reversed(args):
        if lst:
            result = append(copy_lst(lst), result)
    return result


def append(lst1, lst2):
    if lst1 is None:
        return lst2
    else:
        return Pair(lst1.car, append(lst1.cdr, lst2))


def copy_lst(list):
    if list is None:
        return None
    elif isinstance(list, Pair):
        return Pair(list.car, copy_lst(list.cdr))


def begin(*args):
    return args[-1]


def evaluate_file(filename, frame=None):
    result = None
    with open(filename, "r") as f:
        file = f.read()
    tokens = tokenize(file)

    if not frame:
        frame = make_initial_frame()
    while tokens:
        expr = parse(tokens)
        result = evaluate(expr, frame)

    return result


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
    "equal?": equalf,
    ">": decreasing,
    ">=": nonincr,
    "<": increasing,
    "<=": nondec,
    "not": not_f,
    "cons": cons,
    "car": car,
    "cdr": cdr,
    "list": lists,
    "list?": listobj,
    "length": scheme_length,
    "list-ref": list_ref,
    "append": s_append,
    "begin": begin,
}


class S_Function:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __call__(self, *args):
        if len(args) != len(self.params):
            raise SchemeEvaluationError()
        new_frame = Frame(parent=self.env)

        for param, arg in zip(self.params, args):
            new_frame.define(param, arg)

        return evaluate(self.body, new_frame)


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


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
            raise SchemeNameError()

    def set(self, symbol, value):
        if symbol in self.bind:
            self.bind[symbol] = value
        elif self.parent:
            self.parent.set(symbol, value)
        else:
            raise SchemeNameError()

    def d_binding(self, symbol):
        if symbol in self.bind:
            value = self.bind.pop(symbol)
            return value
        else:
            raise SchemeNameError()


def make_initial_frame():
    global_f = Frame()
    for name, func in scheme_builtins.items():
        global_f.define(name, func)
    return Frame(global_f)


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
    if isinstance(tree, (float, int, bool)):
        return tree

    # Symbols are looked up in the curr frame
    elif isinstance(tree, str):
        return frame.lookup(tree)
    elif tree == []:
        return None

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
                #Function
                func_n = symbol[0]
                #Parameters
                params = symbol[1:]
                body = expr
                #Making the lambda expr
                lambda_expr = ["lambda", params, body]
                func_val = evaluate(lambda_expr, frame)
                frame.define(func_n, func_val)
                return func_val
            elif isinstance(symbol, str):
                value = evaluate(expr, frame)
                frame.define(symbol, value)
                return value
        elif tree[0] == "if":
            if len(tree) != 4:
                raise SchemeEvaluationError("Wrong length")
            #evaluate if the value is true
            val = evaluate(tree[1], frame)
            #if True
            if val:
                return evaluate(tree[2], frame)
            else:
                return evaluate(tree[3], frame)
        # Lambda function
        elif tree[0] == "lambda":
            if len(tree) != 3:
                raise SchemeEvaluationError("lambda error")
            params = tree[1]
            body = tree[2]
            if not isinstance(params, list):
                raise SchemeEvaluationError("Parameters")
            return S_Function(params, body, frame)
        # and function
        elif tree[0] == "and":
            result = True
            #go through the tree from the start
            for expr in tree[1:]:
                result = evaluate(expr, frame)
                if not result:
                    return False
            return result
        # or function
        elif tree[0] == "or":
            #go through the entire tree from the start
            for expr in tree[1:]:
                result = evaluate(expr, frame)
                if result:
                    return result
            return False
        # delete function
        elif tree[0] == "del":
            if len(tree) != 2:
                raise SchemeEvaluationError()
            #symbol of the thing deleted
            symbol = tree[1]
            if not isinstance(symbol, str):
                raise SchemeEvaluationError()
            value = frame.d_binding(symbol)
            return value
        # let function
        elif tree[0] == "let":
            if len(tree) != 3:
                raise SchemeEvaluationError()
            #with the let
            binders = tree[1]
            body = tree[2]
            if not isinstance(binders, list):
                raise SchemeEvaluationError()
            n_frame = Frame(parent=frame)
            for b in binders:
                if not isinstance(b, list) or len(b) != 2:
                    raise SchemeEvaluationError()
                var = b[0]
                val_expr = b[1]
                if not isinstance(var, str):
                    raise SchemeEvaluationError()
                val = evaluate(val_expr, frame)
                n_frame.define(var, val)
            return evaluate(body, n_frame)
        # set bang function
        elif tree[0] == "set!":
            if len(tree) != 3:
                raise SchemeEvaluationError()
            #extract the symbol and expr
            symbol = tree[1]
            expr = tree[2]
            if not isinstance(symbol, str):
                raise SchemeEvaluationError()
            value = evaluate(expr, frame)
            frame.set(symbol, value)
            return value
        # Functions
        else:
            #if it is a new function that is not builtin or a scheme built in
            func = evaluate(tree[0], frame)
            args = [evaluate(arg, frame) for arg in tree[1:]]
            if callable(func):  # Built in functions
                return func(*args)
            elif isinstance(func, S_Function):  # User defined ones
                return func(*args)
            else:
                raise SchemeEvaluationError()

    # Invalid
    else:
        raise SchemeEvaluationError()


if __name__ == "__main__":
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False, repl_frame=True
    ).cmdloop()
