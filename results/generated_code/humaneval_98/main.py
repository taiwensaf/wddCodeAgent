def count_upper(s):
    vowels = 'AEIOU'
    count = 0
    for i in range(1, len(s), 2):
        if s[i] in vowels:
            count += 1
    return count

def test_count_upper_normal_case():
    assert count_upper('AeIoU') == 5

def test_count_upper_empty_string():
    assert count_upper('') == 0

def test_count_upper_no_vowels():
    assert count_upper('bcdfg') == 0

def test_count_upper_mixed_case():
    assert count_upper('aEiOu') == 3