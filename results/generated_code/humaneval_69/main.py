def search(lst):
    from collections import Counter
    freq = Counter(lst)
    for num in sorted(freq, reverse=True):
        if freq[num] >= num:
            return num
    return -1
