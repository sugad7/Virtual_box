import re

# 🔹 Constant Folding
def constant_folding(tac):
    optimized = []
    for line in tac:
        match = re.match(r'(\w+)\s*=\s*(\d+)\s*([\+\-\*/])\s*(\d+)', line)
        if match:
            var, op1, operator, op2 = match.groups()
            
            op1, op2 = int(op1), int(op2)
            if operator == '+':
                result = op1 + op2
            elif operator == '-':
                result = op1 - op2
            elif operator == '*':
                result = op1 * op2
            elif operator == '/':
                result = op1 // op2  # integer division

            optimized.append(f"{var} = {result}")
        else:
            optimized.append(line)
    return optimized


# 🔹 Constant Propagation (FIXED)
def constant_propagation(tac):
    values = {}
    optimized = []

    for line in tac:
        var, expr = map(str.strip, line.split('='))

        tokens = expr.split()
        new_expr = []

        for token in tokens:
            if token in values:
                new_expr.append(values[token])
            else:
                new_expr.append(token)

        expr = " ".join(new_expr)

        if expr.isdigit():
            values[var] = expr

        optimized.append(f"{var} = {expr}")

    return optimized


# 🔹 Common Subexpression Elimination (IMPROVED)
def common_subexpression_elimination(tac):
    expr_map = {}
    optimized = []

    for line in tac:
        var, expr = map(str.strip, line.split('='))

        expr = expr.replace(" ", "")  # normalize

        if expr in expr_map:
            optimized.append(f"{var} = {expr_map[expr]}")
        else:
            expr_map[expr] = var
            optimized.append(line)

    return optimized


# 🔹 Dead Code Elimination (BETTER)
def dead_code_elimination(tac):
    used = set()
    optimized = []

    # Last variable is assumed output
    last_var = tac[-1].split('=')[0].strip()
    used.add(last_var)

    for line in reversed(tac):
        var, expr = map(str.strip, line.split('='))

        if var in used:
            optimized.append(line)
            used.update(re.findall(r'\b[a-zA-Z]\w*\b', expr))

    optimized.reverse()
    return optimized


# 🔹 MAIN
tac = [
    "t1 = 2 + 3",
    "t2 = t1 * a",
    "t3 = 2 + 3",
    "t4 = t2 + t3"
]

print("\nOriginal TAC:")
for line in tac:
    print(line)

tac = constant_folding(tac)
print("\nAfter Constant Folding:")
for line in tac:
    print(line)

tac = constant_propagation(tac)
print("\nAfter Constant Propagation:")
for line in tac:
    print(line)

tac = common_subexpression_elimination(tac)
print("\nAfter Common Subexpression Elimination:")
for line in tac:
    print(line)

tac = dead_code_elimination(tac)
print("\nAfter Dead Code Elimination:")
for line in tac:
    print(line)