def sorted_list_sum(lst):
    filtered_lst = [word for word in lst if len(word) % 2 == 0]
    return sorted(filtered_lst, key=lambda x: (len(x), x))

# Test cases
assert sorted_list_sum(['apple', 'banana', 'cherry']) == ['apple', 'banana']