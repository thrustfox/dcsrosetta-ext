import re

def check_pascal_or_camel_case_function(text):
    """
    Check string includes pascal-case or camel-case function call

    """
    
    pattern = r'(?<![a-zA-Z_])([a-z]+[A-Z][a-zA-Z0-9]*|[A-Z][a-zA-Z0-9]*)\('
    
    matches = re.findall(pattern, text)
    
    # Excluded if it consists of lowercases only
    valid_matches = [m for m in matches if not m.islower()]
    
    return len(valid_matches) > 0

def is_lua_script(text: str) -> bool:
    """
    A function that distinguishes between plain strings and Lua scripts.
    
    """
    
    if not text or not isinstance(text, str):
        print('return 1')
        return False
    
    stripped_text = text.strip()
    
    if not stripped_text:
        return False
    
    # Lua keyword patterns
    lua_keywords = [
        #r'\bfunction\b',
        #r'\blocal\b',
        #r'\breturn\b',
        #r'\bif\b.*\bthen\b',
        #r'\belse\b',
        r'\belseif\b',
        #r'\bend\b',
        #r'\bfor\b.*\bdo\b',
        #r'\bwhile\b.*\bdo\b',
        #r'\brepeat\b.*\buntil\b',
        #r'\brequire\b',
        #r'\bmodule\b',
    ]
    
    # Lua-specific syntax patterns
    lua_syntax_patterns = [
        #r'function\s+[A-Za-z0-9_]+\s*\([^)]*\)',   # function definition
        #r'local\s+[A-Za-z0-9_]+\s*=',              # local variable declaration
        #r'[A-Za-z0-9_]+\s*=\s*function\s*\(',      # function allocation
        #r'::[A-Za-z0-9_]+::',                      # label
        #r'--.*',  # Lua comment
        r'function\s+\w+\s*\([^)]*\)',  # function definition
        r'local\s+\w+\s*=',  # local variable declaration
        r'\w+\s*=\s*function\s*\(',  # function allocation
        r'\[\[.*\]\]',  # multi-line string
        #r'\.\.\.',  # variable argument
        r'::\w+::',  # label
        #r'\.\.',  # string concatenation
        #r'\w+\s*\([^)]*\)\s*[\+\-\*/]',  # expression patterns containing function calls
        #r'[\+\-\*/]\s*\w+\s*\([^)]*\)',  # function calls in expression (ex: 1 + func())
        #r'\w+\s*\([^)]*\)\s*\.\.\s*\w+',  # concatenation function call and string
    ]
    
    keyword_count = 0
    syntax_count = 0
    
    # Lua keyword check
    for pattern in lua_keywords:
        if re.search(pattern, stripped_text, re.IGNORECASE):
            keyword_count += 1
    
    # Lua syntax pattern check
    for pattern in lua_syntax_patterns:
        if re.search(pattern, stripped_text):
            syntax_count += 1
    
    # Lua-specific structures check (function-end, if-then-end etc.)
    has_function_end = bool(re.search(r'\bfunction\b.*\bend\b', stripped_text, re.DOTALL))
    has_if_then_end = bool(re.search(r'\bif\b.*\bthen\b.*\bend\b', stripped_text, re.DOTALL))
    has_for_do_end = bool(re.search(r'\bfor\b.*\bdo\b.*\bend\b', stripped_text, re.DOTALL))
    has_while_do_end = bool(re.search(r'\bwhile\b.*\bdo\b.*\bend\b', stripped_text, re.DOTALL))
    
    # Check for expression patterns containing function calls
    #has_function_call = bool(re.search(r'\w+\s*\([^)]*\)', stripped_text))
    has_operator = bool(re.search(r'[\+\-\*/]|\.\.', stripped_text))
    #has_function_in_expression = has_function_call and has_operator
    
    # Lua-specific method call (object:method() or object.method())
    has_method_call = bool(re.search(r'\w+[\.:]\w+\s*\([^)]*\)', stripped_text))
    
    # Lua standard library
    lua_libraries = ['debug', 'coroutine', 'utf8']
    #lua_libraries = ['math', 'string', 'table', 'io', 'os', 'debug', 'coroutine', 'package', 'utf8']
    has_lua_library = any(bool(re.search(rf'\b{lib}\.\w+\s*\(', stripped_text)) or
                         bool(re.search(rf'\b{lib}:\w+\s*\(', stripped_text))
                         for lib in lua_libraries)
    
    # Lua's general internal functions
    common_lua_functions = ['tonumber', 'tostring', 
                           'ipairs', 'pcall', 'xpcall', 
                           'setmetatable', 'getmetatable', 'rawget', 'rawset']
    #common_lua_functions = ['print', 'require', 'assert', 'type', 'tonumber', 'tostring', 
    #                       'pairs', 'ipairs', 'next', 'pcall', 'xpcall', 'error', 'select',
    #                       'setmetatable', 'getmetatable', 'rawget', 'rawset']
    has_lua_builtin = any(bool(re.search(rf'\b{func}\s*\(', stripped_text)) 
                         for func in common_lua_functions)
    
    # Combination of function calls and the .. operator
    #has_concat_with_call = bool(re.search(r'\w+\s*\([^)]*\)\s*\.\.', stripped_text)) or \
    #                      bool(re.search(r'\.\.\s*\w+\s*\([^)]*\)', stripped_text))
    
    has_pascal_or_camel_case_function = check_pascal_or_camel_case_function(stripped_text)
    
    if has_function_end or has_if_then_end or has_for_do_end or has_while_do_end:
        return True
    
    #if has_function_call and keyword_count >= 1:
    #    return True
    
    #if has_method_call and keyword_count >= 1:
    if has_method_call:
        return True
    
    #if has_function_in_expression and keyword_count >= 1:
    #    return True
    
    if has_lua_library:
        return True
    
    if has_lua_builtin:
        return True
    
    #if has_concat_with_call:
    #    return True
    
    #if has_camelcase_function and has_operator:
    #    return True
    
    #if has_camelcase_function:  # PascalCase/camelCase function alone is likely Lua
    #    return True
    
    #if keyword_count >= 2 and syntax_count >= 1:
    if syntax_count >= 1:
        return True
    
    if keyword_count >= 1:
        return True

    if has_pascal_or_camel_case_function:
        return True
    
    return False

