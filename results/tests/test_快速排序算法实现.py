#!/usr/bin/env python
# coding=utf-8

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
source_path = os.path.join(project_root, 'results/generated_code')
sys.path.insert(0, source_path)

from 快速排序算法实现 import quick_sort

import pytest


def test_normal_case():
    assert quick_sort([3, 6, 8, 10, 1, 2, 1]) == [1, 1, 2, 3, 6, 8, 10]


def test_empty_list():
    assert quick_sort([]) == []


def test_single_element_list():
    assert quick_sort([5]) == [5]


def test_repeated_elements():
    assert quick_sort([3, 3, 2, 1, 4, 4]) == [1, 2, 3, 3, 4, 4]


def test_reverse_sorted_list():
    assert quick_sort([10, 9, 8, 7, 6, 5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_already_sorted_list():
    assert quick_sort([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def test_large_list():
    assert quick_sort(list(range(1000))) == list(range(1000))


def test_negative_numbers():
    assert quick_sort([-3, -6, -8, -10, -1, -2, -1]) == [-10, -8, -6, -3, -2, -1, -1]
