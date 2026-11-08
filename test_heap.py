"""Unit tests. Run with:  python -m unittest -v test_heap"""

import random
import unittest

from heapsort import heapsort, build_max_heap
from priority_queue import PriorityQueue, Task
from scheduler_sim import simulate, demo_tasks
from benchmark import quicksort, merge_sort


class TestHeapsort(unittest.TestCase):
    def test_empty_and_single(self):
        self.assertEqual(heapsort([]), [])
        self.assertEqual(heapsort([5]), [5])

    def test_random_against_sorted(self):
        rnd = random.Random(0)
        for _ in range(200):
            a = [rnd.randint(-50, 50) for _ in range(rnd.randint(0, 60))]
            self.assertEqual(heapsort(a[:]), sorted(a))

    def test_special_inputs(self):
        for a in ([1, 2, 3, 4], [4, 3, 2, 1], [7] * 10, [2, 1]):
            self.assertEqual(heapsort(a[:]), sorted(a))

    def test_key_function(self):
        words = ["pear", "fig", "banana", "kiwi"]
        self.assertEqual(heapsort(words, key=len), sorted(words, key=len))

    def test_build_max_heap_property(self):
        a = random.Random(1).sample(range(100), 40)
        build_max_heap(a)
        for i in range(1, len(a)):
            self.assertLessEqual(a[i], a[(i - 1) // 2])

    def test_other_sorts(self):
        a = random.Random(2).sample(range(1000), 300)
        self.assertEqual(quicksort(a[:]), sorted(a))
        self.assertEqual(merge_sort(a[:]), sorted(a))


class TestPriorityQueue(unittest.TestCase):
    def test_empty(self):
        pq = PriorityQueue()
        self.assertTrue(pq.is_empty())
        with self.assertRaises(IndexError):
            pq.extract_max()

    def test_order(self):
        pq = PriorityQueue()
        for i, p in enumerate([3, 9, 1, 7, 5], start=1):
            pq.insert(Task(i, p))
        self.assertTrue(pq.is_valid_heap())
        out = [pq.extract_max().priority for _ in range(5)]
        self.assertEqual(out, [9, 7, 5, 3, 1])

    def test_tie_break_fifo(self):
        pq = PriorityQueue()
        pq.insert(Task(1, 5, arrival_time=3))
        pq.insert(Task(2, 5, arrival_time=1))
        pq.insert(Task(3, 5, arrival_time=2))
        self.assertEqual([pq.extract_max().task_id for _ in range(3)], [2, 3, 1])

    def test_increase_decrease_key(self):
        pq = PriorityQueue()
        for i in range(1, 8):
            pq.insert(Task(i, i))
        pq.increase_key(1, 100)
        self.assertEqual(pq.peek().task_id, 1)
        pq.decrease_key(1, 0)
        self.assertEqual(pq.peek().task_id, 7)
        self.assertTrue(pq.is_valid_heap())
        with self.assertRaises(ValueError):
            pq.increase_key(2, -1)
        with self.assertRaises(KeyError):
            pq.increase_key(99, 1)

    def test_duplicate_id_rejected(self):
        pq = PriorityQueue()
        pq.insert(Task(1, 1))
        with self.assertRaises(ValueError):
            pq.insert(Task(1, 2))

    def test_randomized_against_reference(self):
        rnd = random.Random(3)
        pq, ref = PriorityQueue(), {}
        next_id = 0
        for _ in range(2000):
            op = rnd.random()
            if op < 0.5 or not ref:
                next_id += 1
                p = rnd.randint(0, 20)
                pq.insert(Task(next_id, p, arrival_time=next_id))
                ref[next_id] = p
            elif op < 0.75:
                t = pq.extract_max()
                best = max(ref.items(), key=lambda kv: (kv[1], -kv[0]))
                self.assertEqual((t.task_id, t.priority), best)
                del ref[t.task_id]
            else:
                tid = rnd.choice(list(ref))
                p = rnd.randint(0, 20)
                pq.change_priority(tid, p)
                ref[tid] = p
            self.assertTrue(pq.is_valid_heap())


class TestScheduler(unittest.TestCase):
    def test_all_tasks_finish_and_work_conserved(self):
        out = simulate(demo_tasks())
        self.assertEqual(len(out["results"]), 6)
        busy = sum(1 for x in out["timeline"] if x is not None)
        self.assertEqual(busy, sum(t.burst_time for t in demo_tasks()))

    def test_high_priority_preempts(self):
        out = simulate(demo_tasks())
        res = {r["id"]: r for r in out["results"]}
        # task 4 (prio 9, burst 2) arrives at 4 and should finish at 6
        self.assertEqual(res[4]["finish"], 6)


if __name__ == "__main__":
    unittest.main()
