# /*
#  * Ass1: Generate Symbol table, Literal table, Pool table & Intermediate code of
#  * a two-pass
#  * Assembler for the given source code.
#  */

"""
import os

KEYWORD_INSTRUCTIONS = ["LOAD", "ADD", "MULT"]
KEYWORD_COMP_DIRECTIVES = ["START", "ORIGIN", "LTORG", "END"]
KEYWORD_DATA_DEFINATION = ["DC", "DS"]
LC = 0

intermediate_code = []  # To store intermediate code

opcode_table = {
    # Imperative Statements (IS)
    "STOP":   {"class": "IS", "opcode": 0, "length": 1},
    "ADD":    {"class": "IS", "opcode": 1, "length": 1},
    "SUB":    {"class": "IS", "opcode": 2, "length": 1},
    "MULT":   {"class": "IS", "opcode": 3, "length": 1},
    "MOVER":  {"class": "IS", "opcode": 4, "length": 1},
    "MOVEM":  {"class": "IS", "opcode": 5, "length": 1},
    "COMP":   {"class": "IS", "opcode": 6, "length": 1},
    "BC":     {"class": "IS", "opcode": 7, "length": 1},
    "DIV":    {"class": "IS", "opcode": 8, "length": 1},
    "READ":   {"class": "IS", "opcode": 9, "length": 1},
    "PRINT":  {"class": "IS", "opcode": 10, "length": 1},
    "LOAD":   {"class": "IS", "opcode": 11, "length": 1},

    # Assembler Directives (AD)
    "START":  {"class": "AD", "opcode": 1, "length": 1},
    "END":    {"class": "AD", "opcode": 2, "length": 1},
    "ORIGIN": {"class": "AD", "opcode": 3, "length": 1},
    "EQU":    {"class": "AD", "opcode": 4, "length": 1},
    "LTORG":  {"class": "AD", "opcode": 5, "length": 1},
    # Declarative Statements (DL)
    "DS":     {"class": "DL", "opcode": 1, "length": 1},
    "DC":     {"class": "DL", "opcode": 2, "length": 1},

    # Registers (RG)
    "AREG":   {"class": "RG", "opcode": 1, "length": 1},
    "BREG":   {"class": "RG", "opcode": 2, "length": 1},
    "CREG":   {"class": "RG", "opcode": 3, "length": 1},
    "DREG":   {"class": "RG", "opcode": 4, "length": 1},

    # Condition Codes (CC)
    "EQ":     {"class": "CC", "opcode": 1, "length": 1},
    "LT":     {"class": "CC", "opcode": 2, "length": 1},
    "GT":     {"class": "CC", "opcode": 3, "length": 1},
    "LE":     {"class": "CC", "opcode": 4, "length": 1},
    "GE":     {"class": "CC", "opcode": 5, "length": 1},
    "ANY":    {"class": "CC", "opcode": 6, "length": 1},
}


symbol_table = {}

literal_table = []  # list of {'name': str, 'address': int|None}

pool_table = []  # list of 1-based start indices into literal_table

error_table = {
    "E01": "Duplicate Definition of Symbol",
    "E02": "Symbol Not Declared",
    "E03": "Invalid Mnemonic",
}

warning_table = {
    "W01": "Symbol Declared But Not Used",
}

errors   = []   
warnings = []   
symbol_usage = set()  

def extract_lines(file: str)->list:
    with open(file, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

def extract_instructions(line: list)->list:
    instructions = []
    for l in line:
        instructions.append(l.split())
    return instructions

def is_symobol(token: str)->bool:
    if token.isidentifier() and token not in opcode_table.keys():
        return True
    return False

def is_literal(token: str)->bool:
    if token.startswith('='):
        return True
    return False

def get_symbol_index(symbol: str) -> int:
    symbols = list(symbol_table.keys())
    if symbol in symbols:
        return symbols.index(symbol) + 1
    return 0

def get_literal_index(literal: str, pool_start_0: int = 0) -> int:
    for i in range(pool_start_0, len(literal_table)):
        if literal_table[i]['name'] == literal:
            return i + 1
    return 0

def get_opcode_tuple(mnemonic: str) -> str:
    if mnemonic in opcode_table:
        info = opcode_table[mnemonic]
        return f"({info['class']}, {info['opcode']:02d})"
    return ""

def get_operand_tuple(operand: str, pool_start_0: int = 0) -> str:
    if operand.startswith("='") or operand.startswith("="):
        idx = get_literal_index(operand, pool_start_0)
        return f"(L, {idx:02d})"
    elif operand.isdigit():
        # Constant
        return f"(C, {operand})"
    elif operand in opcode_table and opcode_table[operand]['class'] == 'RG':
        # Register
        return f"({opcode_table[operand]['class']}, {opcode_table[operand]['opcode']:02d})"
    elif is_symobol(operand):
        # Symbol
        idx = get_symbol_index(operand)
        return f"(S, {idx:02d})"
    return ""

def analyze(extracted_lines: list)->dict:
    global LC
    global intermediate_code

    pool_table.append(1)
    current_pool_lit_start = 0     # 0-based index into literal_table where current pool begins
    symbol_order = []
    error_lines = set()  # set of 1-based line numbers with errors

    for line_num_p1, ins in enumerate(extracted_lines, start=1):
        if len(ins) >= 2 and ins[1] in opcode_table:
            lbl   = ins[0]
            mnem  = ins[1]
        else:
            lbl   = None
            mnem  = ins[0]

        if lbl:
            if lbl in symbol_table and symbol_table[lbl] is not None:
                errors.append((
                    line_num_p1, "E01",
                    f"Symbol '{lbl}' already defined at address {symbol_table[lbl]}"
                ))
                error_lines.add(line_num_p1)
            else:
                # Fresh definition OR resolving a forward reference
                symbol_table[lbl] = LC
                if lbl not in symbol_order:
                    symbol_order.append(lbl)

        valid_opcodes = {
            k for k, v in opcode_table.items()
            if v['class'] not in ('RG', 'CC')
        }
        if mnem not in valid_opcodes:
            errors.append((
                line_num_p1, "E03",
                f"Invalid mnemonic '{mnem}'"
            ))
            error_lines.add(line_num_p1)
            
        operand_start = 2 if lbl else 1
        for token in ins[operand_start:]:
            clean_token = token.split('+')[0].split('-')[0]
            if is_symobol(clean_token):
                symbol_usage.add(clean_token)
                if clean_token not in symbol_order:
                    symbol_order.append(clean_token)
                    symbol_table[clean_token] = None   # forward / unknown ref

        if is_literal(ins[-1]):
            already_in_pool = any(
                lit['name'] == ins[-1]
                for lit in literal_table[current_pool_lit_start:]
            )
            if not already_in_pool:
                literal_table.append({'name': ins[-1], 'address': None})

        if 'START' in ins:
            LC = int(ins[ins.index('START') + 1])
        elif 'ORIGIN' in ins:
            instruction = ins[ins.index('ORIGIN') + 1]
            if instruction.isdigit():
                LC = int(instruction)
            else:
                parts = instruction.replace('-', '+-').split('+')
                base   = parts[0]
                offset = int(parts[1]) if len(parts) > 1 else 0
                base_addr = symbol_table.get(base)
                if base_addr is not None:
                    LC = base_addr + offset
        elif 'LTORG' in ins:
            for i in range(current_pool_lit_start, len(literal_table)):
                if literal_table[i]['address'] is None:
                    literal_table[i]['address'] = LC
                    LC += 1
            current_pool_lit_start = len(literal_table)
            pool_table.append(current_pool_lit_start + 1)
        elif 'DS' in ins:
            LC += int(ins[ins.index('DS') + 1])
        elif 'END' in ins:
            for i in range(current_pool_lit_start, len(literal_table)):
                if literal_table[i]['address'] is None:
                    literal_table[i]['address'] = LC
                    LC += 1
        elif 'EQU' in ins:
            if lbl:
                operand = ins[ins.index('EQU') + 1]
                if symbol_table.get(operand) is not None:
                    symbol_table[lbl] = symbol_table[operand]
        else:
            LC += 1

    for sym, addr in symbol_table.items():
        if addr is None:
            # Find first line that uses this symbol as an operand
            ref_line = 0
            for ln, ins in enumerate(extracted_lines, start=1):
                for token in ins[1:]:
                    if token.split('+')[0].split('-')[0] == sym:
                        ref_line = ln
                        break
                if ref_line:
                    break
            errors.append((
                ref_line, "E02",
                f"Symbol '{sym}' used but never declared"
            ))
            error_lines.add(ref_line)

    for sym in symbol_table:
        if sym not in symbol_usage:
            # find declaration line
            decl_line = 0
            for ln, ins in enumerate(extracted_lines, start=1):
                if is_symobol(ins[0]) and ins[0] == sym:
                    decl_line = ln
                    break
            warnings.append((
                decl_line, "W01",
                f"Symbol '{sym}' declared but never used"
            ))
    
    LC = 0
    current_pool_idx = 0        # which pool we're in (0-based index into pool_table)
    processed_lit_0idx = set()  # 0-based indices of literal_table entries already printed
    
    SEP = "-" * 70
    HEADER = f"{'L#':<4}|{'LABEL':<8}|{'OPCODE':<8}|{'OPERAND':<12}|{'LC':<12}|{'OPCODE IC':<12}|{'OPERAND IC':<15}|"
    
    print("\n" + "=" * 70)
    print(" " * 15 + "INTERMEDIATE CODE GENERATION")
    print("=" * 70)
    print(HEADER)
    print(SEP)
    
    for idx, ins in enumerate(extracted_lines):
        line_num = idx + 1
        label = ""
        opcode_mnem = ""
        operand = ""
        lc_str = ""
        opcode_ic = ""
        operand_ic = ""
        
        tokens = ins[:]
        # Same rule as Pass 1: label only if the second token is a known mnemonic
        if len(tokens) >= 2 and tokens[1] in opcode_table:
            label = tokens[0]
            tokens = tokens[1:]
        if len(tokens) >= 1:
            opcode_mnem = tokens[0]
        if len(tokens) >= 2:
            operand = tokens[1]
        
        # 0-based start of CURRENT pool in literal_table
        pool_start_0 = pool_table[current_pool_idx] - 1
        
        if opcode_mnem == 'START':
            LC = int(operand)
            lc_str = "LC = 0"
            opcode_ic = get_opcode_tuple('START')
            operand_ic = f"(C, {operand})"
            
        elif opcode_mnem == 'END':
            opcode_ic = get_opcode_tuple('END')
            lc_str = ""
            
        elif opcode_mnem == 'ORIGIN':
            opcode_ic = get_opcode_tuple('ORIGIN')
            lc_str = ""
            if operand.isdigit():
                LC = int(operand)
                operand_ic = f"(C, {operand})"
            else:
                parts = operand.replace('-', '+-').split('+')
                base = parts[0]
                offset = int(parts[1]) if len(parts) > 1 else 0
                base_idx = get_symbol_index(base)
                operand_ic = f"(S, {base_idx:02d})" if offset >= 0 else f"(S, {base_idx:02d}){offset}"
                base_addr = symbol_table.get(base)
                if base_addr is not None:
                    LC = base_addr + offset
                    
        elif opcode_mnem == 'LTORG':
            opcode_ic = get_opcode_tuple('LTORG')
            lc_str = ""
            err_flag = " [ERR]" if line_num in error_lines else ""
            print(f"{line_num:<4}|{label:<8}|{opcode_mnem:<8}|{operand:<12}|{lc_str:<12}|{opcode_ic:<12}|{operand_ic:<15}|{err_flag}")
            intermediate_code.append({'lc': lc_str, 'opcode_ic': opcode_ic, 'operand_ic': operand_ic})
            # Print ONLY the literals belonging to the current pool (not future pools)
            next_pool_start_0 = pool_table[current_pool_idx + 1] - 1 if current_pool_idx + 1 < len(pool_table) else len(literal_table)
            for i in range(pool_start_0, next_pool_start_0):
                if i not in processed_lit_0idx and literal_table[i]['address'] is not None:
                    lit = literal_table[i]
                    processed_lit_0idx.add(i)
                    lit_lc = f"LC = {lit['address']}"
                    print(f"{'':<4}|{'':<8}|{'':<8}|{lit['name']:<12}|{lit_lc:<12}|{'':<12}|{f'(L, {i+1:02d})':<15}|")
                    intermediate_code.append({'lc': lit_lc, 'opcode_ic': '', 'operand_ic': f'(L, {i+1:02d})'})
                    LC = lit['address'] + 1
            current_pool_idx += 1  # Advance to next pool
            continue
            
        elif opcode_mnem == 'EQU':
            opcode_ic = get_opcode_tuple('EQU')
            if operand in symbol_table:
                operand_ic = f"(S, {get_symbol_index(operand):02d})"
            lc_str = ""
            
        elif opcode_mnem == 'DC':
            lc_str = f"LC = {LC}"
            opcode_ic = get_opcode_tuple('DC')
            operand_ic = f"(C, {operand})"
            LC += 1
            
        elif opcode_mnem == 'DS':
            lc_str = f"LC = {LC}"
            opcode_ic = get_opcode_tuple('DS')
            operand_ic = f"(C, {operand})"
            LC += int(operand)
            
        elif opcode_mnem in opcode_table and opcode_table[opcode_mnem]['class'] == 'IS':
            lc_str = f"LC = {LC}"
            opcode_ic = get_opcode_tuple(opcode_mnem)
            operand_ic = get_operand_tuple(operand, pool_start_0)
            LC += 1
            
        else:
            lc_str = f"LC = {LC}"
            if opcode_mnem in opcode_table:
                opcode_ic = get_opcode_tuple(opcode_mnem)
            operand_ic = get_operand_tuple(operand, pool_start_0) if operand else ""
            LC += 1
        
        intermediate_code.append({'lc': lc_str, 'opcode_ic': opcode_ic, 'operand_ic': operand_ic})
        err_flag = " [ERR]" if line_num in error_lines else ""
        print(f"{line_num:<4}|{label:<8}|{opcode_mnem:<8}|{operand:<12}|{lc_str:<12}|{opcode_ic:<12}|{operand_ic:<15}|{err_flag}")
        
        # After END, print remaining literals from the last pool
        if opcode_mnem == 'END':
            end_pool_start_0 = pool_table[current_pool_idx] - 1 if current_pool_idx < len(pool_table) else len(literal_table)
            for i in range(end_pool_start_0, len(literal_table)):
                if i not in processed_lit_0idx and literal_table[i]['address'] is not None:
                    lit = literal_table[i]
                    processed_lit_0idx.add(i)
                    lit_addr = lit['address']
                    print(f"{'':<4}|{'':<8}|{'':<8}|{lit['name']:<12}|{f'LC = {lit_addr}':<12}|{'':<12}|{f'(L, {i+1:02d})':<15}|")

    print(SEP)
    
    # ---- Symbol Table ----
    print("\n\nSymbol Table:")
    print('-'*5 + '+' + '-'*11 + '+' + '-'*9 + '+')
    print(f"{'#R':<5}|", f"{'SYMBOL':<10}|", f"{'ADDRESS':<7} |")
    print('-'*5 + '+' + '-'*11 + '+' + '-'*9 + '+')
    for i, sym in enumerate(symbol_table.keys()):
        addr = symbol_table[sym] if symbol_table[sym] is not None else "------"
        print(f"{i+1:<5}|", f"{sym:<10}|", f"{addr:<7} |")
    
    # ---- Literal Table ----
    print("\n\nLiteral Table:")
    print('-'*5 + '+' + '-'*11 + '+' + '-'*9 + '+')
    print(f"{'#R':<5}|", f"{'LITERAL':<10}|", f"{'ADDRESS':<7} |")
    print('-'*5 + '+' + '-'*11 + '+' + '-'*9 + '+')
    for i, lit in enumerate(literal_table):
        addr = lit['address'] if lit['address'] is not None else "UNDEF"
        print(f"{i+1:<5}|", f"{lit['name']:<10}|", f"{addr:<7} |")
    
    # ---- Pool Table ----
    print("\n\nPool Table:")
    print('-'*5 + '+' + '-'*9 + '+' + '-'*9 + '+')
    print(f"{'#R':<5}|", f"{'#P':<7} |", f"{'#L':<7} |")
    print('-'*5 + '+' + '-'*9 + '+' + '-'*9 + '+')
    for i in range(len(pool_table)):
        p_start = pool_table[i]
        p_end = pool_table[i + 1] - 1 if i + 1 < len(pool_table) else len(literal_table)
        p_count = p_end - p_start + 1
        print(f"{i+1:<5}|", f"{p_start:<7} |", f"{p_count:<7} |")

    # ---- Error Table ----
    print("\n\nErrors Detected:")
    W = 5; IW = 7; TW = 40; DW = 50
    SEP_E = '-'*W + '+' + '-'*IW + '+' + '-'*TW + '+' + '-'*DW + '+'
    print(SEP_E)
    print(f"{'LINE':<{W}}| {'ID':<{IW-1}}| {'TYPE':<{TW-1}}| {'DESCRIPTION':<{DW-1}}|")
    print(SEP_E)
    if errors:
        for (ln, eid, detail) in sorted(errors, key=lambda x: x[0]):
            etype = error_table.get(eid, eid)
            print(f"{ln:<{W}}| {eid:<{IW-1}}| {etype:<{TW-1}}| {detail:<{DW-1}}|")
    else:
        print("  No errors found.")
    print(SEP_E)

    # ---- Warning Table ----
    print("\n\nWarnings:")
    print(SEP_E)
    print(f"{'LINE':<{W}}| {'ID':<{IW-1}}| {'TYPE':<{TW-1}}| {'DESCRIPTION':<{DW-1}}|")
    print(SEP_E)
    if warnings:
        for (ln, wid, detail) in sorted(warnings, key=lambda x: x[0]):
            wtype = warning_table.get(wid, wid)
            print(f"{ln:<{W}}| {wid:<{IW-1}}| {wtype:<{TW-1}}| {detail:<{DW-1}}|")
    else:
        print("  No warnings.")
    print(SEP_E)

if __name__ == "__main__":
    file = './sample_ic.asm'
    lines = extract_lines(file)
    instructions = extract_instructions(lines)
    analyze(instructions)
"""

