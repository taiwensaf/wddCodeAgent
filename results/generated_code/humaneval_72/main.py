def will_it_fly(q, w):
    if q != q[::-1]:
        return False
    return sum(map(int, q)) <= w