def is_nested(string):
    stack = []
    nested = False
    for char in string:
        if char == '[':
            stack.append(char)
        elif char == ']' and stack:
            stack.pop()
            if stack:
                nested = True
        else:
            return False
    return not stack and nested