# /*
#  * Ass1 input:START 100
#  */
# START 100
# A DC 01
# LOAD A
# LOAD C
# ADD ='5'
# AD D
# ORIGIN A+2
# MULT ='10'
# ADD L
# LTORG
# L ADD ='5'
# ADD B
# B DS 1
# C EQU B
# A DS 1
# X DS 1
# END
# /

# /*
#  * Ass2:
#  * Design suitable data structures & implement a two-pass Macro processor.
#  */

"""
import os

def extract_lines(file: str)->list:
    with open(file, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip()]

def extract_instructions(line: list)->list:
    instructions = []
    for l in line:
        instructions.append(l.split())
    return instructions

MNT = {}
MDT = []
INTERMEDIATE_CODE = []
PARAMETER_TBL = {}
def analyze(extracted_lines: list)->dict:
    macro_name = None
    macro_flag = False
    
    for ins in extracted_lines:
        if 'MACRO' == ins[0]:
            macro_flag = True
            macro_name = ins[1]
            MNT[macro_name] = {}
            MNT[macro_name]['params'] = len(ins[2:])
            parameters = []
            for param in ins[2:]:
                parameters.append(str(param).replace(',',''))
            PARAMETER_TBL[macro_name] = {'formal_params': parameters}
            MNT[macro_name]['mdt_index'] = len(MDT) + 1
        elif 'MEND' == ins[0]:
            MDT.append(ins)
            macro_flag = False
            macro_name = None
        else:
            if macro_flag:
                params = PARAMETER_TBL[macro_name]
                if len(ins) == 2:
                    if ins[1] in params['formal_params']:
                        ins[1] = f"#{params['formal_params'].index(ins[1]) + 1}"
                        MDT.append(ins)
                    else:
                        MDT.append(ins)
                else:
                    MDT.append(ins)
            else:
                INTERMEDIATE_CODE.append(ins)
    
    print("\nMNT:")
    print(f"{'Name of Macro':<15}|", f"{'No. of Params':<15}|", f"{'Starting Index':<15} |")
    print('-'*15 + '+' + '-'*16 + '+' + '-'*17 + '+')
    for macro in MNT.keys():
        print(f"{macro:<15}|", f"{MNT[macro]['params']:<15}|", f"{MNT[macro]['mdt_index']:<15} |")
    print('-'*15 + '+' + '-'*16 + '+' + '-'*17 + '+')
    
    print("\nMDT:")
    print(f"{'#':<15}|", f"{'MDT':<15}|")
    print('-'*15 + '+' + '-'*16 + '+')
    for code in MDT:
        print(f"{MDT.index(code)+1:<15}|", f"{' '.join(code):<15}|")
    
    print("\nIntermediate Code:")
    print(f"{'#':<15}|", f"{'Instrctions':<15}|")
    print('-'*15 + '+' + '-'*16 + '+')
    for code in INTERMEDIATE_CODE:
        print(f"{INTERMEDIATE_CODE.index(code)+1:<15}|", f"{' '.join(code):<15}|")

def expand():
    expanded_code = []
    for code in INTERMEDIATE_CODE:
        if code[0] in MNT.keys():
            macro_name = code[0]
            actual_params = code[1:]
            PARAMETER_TBL[macro_name]['actual_params'] = actual_params
            mdt_index = MNT[macro_name]['mdt_index']
            macro_ins = None
            while mdt_index <= len(MDT):
                macro_ins = MDT[mdt_index - 1]
                if 'MEND' in macro_ins:
                    break
                elif macro_ins[0] in MNT.keys():
                    nested_macro_name = macro_ins[0]
                    nested_macro_actual_params = macro_ins[1:]
                    nested_mdt_index = MNT[nested_macro_name]['mdt_index']
                    while nested_mdt_index <= len(MDT):
                        nested_macro_ins = MDT[nested_mdt_index - 1]
                        if 'MEND' in nested_macro_ins:
                            break
                        if not nested_macro_ins[0] in MNT.keys():
                            if nested_macro_ins[1].startswith('#'):
                                parameter_number = int(nested_macro_ins[1][1:])
                                if len(PARAMETER_TBL[nested_macro_name]) <= 1:
                                    actual_params_nf = ""
                                    for i, param in enumerate(nested_macro_actual_params):
                                        actual_params_nf += f"{param} "
                                    nested_macro_ins[1] = actual_params_nf
                                else:
                                    nested_macro_ins[1] = PARAMETER_TBL[nested_macro_name]['actual_params'][parameter_number - 1].replace(',','')
                                
                            expanded_code.append(nested_macro_ins)
                        nested_mdt_index += 1
                if not macro_ins[0] in MNT.keys():
                            if macro_ins[1].startswith('#'):
                                parameter_number = int(macro_ins[1][1:])
                                if len(PARAMETER_TBL[macro_name]) <= 1:
                                    actual_params_nf = ""
                                    for i, param in enumerate(PARAMETER_TBL[macro_name]['actual_params']):
                                        actual_params_nf += f"{param} "
                                    macro_ins[1] = actual_params_nf
                                else:
                                    macro_ins[1] = PARAMETER_TBL[macro_name]['actual_params'][parameter_number - 1].replace(',','')
                                
                            expanded_code.append(macro_ins)
                mdt_index += 1
        else:
            if not code[0] in MNT.keys():
                expanded_code.append(code)
    
    print("\nExpanded Code:")
    print("\n".join([' '.join(code) for code in expanded_code]))

if __name__ == "__main__":
    file = './samplepgm.asm'
    lines = extract_lines(file)
    instructions = extract_instructions(lines)
    analyze(instructions)
    expand()
    print(PARAMETER_TBL)

"""

