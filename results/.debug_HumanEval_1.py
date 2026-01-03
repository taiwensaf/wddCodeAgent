from typing import List


def separate_paren_groups(paren_string: str) -> List[str]:
    """ Input to this function is a string containing multiple groups of nested parentheses. Your goal is to
    separate those group into separate strings and return the list of those.
    Separate groups are balanced (each open brace is properly closed) and not nested within each other
    Ignore any spaces in the input string.
    >>> separate_paren_groups('( ) (( )) (( )( ))')
    ['()', '(())', '(()())']
    """
To solve this problem, we need to iterate through the input string while keeping track of the balance of parentheses. We'll use a counter to keep track of how many open parentheses we've encountered that haven't been closed yet. When the counter returns to zero, it means we've completed a group.

Here's a Python function that implements this logic:

```python
from typing import List

def separate_paren_groups(paren_string: str) -> List[str]:
    # Remove spaces from the input string
    paren_string = paren_string.replace(" ", "")
    
    result = []
    current_group = []
    balance = 0
    
    for char in paren_string:
        if char == '(':
            balance += 1
        elif char == ')':
            balance -= 1
        
        current_group.append(char)
        
        # When balance is zero, we have a complete group
        if balance == 0:
            result.append(''.join(current_group))
            current_group = []  # Reset the current group for the next one
    
    return result

# Example usage
print(separate_paren_groups('( ) (( )) (( )( ))'))  # Output: ['()', '(())', '(()())']
```

### Explanation:
1. **Remove spaces**: We first remove all spaces from the input string to simplify processing.
2. **Initialize variables**:
   - `result`: This will store the final list of separated groups.
   - `current_group`: This will temporarily hold characters for the current group being processed.
   - `balance`: This counter keeps track of the balance of parentheses.
3. **Iterate through the string**: For each character in the string:
   - If it's an opening parenthesis `'('`, increment the `balance`.
   - If it's a closing parenthesis `')'`, decrement the `balance`.
   - Append the current character to `current_group`.
4. **Check balance**: When `balance` returns to zero, it means we've completed a group. We then join the characters in `current_group` into a string and add it to `result`. Reset `current_group` for the next group.
5. **Return result**: Finally, return the list of separated groups.

This function should correctly separate the nested parentheses groups as required.


METADATA = {
    'author': 'jt',
    'dataset': 'test'
}


def check(candidate):
    assert candidate('(()()) ((())) () ((())()())') == [
        '(()())', '((()))', '()', '((())()())'
    ]
    assert candidate('() (()) ((())) (((())))') == [
        '()', '(())', '((()))', '(((())))'
    ]
    assert candidate('(()(())((())))') == [
        '(()(())((())))'
    ]
    assert candidate('( ) (( )) (( )( ))') == ['()', '(())', '(()())']

check(separate_paren_groups)