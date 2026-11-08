"""Heapsort implementation (in-place, array based, max-heap).

Heap layout (0-indexed array A):
    parent(i) = (i - 1) // 2
    left(i)   = 2 * i + 1
    right(i)  = 2 * i + 2
"""

from typing import List, Optional, Callable, Any


def max_heapify(a: List[Any], n: int, i: int, key: Optional[Callable] = None) -> None:
    """Sift a[i] down within the first n elements so the subtree rooted at i
    satisfies the max-heap property. Iterative to avoid recursion overhead.

    Time: O(log n). Extra space: O(1).
    """
    k = key or (lambda x: x)
    while True:
        left = 2 * i + 1
        right = left + 1
        largest = i
        if left < n and k(a[left]) > k(a[largest]):
            largest = left
        if right < n and k(a[right]) > k(a[largest]):
            largest = right
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def build_max_heap(a: List[Any], key: Optional[Callable] = None) -> None:
    """Bottom-up heap construction (Floyd). Time: O(n)."""
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        max_heapify(a, n, i, key)


def heapsort(a: List[Any], key: Optional[Callable] = None) -> List[Any]:
    """Sort list `a` in ascending order, in place, and return it.

    Steps:
        1. Build a max-heap                      -> O(n)
        2. Repeat n-1 times:
             swap root (max) with last heap slot
             shrink heap by one
             max_heapify(root)                   -> O(log n) each
    Total: O(n log n) in best, average and worst case. Space O(1).
    Not stable.
    """
    n = len(a)
    build_max_heap(a, key)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        max_heapify(a, end, 0, key)
    return a


if __name__ == "__main__":
    data = [12, 3, 19, 7, 1, 25, 8]
    print("before:", data)
    print("after :", heapsort(data))
