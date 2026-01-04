def generate_integers(a, b):
    if a > b:
        a, b = b, a
    return [i for i in range(a, b + 1) if i % 2 == 0]

def test_generate_integers_no_even_numbers():
    assert generate_integers(5, 7) == [], "Test no even numbers in range"

def test_generate_integers_with_even_numbers():
    assert generate_integers(4, 8) == [4, 6, 8], "Test with even numbers in range"

def test_generate_integers_reversed_range():
    assert generate_integers(7, 5) == [], "Test reversed range"