# // Ass2 input.txt:

# LOAD A
# STORE B

# MACRO ABC 
# LOAD P 
# SUB q
# MEND

# MACRO ADD1 ARG
# LOAD X
# STORE ARG 
# MEND

# MACRO ADD5 A1, A2, A3
# STORE A2
# ADD1 5
# ADD1 55
# ADD1 10 
# LOAD A1
# LOAD A3
# MEND

# ABC
# ADD5 X1, X4, X9
# ADD1 99
# ADD5 D1, D2, D3
# END

# //

# /*
#  * Ass3: Write a program to implement a lexical analyser for parts of speech.
#  * Using
#  * LEX.
#  */

[ ] 3.1
"""
%{
#include<stdio.h>
%}

%%
car|house|man|city|country        { printf("%-15s  ->  NOUN\n",yytext); }

he|she|they|we|i|it               { printf("%-15s  ->  PRONOUN\n",yytext); }

run|eat|drives|read|write|go      { printf("%-15s  ->  VERB\n",yytext); }

big|small|blue|fast|good          { printf("%-15s  ->  ADJECTIVE\n",yytext); }

quickly|slowly|very               { printf("%-15s  ->  ADVERB\n",yytext); }

in|on|at|with|under|over          { printf("%-15s  ->  PREPOSITION\n",yytext); }

and|or|but                        { printf("%-15s  ->  CONJUNCTION\n",yytext); }

oh|wow|oops                       { printf("%-15s  ->  INTERJECTION\n",yytext); }

a|an|the                          { printf("%-15s  ->  ARTICLE\n",yytext); }

[a-zA-Z]+                         { printf("%-15s  ->  UNKNOWN WORD OR TOKEN\n",yytext); }

[ \t\n]                           ;

%%

int main()
{
    printf("\nWORD             PART OF SPEECH\n");
    printf("-----------------------------------\n");

    yylex();
    return 0;
}

int yywrap()
{
    return 1;
}

// lex ASG3A.l && gcc lex.yy.c -o ASG3A && ./ASG3A < english.txt
"""

