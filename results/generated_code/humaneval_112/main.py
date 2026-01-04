def reverse_delete(s, c):
    # 删除字符串 s 中所有在字符串 c 中出现的字符
    result = ''.join(char for char in s if char not in c)
    # 检查结果字符串是否为回文
    is_palindrome = result == result[::-1]
    return (result, is_palindrome)