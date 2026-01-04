def truncate_number(number: float) -> float:
    return number - int(number)

# Test cases
def test_truncate_number_normal_case():
    assert abs(truncate_number(3.14) - 0.14) < 1e-9

def test_truncate_number_integer_input():
    assert truncate_number(5) == 0

def test_truncate_number_negative_number():
    assert abs(truncate_number(-2.718) + 2.718) < 1e-9

def test_truncate_number(number: float, expected: float):
    assert abs(truncate_number(number) - expected) < 1e-9