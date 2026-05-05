import re

# 🔹 Parts of Speech Dictionaries
nouns = {"boy", "girl", "dog", "cat", "apple", "car", "city"}
verbs = {"run", "eat", "play", "go", "write", "read", "walk"}
adjectives = {"big", "small", "fast", "happy", "blue", "good"}
adverbs = {"quickly", "slowly", "happily", "badly"}
pronouns = {"he", "she", "it", "they", "we", "i", "you"}
prepositions = {"in", "on", "at", "under", "over", "between"}
conjunctions = {"and", "or", "but", "because"}
articles = {"a", "an", "the"}
helping_verbs = {"is", "am", "are", "was", "were", "has", "have"}

# 🔹 Function for classification
def classify(word):
    if word in nouns:
        return "NOUN"
    elif word in verbs:
        return "VERB"
    elif word in adjectives:
        return "ADJECTIVE"
    elif word in adverbs:
        return "ADVERB"
    elif word in pronouns:
        return "PRONOUN"
    elif word in prepositions:
        return "PREPOSITION"
    elif word in conjunctions:
        return "CONJUNCTION"
    elif word in articles:
        return "ARTICLE"
    elif word in helping_verbs:
        return "HELPING VERB"
    else:
        return "UNKNOWN"

# 🔹 Lexical Analyzer Function
def lexical_analyzer(sentence):
    # Tokenization (removes punctuation)
    tokens = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())

    print("\nTokens and their Parts of Speech:\n")

    for token in tokens:
        pos = classify(token)
        print(f"{token} -> {pos}")

# 🔹 MAIN
sentence = input("Enter a sentence: ")
lexical_analyzer(sentence)




# import re

# # 🔹 Token Definitions
# keywords = {
#     'int', 'float', 'char', 'if', 'else', 'while',
#     'for', 'return', 'break', 'continue', 'void'
# }

# operators = {
#     '+', '-', '*', '/', '=', '==', '<', '>', '<=', '>=', '!=', '++', '--'
# }

# delimiters = {
#     ';', ',', '(', ')', '{', '}'
# }

# symbol_table = {}

# # 🔹 Lexical Analyzer Function
# def lexical_analyzer(code):

#     # Regex for tokenization (priority matters!)
#     token_pattern = r'==|<=|>=|!=|\+\+|--|\d+\.\d+|\d+|[a-zA-Z_]\w*|[+\-*/=<>;(),{}]'

#     tokens = re.findall(token_pattern, code)

#     print("\nTokens and Classification:\n")

#     for token in tokens:

#         if token in keywords:
#             print(f"{token} -> KEYWORD")

#         elif token in operators:
#             print(f"{token} -> OPERATOR")

#         elif token in delimiters:
#             print(f"{token} -> DELIMITER")

#         elif re.match(r'^\d+\.\d+$', token):
#             print(f"{token} -> FLOAT CONSTANT")

#         elif token.isdigit():
#             print(f"{token} -> INTEGER CONSTANT")

#         else:
#             print(f"{token} -> IDENTIFIER")

#             # Add to symbol table
#             if token not in symbol_table:
#                 symbol_table[token] = len(symbol_table) + 1


# # 🔹 MAIN
# code = input("Enter source code:\n")
# lexical_analyzer(code)

# # 🔹 Display Symbol Table
# print("\nSymbol Table:")
# for symbol, index in symbol_table.items():
#     print(f"{symbol} : {index}")