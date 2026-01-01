import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
source_path = os.path.join(project_root, 'results/generated_code/calculator')
sys.path.insert(0, source_path)

from main import *

import pytest

@pytest.fixture
def calculator():
    return Calculator()


def test_add(calculator):
    assert calculator.add(2, 3) == 5
    assert calculator.add(-1, 1) == 0
    assert calculator.add(0, 0) == 0


def test_subtract(calculator):
    assert calculator.subtract(5, 3) == 2
    assert calculator.subtract(0, 0) == 0
    assert calculator.subtract(-1, -1) == 0


def test_multiply(calculator):
    assert calculator.multiply(2, 3) == 6
    assert calculator.multiply(-1, 1) == -1
    assert calculator.multiply(0, 5) == 0


def test_divide(calculator):
    assert calculator.divide(10, 2) == 5.0
    assert calculator.divide(0, 1) == 0.0

    with pytest.raises(ValueError):
        calculator.divide(1, 0)
