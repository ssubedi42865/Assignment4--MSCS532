# Assignment 4: Heap Data Structures

Heapsort and an array-based binary-heap priority queue, with a task-scheduler
simulation and an empirical sorting benchmark. Pure Python 3.8+, standard
library only.

## Files

| File | Purpose |
|------|---------|
| `heapsort.py` | In-place Heapsort (`max_heapify`, `build_max_heap`, `heapsort`) |
| `priority_queue.py` | `Task` dataclass and `PriorityQueue` (binary max-heap with position map) |
| `scheduler_sim.py` | Preemptive priority scheduler with optional aging, plus FIFO baseline |
| `benchmark.py` | Quicksort, Merge Sort, and the timing harness (writes `benchmark_results.csv`) |
| `test_heap.py` | 14 unit tests |
| `HeapDataStructures_MSCS532.docx` | Full report: design, analysis, results |
| `benchmark_results.csv`, `benchmark_chart.png` | Benchmark output used in the report |

## How to run

```bash
python heapsort.py                 # small Heapsort demo
python -m unittest -v test_heap    # run all tests (14 tests, all pass)
python scheduler_sim.py            # scheduler demo + 200-task random workload
python benchmark.py                # sorting benchmark, about a minute
```

## Using the priority queue

```python
from priority_queue import PriorityQueue, Task

pq = PriorityQueue()
pq.insert(Task(task_id=1, priority=5, arrival_time=0, burst_time=3))
pq.insert(Task(task_id=2, priority=9, arrival_time=1, burst_time=2))
pq.increase_key(1, 10)      # raise priority of task 1
top = pq.extract_max()      # -> task 1 (priority 10)
pq.is_empty()               # False
```

Highest priority number is served first. Ties go to the earlier arrival time,
then the smaller task id. A task-id to heap-index map makes `increase_key` and
`decrease_key` O(log n).

## Complexity summary

| Operation | Time |
|-----------|------|
| Heapsort (all cases, distinct keys) | Theta(n log n), O(1) extra space, not stable |
| build_max_heap | O(n) |
| insert | O(log n) worst, O(1) expected for random priorities |
| extract_max | O(log n) |
| increase_key / decrease_key | O(log n) |
| peek / is_empty | O(1) |

## Summary of findings

**Sorting benchmark** (pure Python, best of 3, n = 50,000):

| Input | Heapsort | Quicksort | Merge sort |
|-------|----------|-----------|------------|
| random | 0.180 s | 0.071 s | 0.095 s |
| sorted | 0.149 s | 0.062 s | 0.068 s |
| reverse | 0.142 s | 0.063 s | 0.067 s |
| 10 distinct values | 0.133 s | 2.692 s | 0.073 s |

- Heapsort's time barely depends on input order, matching its Theta(n log n)
  bound for distinct keys. All-equal input takes linear time in this implementation.
- On random data it is about 2.6x slower than Quicksort and 1.9x slower than
  Merge Sort in this run; individual sources of overhead were not measured.
- Quicksort (Lomuto partition, random pivot) becomes roughly quadratic with many
  duplicate keys; Heapsort's guarantee avoids this.

**Scheduler** (200 random tasks, about 88% load):

| Policy | Avg wait | Max wait | High-priority avg wait | Low-priority avg wait |
|--------|----------|----------|------------------------|-----------------------|
| Priority | 6.52 | 89 | 0.17 | 18.00 |
| Priority + aging | 6.20 | 58 | 0.17 | 14.21 |
| FIFO | 5.32 | 22 | 4.67 | 5.40 |

- Priority scheduling gives urgent tasks near-zero waiting but delays
  low-priority work (starvation tendency).
- Aging reduces the worst-case wait at some cost to mid-priority tasks.
- On the small hand-built workload, priority scheduling met 6 of 6 deadlines
  versus 3 of 6 for FIFO.

See `HeapDataStructures_MSCS532.docx` for the full analysis.
