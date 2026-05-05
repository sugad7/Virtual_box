MOT = {
    "STOP": ("IS", 0),
    "ADD": ("IS", 1),
    "SUB": ("IS", 2),
    "MULT": ("IS", 3),
    "MOVER": ("IS", 4),
    "MOVEM": ("IS", 5),
    "COMP": ("IS", 6),
    "BC": ("IS", 7),
    "DIV": ("IS", 8),
    "READ": ("IS", 9),
    "PRINT": ("IS", 10)
}

POT = {
    "START": ("AD", 1),
    "END": ("AD", 2),
    "ORIGIN": ("AD", 3),
    "EQU": ("AD", 4),
    "LTORG": ("AD", 5)
}

REG = {"AREG": 1, "BREG": 2, "CREG": 3, "DREG": 4}

symtab = {}
littab = []
pooltab = [0]
ic = []

lc = 0


def process_literals():
    global lc
    for i in range(pooltab[-1], len(littab)):
        lit = littab[i]
        print(f"Assigning {lit} at {lc}")
        lc += 1
    pooltab.append(len(littab))


def pass1(code):
    global lc

    for line in code:
        parts = line.replace(',', '').split()

        # START
        if parts[0] == "START":
            lc = int(parts[1])
            ic.append(f"(AD,01) (C,{parts[1]})")

        # Label
        elif parts[0].endswith(':'):
            label = parts[0][:-1]
            symtab[label] = lc

        # DS (Define Storage)
        elif len(parts) >= 3 and parts[1] == "DS":
            symtab[parts[0]] = lc
            lc += int(parts[2])

        # Imperative Statements
        elif parts[0] in MOT:
            op = parts[0]
            code_line = f"(IS,{MOT[op][1]:02})"

            if len(parts) > 1:
                reg = parts[1]
                if reg in REG:
                    code_line += f" ({REG[reg]})"

            if len(parts) > 2:
                operand = parts[2]
                if operand.startswith("='"):
                    if operand not in littab:
                        littab.append(operand)
                    code_line += f" (L,{littab.index(operand)})"
                else:
                    if operand not in symtab:
                        symtab[operand] = None
                    code_line += f" (S,{list(symtab.keys()).index(operand)})"

            ic.append(code_line)
            lc += 1

        # LTORG
        elif parts[0] == "LTORG":
            process_literals()

        # END
        elif parts[0] == "END":
            process_literals()
            ic.append("(AD,02)")
            break


def display():
    print("\nIntermediate Code:")
    for i in ic:
        print(i)

    print("\nSymbol Table:")
    for i, (sym, addr) in enumerate(symtab.items()):
        print(i, sym, addr)

    print("\nLiteral Table:")
    for i, lit in enumerate(littab):
        print(i, lit)

    print("\nPool Table:", pooltab)


# 🔹 TEST CODE
code = [
    "START 100",
    "MOVER AREG, ='5'",
    "ADD BREG, ='1'",
    "MOVEM AREG, X",
    "MOVER CREG, ='2'",
    "ADD AREG, X",
    "LTORG",
    "MOVER BREG, ='3'",
    "ADD CREG, ='4'",
    "MOVEM BREG, Y",
    "LTORG",
    "X DS 1",
    "Y DS 1",
    "END"
]

pass1(code)
display()