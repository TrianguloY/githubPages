from itertools import groupby
from typing import Iterable, Tuple

SEASONS = range(1, 4 + 1)
PUZZLES = range(1, 61 + 1)


def group_by[K, V](elements: Iterable[Tuple[K, V]]) -> list[Tuple[
    K, list[V]]]:
    """( (k1, v11), (k1, v12), (k2, v2) ) --> [ (k1, [v11, v12]), (k2, [v2]) ]"""
    return [
        (key, [element[1] for element in grouped_elements])
        for key, grouped_elements in groupby(elements, key=lambda x: x[0])
    ]
