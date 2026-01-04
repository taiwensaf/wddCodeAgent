def unique_digits(x):
    def has_no_even_digit(num):
        return all(int(digit) % 2 != 0 for digit in str(num))

    result = [num for num in x if has_no_even_digit(num)]
    return sorted(result)