# [ ] 3.2
"""
%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Define the structure for the Symbol Table node */
struct symnode {
    char word[50];
    char pos[20];
    struct symnode *next;
};

struct symnode *head = NULL;

/* Function to insert a word and its part of speech into the symbol table */
void insert(char *w, char *p) {
    struct symnode *ptr = head;
    
    /* Check if the word already exists in the symbol table */
    while(ptr != NULL) {
        if(strcmp(ptr->word, w) == 0) {
            return; /* Word already in symbol table, skip insertion */
        }
        ptr = ptr->next;
    }
    
    /* Create a new node and add it to the head of the list */
    struct symnode *newnode = (struct symnode *)malloc(sizeof(struct symnode));
    strcpy(newnode->word, w);
    strcpy(newnode->pos, p);
    newnode->next = head;
    head = newnode;
}

/* Function to display the symbol table */
void display() {
    struct symnode *ptr = head;
    printf("\n\n--- SYMBOL TABLE ---\n");
    printf("%-20s | %-15s\n", "WORD", "PART OF SPEECH");
    printf("----------------------------------------\n");
    while(ptr != NULL) {
        printf("%-20s | %-15s\n", ptr->word, ptr->pos);
        ptr = ptr->next;
    }
    printf("----------------------------------------\n");
}
%}

%%
    /* Lex Rules for Parts of Speech based on the provided subset */

"car"|"house"|"man"|"state"|"ocean"|"country"|"city"              { insert(yytext, "NOUN"); }
"She"|"he"|"we"|"they"|"it"                                       { insert(yytext, "PRONOUN"); }
"Come"|"go"|"walk"|"did"|"have"|"read"|"write"                    { insert(yytext, "VERB"); }
"Pretty"|"Old"|"Blue"|"smart"                                     { insert(yytext, "ADJECTIVE"); }
"abnormally"|"accidentally"|"actually"|"beautifully"|"bitterly"|"brightly"|"calmly" { insert(yytext, "ADVERB"); }
"By"|"with"|"About"|"until"                                       { insert(yytext, "PREPOSITION"); }
"And"|"but"|"or"|"while"|"because"                                { insert(yytext, "CONJUNCTION"); }
"Oh!"|"Wow!"|"Oops!"                                              { insert(yytext, "INTERJECTION"); }

[a-zA-Z]+                                                         { insert(yytext, "UNKNOWN"); }
[ \t\n.,]                                                         { /* Ignore whitespace and standard punctuation */ }
.                                                                 { /* Ignore any other characters */ }
%%

int yywrap() {
    return 1;
}

int main() {
    printf("Enter English text (Press Ctrl+D on Linux/Mac or Ctrl+Z on Windows to stop):\n");
    yylex();
    display();
    return 0;
}

// lex ASG3A.l && gcc lex.yy.c -o ASG3A && ./ASG3A < english.txt
"""

