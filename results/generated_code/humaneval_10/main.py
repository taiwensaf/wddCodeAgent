def is_palindrome(string: str) -> bool:
    return string == string[::-1]


def make_palindrome(string: str) -> str:
    if is_palindrome(string):
        return string
    for i in range(len(string), -1, -1):
        if is_palindrome(string[i:]):
            prefix = string[:i]
            break
    return string + prefix[::-1]