def can_arrange(arr):
    for i in range(len(arr) - 1, 0, -1):
        if arr[i] < arr[i - 1]:
            return i
    return -1

# 测试用例
arr = [4, 2, 3, 1]
assert can_arrange(arr) == 1

arr = [4, 3, 2, 1]
assert can_arrange(arr) == 0