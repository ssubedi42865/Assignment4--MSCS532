"""Empirical comparison of Heapsort, Quicksort and Merge Sort.

Quicksort: randomized pivot, in place (Lomuto partition with random pivot,
           three-way handling avoided for simplicity; recursion on smaller side
           first to keep stack depth O(log n)).
Merge sort: top-down, uses an auxiliary buffer.
All three are pure Python so the comparison is like-for-like.
Python's built-in sorted() is timed as a reference only.
"""

import csv
import random
import sys
import time
from typing import Callable, Dict, List

from heapsort import heapsort

sys.setrecursionlimit(10000)


def quicksort(a: List[int]) -> List[int]:
    rnd = random.Random(12345)

    def partition(lo: int, hi: int) -> int:
        p = rnd.randint(lo, hi)
        a[p], a[hi] = a[hi], a[p]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        return i

    def qs(lo: int, hi: int) -> None:
        while lo < hi:
            p = partition(lo, hi)
            if p - lo < hi - p:
                qs(lo, p - 1)
                lo = p + 1
            else:
                qs(p + 1, hi)
                hi = p - 1

    qs(0, len(a) - 1)
    return a


def merge_sort(a: List[int]) -> List[int]:
    buf = a[:]

    def ms(lo: int, hi: int) -> None:  # sorts a[lo:hi]
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        ms(lo, mid)
        ms(mid, hi)
        i, j, k = lo, mid, lo
        while i < mid and j < hi:
            if a[i] <= a[j]:
                buf[k] = a[i]; i += 1
            else:
                buf[k] = a[j]; j += 1
            k += 1
        while i < mid:
            buf[k] = a[i]; i += 1; k += 1
        while j < hi:
            buf[k] = a[j]; j += 1; k += 1
        a[lo:hi] = buf[lo:hi]

    ms(0, len(a))
    return a


def make_data(kind: str, n: int, seed: int = 7) -> List[int]:
    rnd = random.Random(seed)
    if kind == "random":
        return [rnd.randint(0, n * 10) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "few_unique":
        return [rnd.randint(0, 9) for _ in range(n)]
    raise ValueError(kind)


ALGOS: Dict[str, Callable] = {
    "heapsort": heapsort,
    "quicksort": quicksort,
    "mergesort": merge_sort,
    "builtin_sorted": lambda a: a.sort() or a,
}


def time_once(fn: Callable, data: List[int]) -> float:
    a = data[:]
    t0 = time.perf_counter()
    out = fn(a)
    dt = time.perf_counter() - t0
    assert out == sorted(data), "sort produced wrong result"
    return dt


def run(sizes=(1000, 5000, 10000, 50000), kinds=("random", "sorted", "reverse", "few_unique"),
        repeats: int = 3, out_csv: str = "benchmark_results.csv") -> List[dict]:
    rows = []
    for kind in kinds:
        for n in sizes:
            data = make_data(kind, n)
            for name, fn in ALGOS.items():
                best = min(time_once(fn, data) for _ in range(repeats))
                rows.append({"distribution": kind, "n": n, "algorithm": name,
                             "seconds": round(best, 5)})
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["distribution", "n", "algorithm", "seconds"])
        w.writeheader()
        w.writerows(rows)
    return rows


def print_table(rows: List[dict]) -> None:
    kinds = sorted({r["distribution"] for r in rows}, key=lambda k: ["random", "sorted", "reverse", "few_unique"].index(k))
    sizes = sorted({r["n"] for r in rows})
    algos = list(ALGOS)
    for kind in kinds:
        print(f"\n[{kind}]  best of 3 runs, seconds")
        print(f"{'n':>8} " + " ".join(f"{a:>15}" for a in algos))
        for n in sizes:
            vals = {r["algorithm"]: r["seconds"] for r in rows if r["distribution"] == kind and r["n"] == n}
            print(f"{n:>8} " + " ".join(f"{vals[a]:>15.5f}" for a in algos))


if __name__ == "__main__":
    rows = run()
    print_table(rows)
    print("\nSaved benchmark_results.csv")
