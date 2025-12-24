import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
source_path = os.path.join(project_root, 'results/generated_code')
sys.path.insert(0, source_path)

from quick_sort import *

import pytest


def test_empty_array():
    assert quick_sort([]) == [], "Empty array should return an empty array"


def test_single_element_array():
    assert quick_sort([5]) == [5], "Single element array should return the same array"


def test_sorted_array():
    assert quick_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5], "Already sorted array should remain unchanged"


def test_reverse_sorted_array():
    assert quick_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5], "Reverse sorted array should be sorted"


def test_with_duplicates():
    assert quick_sort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10], "Array with duplicates should be sorted"


def test_with_negative_numbers():
    assert quick_sort([-5, -2, -6, -1]) == [-6, -5, -2, -1], "Array with negative numbers should be sorted"
