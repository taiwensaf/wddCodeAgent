import sys
import os
# 添加源代码目录到 Python 路径
sys.path.insert(0, r'E:\研一（上）\LLM_Course\wddCodeAgent\wddCodeAgent\results\generated_code')

from 计算器函数项目 import *

import pytest

# 测试加法功能
def test_add():
    assert add(1, 2) == 3
    assert add(-1, -1) == -2
    assert add(0, 0) == 0

# 测试减法功能
def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 0) == 0
    assert subtract(-1, -1) == 0

# 测试乘法功能
def test_multiply():
    assert multiply(4, 3) == 12
    assert multiply(-1, -1) == 1
    assert multiply(0, 5) == 0

# 测试除法功能
def test_divide():
    assert divide(8, 4) == 2.0
    assert divide(9, 3) == 3.0
    with pytest.raises(ValueError):
        divide(5, 0)
