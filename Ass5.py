def infix_to_postfix(expression):
    stack = []
    postfix = []
    precedence = {'+':1, '-':1, '*':2, '/':2}

    for ch in expression:
        if ch.isalnum():  # operand
            postfix.append(ch)
        elif ch == '(':
            stack.append(ch)
        elif ch == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            stack.pop()
        else:  # operator
            while stack and stack[-1] != '(' and precedence[ch] <= precedence[stack[-1]]:
                postfix.append(stack.pop())
            stack.append(ch)

    while stack:
        postfix.append(stack.pop())

    return postfix


def generate_TAC(postfix, result_var):
    stack = []
    temp_count = 1

    for ch in postfix:
        if ch.isalnum():
            stack.append(ch)
        else:
            op2 = stack.pop()
            op1 = stack.pop()
            temp = f"t{temp_count}"
            print(f"{temp} = {op1} {ch} {op2}")
            stack.append(temp)
            temp_count += 1

    print(f"{result_var} = {stack.pop()}")


# 🔹 MAIN
expr = input("Enter expression (e.g., a+b*c-d/e): ")

# Split variable and expression
result_var, expression = expr.split('=')

postfix = infix_to_postfix(expression)
print("\nPostfix:", ''.join(postfix))

print("\nThree Address Code:")
generate_TAC(postfix, result_var)