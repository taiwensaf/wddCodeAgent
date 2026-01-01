import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
source_path = os.path.join(project_root, 'results/generated_code/calculator')
sys.path.insert(0, source_path)

from main import *

import pytest

@pytest.mark.parametrize('num1, num2, operator, expected', [
    (5, 3, '+', 8),
    (5, 3, '-', 2),
    (5, 3, '*', 15),
    (5, 3, '/', 1.67),
    (0, 5, '+', 5),
    (-5, 5, '-', -10),
    (5, 0, '/', 'Division by zero'),
    (5, 3, '^', 'Invalid operator')
])
def test_calculator(num1, num2, operator, expected):
    if isinstance(expected, str) and 'Division by zero' in expected:
        with pytest.raises(ValueError) as exc_info:
            calculator(num1, num2, operator)
        assert str(exc_info.value) == 'Division by zero'
    elif isinstance(expected, str) and 'Invalid operator' in expected:
        with pytest.raises(ValueError) as exc_info:
            calculator(num1, num2, operator)
        assert str(exc_info.value) == 'Invalid operator'
    else:
        result = calculator(num1, num2, operator)
        assert result == expected
