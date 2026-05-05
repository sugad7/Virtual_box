# TWO PASS MACRO PROCESSOR (WITH OPTIONAL NESTED SUPPORT)

MNT = {}   # Macro Name Table → name : (mdt_index, param_list)
MDT = []   # Macro Definition Table


# 🔹 PASS 1 → Build MNT & MDT
def pass1(code):
    i = 0
    while i < len(code):
        line = code[i].strip()

        if line == "MACRO":
            i += 1
            header = code[i].strip().split()

            macro_name = header[0]
            params = header[1:] if len(header) > 1 else []

            # Store macro in MNT
            MNT[macro_name] = (len(MDT), params)

            i += 1
            while code[i].strip() != "MEND":
                MDT.append(code[i].strip())
                i += 1
            MDT.append("MEND")

        i += 1


# 🔥 =========================
# 🔹 OPTION 1: SIMPLE (NO NESTED MACROS)
# Uncomment this if you want basic version
# =========================

"""
def pass2(code):
    output = []
    i = 0

    while i < len(code):
        line = code[i].strip()

        # Skip macro definitions
        if line == "MACRO":
            while code[i].strip() != "MEND":
                i += 1
            i += 1
            continue

        parts = line.split()

        if parts and parts[0] in MNT:
            macro_name = parts[0]
            actual_args = parts[1:]

            mdt_index, params = MNT[macro_name]

            # Build ALA
            ALA = {}
            for p, a in zip(params, actual_args):
                ALA[p] = a

            j = mdt_index
            while MDT[j] != "MEND":
                temp_line = MDT[j]

                for key in ALA:
                    temp_line = temp_line.replace(key, ALA[key])

                output.append(temp_line)
                j += 1

        else:
            output.append(line)

        i += 1

    return output
"""


# 🔥 =========================
# 🔹 OPTION 2: ADVANCED (WITH NESTED MACROS)
# Default active
# =========================

def expand_macro(line):
    parts = line.split()

    if parts and parts[0] in MNT:
        macro_name = parts[0]
        actual_args = parts[1:]

        mdt_index, params = MNT[macro_name]

        # Build local ALA
        local_ALA = {}
        for p, a in zip(params, actual_args):
            local_ALA[p] = a

        expanded_lines = []
        j = mdt_index

        while MDT[j] != "MEND":
            temp_line = MDT[j]

            # Replace parameters
            for key in local_ALA:
                temp_line = temp_line.replace(key, local_ALA[key])

            # 🔥 Recursive call → handles nested macros
            expanded_lines.extend(expand_macro(temp_line))

            j += 1

        return expanded_lines

    else:
        return [line]


def pass2(code):
    output = []
    i = 0

    while i < len(code):
        line = code[i].strip()

        # Skip macro definitions
        if line == "MACRO":
            while code[i].strip() != "MEND":
                i += 1
            i += 1
            continue

        output.extend(expand_macro(line))
        i += 1

    return output


# 🔹 DISPLAY
def display():
    print("\nMNT (Macro Name Table):")
    for name, (idx, params) in MNT.items():
        print(name, "→ MDT Index:", idx, "Params:", params)

    print("\nMDT (Macro Definition Table):")
    for i, line in enumerate(MDT):
        print(i, line)


# 🔹 TEST INPUT (WITH NESTED MACRO)
code = [
    "MACRO",
    "INCR &A &B",
    "LDA &A",
    "ADD &B",
    "STA &A",
    "MEND",

    "MACRO",
    "DOUBLE &X &Y",
    "INCR &X &Y",
    "INCR &X &Y",
    "MEND",

    "START",
    "DOUBLE P Q",
    "END"
]

# RUN
pass1(code)
display()

expanded = pass2(code)

print("\nExpanded Code:")
for line in expanded:
    print(line)