# [ ] 3.3

'''
%{
#include <stdio.h>
%}

DIGIT      [0-9]
LETTER     [a-zA-Z]
ID         {LETTER}({LETTER}|{DIGIT})*
NUM        {DIGIT}+(\.{DIGIT}+)?

%%

"if"        { printf("KEYWORD: %s\n", yytext); }
"while"     { printf("KEYWORD: %s\n", yytext); }
"for"       { printf("KEYWORD: %s\n", yytext); }
"printf"    { printf("KEYWORD: %s\n", yytext); }

"%d"        { printf("FORMAT SPECIFIER: %s\n", yytext); }
"%c"        { printf("FORMAT SPECIFIER: %s\n", yytext); }
"%s"        { printf("FORMAT SPECIFIER: %s\n", yytext); }
"%f"        { printf("FORMAT SPECIFIER: %s\n", yytext); }

"=="        { printf("RELATIONAL OPERATOR: %s\n", yytext); }
"<="        { printf("RELATIONAL OPERATOR: %s\n", yytext); }
">="        { printf("RELATIONAL OPERATOR: %s\n", yytext); }
"<"         { printf("RELATIONAL OPERATOR: %s\n", yytext); }
">"         { printf("RELATIONAL OPERATOR: %s\n", yytext); }

"&&"        { printf("LOGICAL OPERATOR: %s\n", yytext); }
"||"        { printf("LOGICAL OPERATOR: %s\n", yytext); }

"+"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"-"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"*"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"/"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"%"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }

";"         { printf("PUNCTUATION: %s\n", yytext); }
","         { printf("PUNCTUATION: %s\n", yytext); }
"("         { printf("PUNCTUATION: %s\n", yytext); }
")"         { printf("PUNCTUATION: %s\n", yytext); }
"{"         { printf("PUNCTUATION: %s\n", yytext); }
"}"         { printf("PUNCTUATION: %s\n", yytext); }
"["         { printf("PUNCTUATION: %s\n", yytext); }
"]"         { printf("PUNCTUATION: %s\n", yytext); }
"#"         { printf("PUNCTUATION: %s\n", yytext); }

{NUM}       { printf("NUMBER: %s\n", yytext); }
{ID}        { printf("IDENTIFIER: %s\n", yytext); }

[ \t\n]+    ;

.           { printf("UNKNOWN: %s\n", yytext); }

%%

int main() {
    yylex();
    return 0;
}

int yywrap() {
    return 1;
}

*/
>>> // lex ASG3A.l && gcc lex.yy.c -o ASG3A && ./ASG3A < code.c

#include <stdio.h>

int main() {
    int a = 10, b = 20;
    float result = 0.0;

    if (a < b && b > 0) {
        result = a + b * 2;
        printf("Sum is: %d\n", result);
    }

    for (int i = 0; i < 5; i++) {
        printf("Value: %d\n", i);
    }

    while (a <= b) {
        a = a + 1;
    }

    return 0;
}
/*
'''

