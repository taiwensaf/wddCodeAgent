def do_algebra(operator, operand):
    result = operand[0]
    for i in range(len(operator)):
        if operator[i] == '+':
            result += operand[i + 1]
        elif operator[i] == '-':
            result -= operand[i + 1]
        elif operator[i] == '*':
            result *= operand[i + 1]
        elif operator[i] == '//':
            if i + 1 < len(operand):
                result //= operand[i + 1]
        elif operator[i] == '**':
            if i + 1 < len(operand):
                result **= operand[i + 1]
    return result

# Test cases
assert do_algebra(['+', '*', '-'], [2, 3, 4, 1]) == 9