import math
import re

# 🔹 Symbol Table
variables = {}

# 🔹 Allowed functions
functions = {
    "sin": math.sin,
    "cos": math.cos,
    "sqrt": math.sqrt,
    "tan": math.tan,
    "log": math.log
}

# 🔹 Tokenizer (like LEX)
def tokenize(expr):
    pattern = r'\d+\.\d+|\d+|[a-zA-Z_]\w*|[+\-*/=()]'
    return re.findall(pattern, expr)

"""
# 🔹 Evaluate expression safely (USING built-in eval - Commented Out)
def evaluate_expression_old(expr):
    try:
        # Replace variables with values
        for var in variables:
            expr = re.sub(r'\b' + var + r'\b', str(variables[var]), expr)

        # Replace functions
        for func in functions:
            if func in expr:
                expr = expr.replace(func, f'functions["{func}"]')

        # Evaluate safely
        result = eval(expr, {"__builtins__": None}, {"functions": functions})
        return result

    except Exception as e:
        return "Error"
"""

# 🔹 Helper to check if string is a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# 🔹 Parse expression to Postfix (Custom Parser avoiding eval)
def infix_to_postfix(tokens):
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    postfix = []
    stack = []

    for token in tokens:
        if is_number(token):
            postfix.append(float(token))
        elif token in variables:
            postfix.append(float(variables[token]))
        elif token in functions:
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()
            if stack and stack[-1] in functions:
                postfix.append(stack.pop())
        elif token in precedence:
            while stack and stack[-1] != '(' and stack[-1] not in functions and precedence.get(stack[-1], 0) >= precedence[token]:
                postfix.append(stack.pop())
            stack.append(token)
        else:
            raise ValueError(f"Unknown token: {token}")

    while stack:
        postfix.append(stack.pop())

    return postfix

# 🔹 Evaluate the Postfix expression stack
def evaluate_postfix(postfix):
    stack = []
    for token in postfix:
        if type(token) is float:
            stack.append(token)
        elif token in functions:
            op = stack.pop()
            stack.append(functions[token](op))
        elif token == '+':
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(op1 + op2)
        elif token == '-':
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(op1 - op2)
        elif token == '*':
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(op1 * op2)
        elif token == '/':
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(op1 / op2)
    return stack[0]

# 🔹 Evaluate expression safely
def evaluate_expression(expr):
    try:
        tokens = tokenize(expr)
        postfix = infix_to_postfix(tokens)
        result = evaluate_postfix(postfix)
        return result
    except Exception as e:
        return "Error"

# 🔹 Main Interpreter Loop
def main():
    print("Arithmetic Expression Evaluator (Python)")
    print("Supports variables and functions (sin, cos, sqrt, log)")
    print("Type 'exit' to quit\n")

    while True:
        line = input(">> ").strip()

        if line.lower() == "exit":
            break

        # Assignment
        if "=" in line:
            var, expr = line.split("=", 1)
            var = var.strip()
            expr = expr.strip()

            value = evaluate_expression(expr)

            if value != "Error":
                variables[var] = value
                print(f"{var} = {value}")
            else:
                print("Invalid Expression")

        # Normal expression
        else:
            result = evaluate_expression(line)
            print("Result =", result)

    # 🔹 Show Symbol Table
    print("\nSymbol Table:")
    for k, v in variables.items():
        print(f"{k} : {v}")

# 🔹 Run
if __name__ == "__main__":
    main()


# import math

# # Symbol table
# variables = {}

# print("Enter expressions (type 'exit' to stop):")

# while True:
#     line = input(">> ")

#     if line == "exit":
#         break

#     try:
#         # Assignment
#         if "=" in line:
#             var, expr = line.split("=")
#             var = var.strip()
#             expr = expr.strip()

#             value = eval(expr, {"__builtins__": None}, {**math.__dict__, **variables})
#             variables[var] = value

#             print(var, "=", value)

#         # Normal expression
#         else:
#             result = eval(line, {"__builtins__": None}, {**math.__dict__, **variables})
#             print("Result =", result)

#     except:
#         print("Invalid Expression")

# # Print symbol table
# print("\nSymbol Table:")
# for k, v in variables.items():
#     print(k, ":", v)



