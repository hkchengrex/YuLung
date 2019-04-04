import math


def _get_ordering(N):
    dist = []
    idx = []

    for i in range(-N, N+1):
        for j in range(-N, N+1):
            dist.append(math.sqrt(i**2 + j**2))
            idx.append((i, j))

    return [x for _, x in sorted(zip(dist, idx))]


order_3 = _get_ordering(3)
order_4 = _get_ordering(4)
order_5 = _get_ordering(5)