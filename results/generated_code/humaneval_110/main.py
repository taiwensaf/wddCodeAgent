def exchange(lst1, lst2):
    even_count = sum(1 for x in lst1 if x % 2 == 0)
    odd_count = len(lst1) - even_count
    available_even = sum(1 for x in lst2 if x % 2 == 0)
    return 'YES' if available_even >= odd_count else 'NO'