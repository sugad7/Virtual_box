# ==========================================
# ASSIGNMENT 1
# ==========================================
# PASS 1 + PASS 2 (Simplified)
#
# OPTAB = {
#     "START": "AD", "END": "AD", "MOVER": "IS", "MOVEM": "IS",
#     "ADD": "IS", "SUB": "IS", "MULT": "IS", "STOP": "IS"
# }
#
# symbol_table = {}
# literal_table = []
# pool_table = [0]
# intermediate_code = []
#
# lc = 0
#
# program = [
#     "START 100",
#     "MOVER AREG ='5'",
#     "ADD BREG ='1'",
#     "MOVEM AREG X",
#     "STOP",
#     "X DS 1",
#     "END"
# ]
#
# # PASS 1
# for line in program:
#     parts = line.split()
#
#     if parts[0] == "START":
#         lc = int(parts[1])
#         continue
#
#     if parts[0] == "END":
#         break
#
#     if len(parts) == 3 and parts[2].startswith("="):
#         literal_table.append(parts[2])
#
#     if len(parts) == 3 and not parts[2].startswith("="):
#         symbol_table[parts[2]] = lc
#
#     intermediate_code.ap…


# ==========================================
# ASSIGNMENT 2
# ==========================================
# MNT = {}
# MDT = []
# ALA = {}
#
# program = [
#     "MACRO",
#     "INCR &ARG",
#     "ADD &ARG,1",
#     "MEND",
#     "START",
#     "INCR A",
#     "END"
# ]
#
# i = 0
# while i < len(program):
#     if program[i] == "MACRO":
#         name, arg = program[i+1].split()
#         MNT[name] = len(MDT)
#         ALA[arg] = "#1"
#         MDT.append(program[i+1])
#         MDT.append(program[i+2])
#         i += 3
#     else:
#         i += 1
#
# print("MNT:", MNT)
# print("MDT:", MDT)
# print("ALA:", ALA)


# ==========================================
# ASSIGNMENT 3
# ==========================================
# import re
#
# code = "int a = b + 10;"
#
# tokens = [
#     ('KEYWORD', r'\bint\b'),
#     ('IDENTIFIER', r'[a-zA-Z_]\w*'),
#     ('NUMBER', r'\d+'),
#     ('OPERATOR', r'[+\-*/=]'),
#     ('SEMICOLON', r';')
# ]
#
# for name, pattern in tokens:
#     for match in re.finditer(pattern, code):
#         print(name, ":", match.group())


# ==========================================
# ASSIGNMENT 4
# ==========================================
# import ply.lex as lex
# import ply.yacc as yacc
#
# tokens = ('NUMBER','PLUS','MINUS')
#
# t_PLUS = r'\+'
# t_MINUS = r'-'
# t_ignore = ' \t'
#
# def t_NUMBER(t):
#     r'\d+'
#     t.value = int(t.value)
#     return t
#
# def t_error(t):
#     t.lexer.skip(1)
#
# lexer = lex.lex()
#
# def p_expr(p):
#     '''expr : expr PLUS expr
#             | expr MINUS expr'''
#     if p[2] == '+':
#         p[0] = p[1] + p[3]
#     else:
#         p[0] = p[1] - p[3]
#
# def p_expr_num(p):
#     'expr : NUMBER'
#     p[0] = p[1]
#
# def p_error(p):
#     print("Error")
#
# parser = yacc.yacc()
#
# print(parser.parse("3+5-2"))


# ==========================================
# ASSIGNMENT 5
# ==========================================
# temp_count = 1
#
# def new_temp():
#     global temp_count
#     temp = f"T{temp_count}"
#     temp_count += 1
#     return temp
#
# def precedence(op):
#     if op in ('+', '-'):
#         return 1
#     if op in ('*', '/'):
#         return 2
#     return 0
#
# def generate_TAC(expression):
#     global temp_count
#     temp_count = 1
#
#     tokens = expression.replace('=', ' = ').split()
#     output = []
#     stack = []
#     tac = []
#
#     # Convert to postfix (Shunting Yard)
#     for token in tokens:
#         if token.isalnum():
#             output.append(token)
#         elif token == '=':
#             stack.append(token)
#         else:
#             while stack and precedence(stack[-1]) >= precedence(token):
#                 output.append(stack.pop())
#             stack.append(token)
#
#     while stack:
#         output.append(stack.pop())
#
#     # Generate TAC from postfix
#     stack = []
#     for token in output:
#         if token.isalnum():
#             stack.append(token)
#         else:
#             op2 = stack.pop()
#             op1 = stack.pop()
#             temp = new_temp()
#             tac.append(f"{temp} = {op1} {token} {op2}")
#             stack.append(temp)
#
#     return tac
#
# # Example expression
# expr = "a = b + c * d - e"
#
# print("Expression:", expr)
# print("\nThree Address Code:")
#
# tac = generate_TAC(expr)
# for line in tac:
#     print(line)
#
# # Final assignment
# print(f"{expr.split()[0]} = T{temp_count-1}")


# ==========================================
# ASSIGNMENT 6
# ==========================================
# code = [
#     "t1 = 5 + 3",
#     "t2 = t1",
#     "t3 = 5 + 3"
# ]
#
# optimized = []
# seen = {}
#
# for line in code:
#     if line in seen:
#         print(f"{line}  => replaced with {seen[line]}")
#     else:
#         seen[line] = line.split('=')[0].strip()
#         optimized.append(line)
#
# print("\nOptimized Code:")
# for line in optimized:
#     print(line)
