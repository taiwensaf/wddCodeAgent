from typing import List

def separate_paren_groups(paren_string: str) -> List[str]:
    result = []
    current_group = []
    depth = 0
    for char in paren_string.replace(' ', ''):
        if char == '(':
            depth += 1
        current_group.append(char)
        if char == ')':
            depth -= 1
            if depth == 0:
                result.append(''.join(current_group))
                current_group = []
    return result

# Test cases
import pytest

def test_separate_paren_groups(input_str, expected_output):
    assert separate_paren_groups(input_str) == expected_output

@pytest.mark.parametrize('input_str, expected_output', [
    ('()()', ['()()', '()']),
    ('((()))', ['((()))']),
    ('(()())', ['(()())']),
    ('(())()', ['(())', '()']),
    ('', []),
    (' ', []),
    ('( )', ['()']),
    ('(( ))', ['( )'])
])
def test_separate_paren_groups(input_str, expected_output):
    assert separate_paren_groups(input_str) == expected_output