# [ ] 3.4

"""
%{
include <stdio.h>
include <string.h>

define MAX 100

char symtab[MAX][50];
int count = 0;

/* Search identifier */
int search(char *str) {
    for(int i = 0; i < count; i++) {
        if(strcmp(symtab[i], str) == 0)
            return i;
    }
    return -1;
}

/* Insert identifier */
void insert(char *str) {
    if(search(str) == -1 && count < MAX) {
        strcpy(symtab[count], str);
        count++;
    }
}
%}

DIGIT      [0-9]
LETTER     [a-zA-Z]
ID         {LETTER}({LETTER}|{DIGIT})*
NUM        {DIGIT}+(\.{DIGIT}+)?

%%

"if"        { printf("KEYWORD: %s\n", yytext); }
"while"     { printf("KEYWORD: %s\n", yytext); }
"for"       { printf("KEYWORD: %s\n", yytext); }
"printf"    { printf("KEYWORD: %s\n", yytext); }

"%d"        { printf("FORMAT SPECIFIER: %s\n", yytext); }
"%c"        { printf("FORMAT SPECIFIER: %s\n", yytext); }
"%s"        { printf("FORMAT SPECIFIER: %s\n", yytext); }
"%f"        { printf("FORMAT SPECIFIER: %s\n", yytext); }

"=="        { printf("RELATIONAL OPERATOR: %s\n", yytext); }
"<="        { printf("RELATIONAL OPERATOR: %s\n", yytext); }
">="        { printf("RELATIONAL OPERATOR: %s\n", yytext); }
"<"         { printf("RELATIONAL OPERATOR: %s\n", yytext); }
">"         { printf("RELATIONAL OPERATOR: %s\n", yytext); }

"&&"        { printf("LOGICAL OPERATOR: %s\n", yytext); }
"||"        { printf("LOGICAL OPERATOR: %s\n", yytext); }

"+"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"-"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"*"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"/"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }
"%"         { printf("ARITHMETIC OPERATOR: %s\n", yytext); }

";"         { printf("PUNCTUATION: %s\n", yytext); }
","         { printf("PUNCTUATION: %s\n", yytext); }
"("         { printf("PUNCTUATION: %s\n", yytext); }
")"         { printf("PUNCTUATION: %s\n", yytext); }
"{"         { printf("PUNCTUATION: %s\n", yytext); }
"}"         { printf("PUNCTUATION: %s\n", yytext); }
"["         { printf("PUNCTUATION: %s\n", yytext); }
"]"         { printf("PUNCTUATION: %s\n", yytext); }
"#"         { printf("PUNCTUATION: %s\n", yytext); }

{NUM}       { printf("NUMBER: %s\n", yytext); }

{ID}        { printf("IDENTIFIER: %s\n", yytext); insert(yytext); }

[ \t\n]+    ;

.           { printf("UNKNOWN: %s\n", yytext); }

%%

int main() {
    yylex();

    printf("\n----- SYMBOL TABLE -----\n");
    printf("Index\tIdentifier\n");

    for(int i = 0; i < count; i++) {
        printf("%d\t%s\n", i, symtab[i]);
    }

    return 0;
}

int yywrap() {
    return 1;
}


*/
>>> // lex ASG3A.l && gcc lex.yy.c -o ASG3A && ./ASG3A < code.c

#include <stdio.h>

int main() {
    int a = 10, b = 20;
    float result = 0.0;

    if (a < b && b > 0) {
        result = a + b * 2;
        printf("Sum is: %d\n", result);
    }

    for (int i = 0; i < 5; i++) {
        printf("Value: %d\n", i);
    }

    while (a <= b) {
        a = a + 1;
    }

    return 0;
}

/*
"""

