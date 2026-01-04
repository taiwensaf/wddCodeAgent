def f(n):
    def factorial(x):
        if x == 0:
            return 1
        else:
            return x * factorial(x - 1)

    def sum_to_x(x):
        return sum(range(1, x + 1))

    result = []
    for i in range(1, n + 1):
        if i % 2 == 0:
            result.append(factorial(i))
        else:
            result.append(sum_to_x(i))
    return result