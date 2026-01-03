import sys
import pathlib
THIS_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = pathlib.Path(r'E:\研一（上）\LLM_Course\wddCodeAgent\wddCodeAgent\wddCodeAgent\results\generated_code\project').resolve()
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from main import *

import pytest

@pytest.mark.parametrize('n, expected', [
    (0, 1),
    (5, [1, 2, 6, 24, 15]),
    (-1, 'Input must be a non-negative integer'),
    ('a', 'Input must be a non-negative integer'),
    (3.5, 'Input must be a non-negative integer')
])
def test_factorial(n, expected):
    if isinstance(expected, str):
        with pytest.raises(ValueError) as exc_info:
            factorial(n)
        assert str(exc_info.value) == expected
    else:
        assert factorial(n) == expected

@pytest.mark.parametrize('n, expected', [
    (0, 0),
    (5, 15),
    (-1, 'Input must be a non-negative integer'),
    ('a', 'Input must be a non-negative integer'),
    (3.5, 'Input must be a non-negative integer')
])
def test_sum_to_n(n, expected):
    if isinstance(expected, str):
        with pytest.raises(ValueError) as exc_info:
            sum_to_n(n)
        assert str(exc_info.value) == expected
    else:
        assert sum_to_n(n) == expected

@pytest.mark.parametrize('n, expected', [
    (0, []),
    (1, [1]),
    (2, [1, 2]),
    (3, [1, 2, 6]),
    (-1, 'Input must be a non-negative integer'),
    ('a', 'Input must be a non-negative integer'),
    (3.5, 'Input must be a non-negative integer')
])
def test_f(n, expected):
    if isinstance(expected, str):
        with pytest.raises(ValueError) as exc_info:
            f(n)
        assert str(exc_info.value) == expected
    else:
        assert f(n) == expected