# /*
#  * Ass4: Write a program to evaluate arithmetic expression, built-in functions,
#  * and variables
#  * using YACC
#  */

# [ ] 4.1

"""
======= Command ======
bison -dy ASG4A.y && flex ASG4A.l && gcc lex.yy.c y.tab.c -o ASG4A && ./ASG4A

======== LEX ======== (ASG3A.l)
%{
#include "y.tab.h"
#include<stdio.h>
#include<stdlib.h>
%}

%%
[0-9]+      { yylval = atoi(yytext); return NUM; }
"+"         return PLUS;
"-"         return MINUS;
"*"         return MUL;
"/"         return DIV;
"("         return LPAREN;
")"         return RPAREN;
\n          return 0;
[ \t]       ;   /* ignore spaces */
.           return yytext[0];
%%

int yywrap()
{
    return 1;
}


========= YACC ========= (ASG3A.y)
%{
#include<stdio.h>
#include<stdlib.h>

int yylex();
void yyerror(const char *s);
%}

%token NUM PLUS MINUS MUL DIV LPAREN RPAREN

%%

S : E { printf("Result = %d\n", $1); }
  ;

E : E PLUS T   { $$ = $1 + $3; }
  | E MINUS T  { $$ = $1 - $3; }
  | T          { $$ = $1; }
  ;

T : T MUL F    { $$ = $1 * $3; }
  | T DIV F    { $$ = $1 / $3; }
  | F          { $$ = $1; }
  ;

F : LPAREN E RPAREN { $$ = $2; }
  | NUM              { $$ = $1; }
  ;

%%

int main()
{
    printf("Enter Expression: ");
    yyparse();
    return 0;
}

void yyerror(const char *s)
{
    printf("Invalid Expression\n");
}
"""

# [ ] 4.2
"""
======= Command ======
bison -dy ASG4A.y && flex ASG4A.l && gcc lex.yy.c y.tab.c -o ASG4A && ./ASG4A

======== LEX ======== (ASG3A.l)
%{
#include "y.tab.h"
#include <stdlib.h>
#include <string.h>
%}

%%
[0-9]+          { yylval.num = atoi(yytext); return NUMBER; }

sqrt            { return SQRT; }
strlen          { return STRLEN; }

\"[^\"]*\"      { 
                    yylval.str = strdup(yytext);
                    return STRING;
                }

[ \t\n]         ;   /* ignore whitespace */

.               { return yytext[0]; }
%%

int yywrap() {
    return 1;
}


========= YACC ========= (ASG3A.y)
%{
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int yylex();
void yyerror(const char *s);
%}

%union {
    int num;
    char *str;
}

%token <num> NUMBER
%token <str> STRING
%token SQRT STRLEN

%type <num> expr

%%

input:
    expr { 
        printf("Result = %d\n", $1); 
        exit(0);   // terminate after one input
    }
    ;

expr:
      SQRT '(' NUMBER ')'   
        { $$ = (int)sqrt($3); }

    | STRLEN '(' STRING ')' 
        { $$ = strlen($3) - 2; }  /* remove quotes */
    ;

%%

void yyerror(const char *s) {
    printf("Error: %s\n", s);
}

int main() {
    printf("Enter function: ");
    yyparse();
    return 0;
}
"""

# [ ] 4.3

"""
======= Command ======
bison -dy ASG4A.y && flex ASG4A.l && gcc lex.yy.c y.tab.c -o ASG4A && ./ASG4A

======== LEX ======== (ASG3A.l)
%{
#include "y.tab.h"
#include<stdio.h>
#include<stdlib.h>
%}

%%
[a-zA-Z]    return A;
[0-9]       return N;
"_"         return U;
\n          return 0;
.           return yytext[0];
%%

int yywrap()
{
    return 1;
}


========= YACC ========= (ASG3A.y)
%{
#include<stdio.h>
#include<stdlib.h>

int yylex();
void yyerror(const char *s);
%}

%token A N U

%%
a : A N
  | a A
  | a N
  | a U a
  | a U N
  | A
  ;
%%

int main()
{
    printf("enter the string: ");
    yyparse();
    printf("valid variable\n");
    return 0;
}

void yyerror(const char *s)
{
    printf("invalid variable\n");
    exit(0);
}
"""

# /*
#  * Ass5: Write a program to generate three address code for the simple
#  * expression.
# */



# /*
# Ass5 input.txt:a:=b*-c+b*-c
# */

# [ ] 5.1

"""
import re

temp_count = 1

def new_temp():
    global temp_count
    temp = f"t{temp_count}"
    temp_count += 1
    return temp

def precedence(op):
    if op in ('+','-'): return 1
    if op in ('*', '/'): return 2
    else: return 0
    
def infix_to_postfix(expr):
    stack = []
    output = []
    i = 0 
    tokens = re.findall(r'[a-zA-Z]+|\d+|[-+*/()]',expr)
    
    while i < len(tokens):
        token = tokens[i]
        
        if token == '-' and (i==0 or tokens[i-1] in '+-*/('):
            output.append('u-')
        elif token.isalnum():
            output.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and precedence(stack[-1]) >= precedence(token):
                output.append(stack.pop())
            stack.append(token)
        i+=1
        

    while stack:
            output.append(stack.pop())
    
    return output

def generate_TAC(lhs,postfix):
    stack = []
    code = []
    
    for token in postfix:
        if token=='u-':
            op = stack.pop()
            temp = new_temp()
            code.append(f"{temp} := -{op}")
            stack.append(temp)
        elif token in '+-*/':
            op2 = stack.pop()
            op1 = stack.pop()
            temp = new_temp()
            code.append(f"{temp} := {op1} {token} {op2}")
            stack.append(temp)
        else:
            stack.append(token)
        
    res = stack.pop()
    code.append(f"{lhs} := {res}")
    return code

def process_lines(expr):
    lhs,rhs = expr.split("=")
    postfix = infix_to_postfix(rhs)
    print(lhs,rhs,postfix)

    tac = generate_TAC(lhs,postfix)
    return tac

def main():
    expr = "x=a+b*c/d-f"
    res = process_lines(expr)
    
    for line in res:
        print(line)
        
            
main()
"""

