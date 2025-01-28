"""
6.101 Lab:
Symbolic Algebra
"""

# import doctest # optional import
# import typing # optional import
# import pprint # optional import
# import string # optional import

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Expr:
    """
    Initializer.  Store an instance variable called `name`, containing the
    value passed in to the initializer.
    """

    def __add__(self, other):
        # handle addition: create an Add expression
        return Add(self, other)

    def __radd__(self, other):
        # handle right addition
        return Add(other, self)

    def __sub__(self, other):
        # handle subtraction
        return Sub(self, other)

    def __rsub__(self, other):
        # handle right subtraction
        return Sub(other, self)

    def __mul__(self, other):
        # handle multiplication
        return Mul(self, other)

    def __rmul__(self, other):
        # handle right multiplication
        return Mul(other, self)

    def __truediv__(self, other):
        # handle division
        return Div(self, other)

    def __rtruediv__(self, other):
        # handle right division
        return Div(other, self)


class Var(Expr):
    """
    Initializes a variable class
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        # evaluate with the mapping
        if self.name in mapping:
            return mapping[self.name]
        else:
            raise NameError(f"Val not in mapping")

    def deriv(self, var):
        # derivative is 1 if variable matches, else 0
        if self.name != var:
            return Num(0)
        else:
            return Num(1)

    def simplify(self):
        # variable simplifies to itself
        return self

    def __eq__(self, other):
        # variables are equal if their names are equal
        return isinstance(other, Var) and self.name == other.name


# define a number class
class Num(Expr):
    """
    Initializer.  Store an instance variable called `n`, containing the
    value passed in to the initializer.
    """

    def __init__(self, n):
        # store the numeric value as float
        self.n = float(n)

    def __str__(self):
        # convert to int if the number is integer
        if self.n.is_integer():
            return str(int(self.n))
        else:
            return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, _):
        return self.n

    def deriv(self, _):
        # derivative of a constant is zero
        return Num(0)

    def simplify(self):
        # number simplifies to itself
        return self

    def __eq__(self, other):
        # numbers are equal if they are numerically close enough
        return isinstance(other, Num) and self.n == other.n


# base class for binary operations
class BinOp(Expr):
    """
    Initializer.  Store a binary class for operations
    """

    def __init__(self, left, right):
        # convert inputs to Expr if they aren't already
        if not isinstance(left, Expr):
            if isinstance(left, str):
                left = Var(left)
            else:
                left = Num(left)
        if not isinstance(right, Expr):
            if isinstance(right, str):
                right = Var(right)
            else:
                right = Num(right)
        self.left = left
        self.right = right

    def __repr__(self):
        # simple f string solves the problems!
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def eval(self, mapping):
        # evaluate left and right, then apply the operation
        left_val = self.left.eval(mapping)
        right_val = self.right.eval(mapping)
        return self.app_oper(left_val, right_val)

    def __eq__(self, other):
        # check if same class and left/right are equal
        return (
            isinstance(other, self.__class__)
            and self.left == other.left
            and self.right == other.right
        )


# addition class
class Add(BinOp):
    """
    Addition class
    """

    def __str__(self):
        # string representation of addition
        return f"{self.left} + {self.right}"

    def deriv(self, var):
        # derivative of sum is sum of derivatives
        return Add(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        """
        Simplifcation function
        """
        # simplify left and right
        left_simpl = self.left.simplify()
        right_simpl = self.right.simplify()

        # if both are numbers, compute the sum
        if isinstance(left_simpl, Num) and isinstance(right_simpl, Num):
            return Num(left_simpl.n + right_simpl.n)
        # if either is zero, return the other
        elif isinstance(left_simpl, Num) and abs(left_simpl.n) == 0:
            return right_simpl
        elif isinstance(right_simpl, Num) and abs(right_simpl.n) == 0:
            return left_simpl
        # otherwise, return simplified addition
        return Add(left_simpl, right_simpl)

    def app_oper(self, left_val, right_val):
        return left_val + right_val


# subtraction class
class Sub(BinOp):
    """
    Subtraction class
    """

    def __str__(self):
        # need parentheses around right operand if it's Add or Sub
        right_str = (
            f"({self.right})" if isinstance(self.right, (Add, Sub)) else str(self.right)
        )
        return f"{self.left} - {right_str}"

    def deriv(self, var):
        # derivative of difference is difference of derivatives
        return Sub(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        # simplify left and right
        left_simpl = self.left.simplify()
        right_simpl = self.right.simplify()

        # if both are numbers, compute the difference
        if isinstance(left_simpl, Num) and isinstance(right_simpl, Num):
            return Num(left_simpl.n - right_simpl.n)
        # if right is zero, return left
        if isinstance(right_simpl, Num) and abs(right_simpl.n) == 0:
            return left_simpl
        # otherwise, return simplified subtraction
        return Sub(left_simpl, right_simpl)

    def app_oper(self, left_val, right_val):
        return left_val - right_val


# multiplication class
class Mul(BinOp):
    """
    Multiplication class
    """

    def __str__(self):
        # wrap operands in parentheses if needed
        left_str = (
            f"({self.left})" if isinstance(self.left, (Add, Sub)) else str(self.left)
        )
        right_str = (
            f"({self.right})" if isinstance(self.right, (Add, Sub)) else str(self.right)
        )
        return f"{left_str} * {right_str}"

    def deriv(self, var):
        # product rule
        return Add(
            Mul(self.left.deriv(var), self.right), Mul(self.left, self.right.deriv(var))
        )

    def simplify(self):
        # simplify left and right
        left_simpl = self.left.simplify()
        right_simpl = self.right.simplify()

        # if both are numbers, compute the product
        if isinstance(left_simpl, Num) and isinstance(right_simpl, Num):
            return Num(left_simpl.n * right_simpl.n)
        # if either is zero, return zero
        if (isinstance(left_simpl, Num) and abs(left_simpl.n) == 0) or (
            isinstance(right_simpl, Num) and abs(right_simpl.n) == 0
        ):
            return Num(0)
        # if either is one, return the other
        if isinstance(left_simpl, Num) and abs(left_simpl.n - 1) == 0:
            return right_simpl
        if isinstance(right_simpl, Num) and abs(right_simpl.n - 1) == 0:
            return left_simpl
        # otherwise, return simplified multiplication
        return Mul(left_simpl, right_simpl)

    def app_oper(self, left_val, right_val):
        return left_val * right_val


# division class
class Div(BinOp):
    """
    Division class
    """

    def __str__(self):
        # wrap operands in parentheses if needed
        left_str = (
            f"({self.left})" if isinstance(self.left, (Add, Sub)) else str(self.left)
        )
        right_str = (
            f"({self.right})" if isinstance(self.right, BinOp) else str(self.right)
        )
        return f"{left_str} / {right_str}"

    def deriv(self, var):
        # quotient rule
        numer = Sub(
            Mul(self.right, self.left.deriv(var)), Mul(self.left, self.right.deriv(var))
        )
        denom = Mul(self.right, self.right)
        return Div(numer, denom)

    def simplify(self):
        """
        Simplify a function
        """
        # simplify left and right
        left_simpl = self.left.simplify()
        right_simpl = self.right.simplify()

        # if both are numbers, compute the division
        if (
            isinstance(left_simpl, Num)
            and isinstance(right_simpl, Num)
            and abs(right_simpl.n) > 0
        ):
            return Num(left_simpl.n / right_simpl.n)
        # if numer is zero, return zero
        if isinstance(left_simpl, Num) and abs(left_simpl.n) == 0:
            return Num(0)
        # if denom is one, return numer
        if isinstance(right_simpl, Num) and abs(right_simpl.n - 1) == 0:
            return left_simpl
        # otherwise, return simplified division
        return Div(left_simpl, right_simpl)

    def app_oper(self, left_val, right_val):
        if abs(right_val) == 0:
            raise ZeroDivisionError("Division by zero")
        return left_val / right_val


def make_expression(expr_str):
    """
    Make an expression with the helpers below
    """
    # tokenize
    tokens = tokenize(expr_str)
    # parse the expressions
    parsed_expr, _ = parse_expression(tokens, 0)
    return parsed_expr


def tokenize(expression):
    """
    Tokenize the expression
    """
    tokens = []
    # iterator
    i = 0
    while i < len(expression):
        char = expression[i]
        if char == " ":
            i += 1  # skip spaces
            continue
        # Set for fast lookup
        if char in ("(", ")", "+", "-", "*", "/"):
            # check for negative number
            if (
                char == "-"
                and i + 1 < len(expression)
                and (expression[i + 1].isdigit() or expression[i + 1] == ".")
            ):
                start_idx = i
                i += 1
                while i < len(expression) and (
                    expression[i].isdigit() or expression[i] == "."
                ):
                    i += 1
                tokens.append(expression[start_idx:i])
            else:
                tokens.append(char)
                i += 1
        elif char.isdigit():
            start_idx = i
            while i < len(expression) and (
                expression[i].isdigit() or expression[i] == "."
            ):
                i += 1
            tokens.append(expression[start_idx:i])
        elif char.isalpha():
            tokens.append(char)
            i += 1
    return tokens


def parse_expression(tokens, index):
    """
    Parser function for a tokens
    """
    if index >= len(tokens):
        raise ValueError("There aren't enough tokens")

    token = tokens[index]

    if token == "(":
        expr, next_index = parse_paren_expression(tokens, index)
        return expr, next_index
    elif token.isalpha() and len(token) == 1:
        return Var(token), index + 1
    elif is_number(token):
        return Num(float(token)), index + 1


def parse_paren_expression(tokens, index):
    """
    Parser function for parenthetical
    """
    index += 1  # skip '('

    expr1, index = parse_expression(tokens, index)

    token = tokens[index]

    if token == ")":
        # it's a single expression inside parentheses
        return expr1, index + 1
    elif token in ("+", "-", "*", "/"):
        operator = token
        index += 1  # move past operator

        expr2, index = parse_expression(tokens, index)

        index += 1  # skip ')'

        # build the combined expression
        if operator == "+":
            combined_expr = Add(expr1, expr2)
        elif operator == "-":
            combined_expr = Sub(expr1, expr2)
        elif operator == "*":
            combined_expr = Mul(expr1, expr2)
        elif operator == "/":
            combined_expr = Div(expr1, expr2)

        return combined_expr, index


def is_number(token):
    """
    Checks if the token is a number
    """
    # check if token is a valid number
    if token.startswith("-") and len(token) > 1:
        return token[1:].replace(".", "", 1).isdigit()
    else:
        return token.replace(".", "", 1).isdigit()


# Testing driver in main block
if __name__ == "__main__":
    # Example usage
    x = Var("x")
    y = Var("y")
    z = x + 2 - x * y + x
    print(z)  # Expect: x + 2 * x * y + x
    print(z.deriv("x"))  # derivative w.r.t x
    print(z.deriv("x").simplify())
    print(z.deriv("y"))  # derivative w.r.t y
    print(z.deriv("y").simplify())
    print(z.eval({"x": 3, "y": 7}))  # Evaluate with x=3, y=7
