import sys
import pathlib
THIS_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = pathlib.Path(r'E:\研一（上）\LLM_Course\wddCodeAgent\wddCodeAgent\wddCodeAgent\results\generated_code\humaneval_99').resolve()
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from main import *

import pytest

def test_closest_integer_normal_case():
    assert closest_integer('3.5') == 4
    assert closest_integer('-2.5') == -3

def test_closest_integer_boundary_case():
    assert closest_integer('0.5') == 1
    assert closest_integer('-0.5') == -1