# [ ] 5.2
"""
import re
temp_count=1
label_count=1
 
def new_temp():
    global temp_count
    t=f"t{temp_count}"
    temp_count+=1
    return t
 
def new_label():
    global label_count
    l=f"L{label_count}"
    label_count+=1
    return l
 
def Arth_tac(expr):
    expr=expr.replace(" ","")
    if "=" in expr:
        lhs,rhs=expr.split("=")
    else:
        lhs=None
        rhs=expr
    tokens=re.findall(r"[A-Za-z0-9]+|[\+\-\*\/\(\)]",rhs)
    op_stack=[]
    val_stack=[]
    tac=[]
    precedence={'+':1,'-':1,'*':2,'/':2}
 
    def apply_op():
        op=op_stack.pop()
        b=val_stack.pop()
        a=val_stack.pop()
        t=new_temp()
        tac.append(f"{t} = {a} {op} {b}")
        val_stack.append(t)
 
    for line in tokens:
        if line.isalnum():
            val_stack.append(line)
        elif line == "(":
            op_stack.append(line)
        elif line == ")":
            while op_stack and op_stack[-1]!="(":
                apply_op()
            op_stack.pop()
        else:
            while (op_stack and op_stack[-1]!="(" and precedence.get(op_stack[-1],0) >= precedence[line]):
                apply_op()
            op_stack.append(line)
 
    while op_stack:
        apply_op()
 
    result=val_stack.pop()
    if lhs:
        tac.append(f"{lhs} = {result}")
    else:
        tac.append(result)
    return tac
 
def if_else():
    print("Enter condition:")
    condition=input()
    print("If statement:")
    if_stmt=input()
    print("Else statement:")
    else_stmt=input()
    tac=[]
    L1=new_label()
    L2=new_label()
    L3=new_label()
    tac.append(f"if {condition} goto {L1}")
    tac.append(f"goto{L2}")
    tac.append(f"{L1}:")
    tac.extend(Arth_tac(if_stmt))
    tac.append(f"goto {L3}")
    tac.append(f"{L2}:")
    tac.extend(Arth_tac(else_stmt))
    tac.append(f"{L3} :")
    return tac
 
print("1. Arithmetic Expression to TAC \n2. IF-ELSE to TAC")
choice=int(input())
if choice==1:
    print("Enter expression:")
    expr=input()
    result=Arth_tac(expr)
    for r in result:
        print(r)
elif choice==2:
    result=if_else()
    for r in result:
        print(r)
"""

# /*
# Ass6: Write a program to apply various code optimization techniques for given three address code.
# */

"""
import re

def is_constant(expr):
    return re.fullmatch(r"\d+(\.\d+)?", expr)

def is_variable(expr):
    return re.fullmatch(r"[a-zA-Z]\w*", expr)

def evaluate(expr):
    try:
        return str(eval(expr))
    except:
        return expr

def simplify(expr):
    if "*" in expr:
        a, b = expr.split("*", 1)
        if a == "1":
            return b
        if b == "1":
            return a
        if a == "0" or b == "0":
            return "0"

    if "+" in expr:
        a, b = expr.split("+", 1)
        if a == "0":
            return b
        if b == "0":
            return a

    return expr


def optimize_tac(tac):
    values = {}
    optimized = []

    for line in tac:
        if "=" not in line:
            optimized.append(line)
            continue

        left, right = line.split("=")
        left = left.strip()
        right = right.strip().replace(" ", "")

        # Safe propagation (ONLY constants or variables)
        for var in values:
            if is_constant(values[var]) or is_variable(values[var]):
                right = re.sub(rf"\b{var}\b", values[var], right)

        # Simplify algebra
        right = simplify(right)

        # Constant folding
        if re.fullmatch(r"\d+([+\-*/]\d+)", right):
            right = evaluate(right)

        # Store only safe mappings
        if is_constant(right) or is_variable(right):
            values[left] = right
        else:
            values[left] = left  # block further expansion

        optimized.append(f"{left} = {right}")

    return optimized


def dead_code_elimination(tac):
    used = set()
    result = []

    if tac:
        last_line = tac[-1]
        if "=" in last_line:
            left, _ = last_line.split("=")
            used.add(left.strip())

    for line in reversed(tac):
        if "=" not in line:
            result.append(line)
            continue

        left, right = line.split("=")
        left = left.strip()
        right = right.strip()

        if left in used:
            result.append(line)

            tokens = re.findall(r"[a-zA-Z]\w*", right)
            for t in tokens:
                used.add(t)

    return list(reversed(result))


if __name__ == "__main__":
    print("Enter TAC (empty line to stop):")

    tac = []
    while True:
        line = input()
        if line == "":
            break
        tac.append(line)

    opt = optimize_tac(tac)
    final = dead_code_elimination(opt)

    print("\nOptimized TAC:")
    for line in final:
        print(line)
        
# Input:

"""
t1 = a + b
t2 = t1 * 2
t3 = t2 + c
t4 = t3 * 1
t5 = t4 + 0
t6 = t5 + d
result = t6
"""


"""