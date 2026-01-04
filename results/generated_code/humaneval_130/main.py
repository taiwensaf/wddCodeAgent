def tri(n):
    if n == 0:
        return [3]
    elif n == 1:
        return [3, 2]
    else:
        result = [3, 2]
        for i in range(2, n + 1):
            if i % 2 == 0:
                result.append(1 + i / 2)
            else:
                result.append(result[i - 1] + result[i - 2])
        return result
