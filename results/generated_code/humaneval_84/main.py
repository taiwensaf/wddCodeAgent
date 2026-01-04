def solve(N):
    digit_sum = sum(int(digit) for digit in str(N))
    return bin(digit_sum)[2:].zfill(4)

# 测试用例
assert solve(9999) == '100100', 'Test case for large number input'