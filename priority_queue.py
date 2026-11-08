"""Binary-heap priority queue for task scheduling.

Design:
  * Binary MAX-heap stored in a Python list (array representation).
  * Highest priority number is served first.
  * Ties are broken by earlier arrival time, then by smaller task id
    (so equal-priority tasks are served FIFO, which avoids arbitrary order).
  * A dict maps task_id -> heap index so that increase_key / decrease_key
    can locate a task in O(1) instead of scanning in O(n).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Task:
    task_id: int
    priority: int
    arrival_time: int = 0
    deadline: Optional[int] = None
    burst_time: int = 1          # CPU time needed (used by the scheduler simulation)
    name: str = ""
    remaining: int = field(init=False)

    def __post_init__(self):
        self.remaining = self.burst_time

    def __repr__(self) -> str:
        return (f"Task(id={self.task_id}, prio={self.priority}, "
                f"arr={self.arrival_time}, dl={self.deadline}, burst={self.burst_time})")


def _before(a: Task, b: Task) -> bool:
    """True if task a should be served before task b."""
    if a.priority != b.priority:
        return a.priority > b.priority
    if a.arrival_time != b.arrival_time:
        return a.arrival_time < b.arrival_time
    return a.task_id < b.task_id


class PriorityQueue:
    """Max-priority queue implemented as an array-based binary heap."""

    def __init__(self) -> None:
        self._heap: List[Task] = []
        self._pos: Dict[int, int] = {}   # task_id -> index in _heap

    # ---------- helpers ----------
    def __len__(self) -> int:
        return len(self._heap)

    def __contains__(self, task_id: int) -> bool:
        return task_id in self._pos

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int) -> None:
        h = self._heap
        h[i], h[j] = h[j], h[i]
        self._pos[h[i].task_id] = i
        self._pos[h[j].task_id] = j

    def _sift_up(self, i: int) -> None:
        while i > 0:
            p = self._parent(i)
            if _before(self._heap[i], self._heap[p]):
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._heap)
        while True:
            l, r, best = self._left(i), self._right(i), i
            if l < n and _before(self._heap[l], self._heap[best]):
                best = l
            if r < n and _before(self._heap[r], self._heap[best]):
                best = r
            if best == i:
                return
            self._swap(i, best)
            i = best

    # ---------- public API ----------
    def is_empty(self) -> bool:
        """O(1)."""
        return not self._heap

    def peek(self) -> Task:
        """Return (without removing) the highest priority task. O(1)."""
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0]

    def insert(self, task: Task) -> None:
        """Add a task. Append at the end, then sift up.

        Time: O(log n) worst case (height of the heap), O(1) average for
        random priorities. Space: O(1) extra.
        """
        if task.task_id in self._pos:
            raise ValueError(f"task id {task.task_id} already in queue")
        self._heap.append(task)
        idx = len(self._heap) - 1
        self._pos[task.task_id] = idx
        self._sift_up(idx)

    def extract_max(self) -> Task:
        """Remove and return the highest priority task.

        Move last element to the root, shrink, sift down.
        Time: O(log n). Space: O(1) extra.
        """
        if not self._heap:
            raise IndexError("extract_max from empty priority queue")
        top = self._heap[0]
        last = self._heap.pop()
        del self._pos[top.task_id]
        if self._heap:
            self._heap[0] = last
            self._pos[last.task_id] = 0
            self._sift_down(0)
        return top

    def change_priority(self, task_id: int, new_priority: int) -> None:
        """Change a task's priority and restore the heap property.

        Time: O(1) to locate (position map) + O(log n) to sift.
        Without the map, locating the task would cost O(n).
        """
        if task_id not in self._pos:
            raise KeyError(f"task id {task_id} not in queue")
        i = self._pos[task_id]
        task = self._heap[i]
        old = task.priority
        task.priority = new_priority
        if new_priority > old:
            self._sift_up(i)
        elif new_priority < old:
            self._sift_down(i)

    def increase_key(self, task_id: int, new_priority: int) -> None:
        """Raise a task's priority (new value must not be lower). O(log n)."""
        i = self._pos.get(task_id)
        if i is None:
            raise KeyError(f"task id {task_id} not in queue")
        if new_priority < self._heap[i].priority:
            raise ValueError("new priority is lower than current priority")
        self.change_priority(task_id, new_priority)

    def decrease_key(self, task_id: int, new_priority: int) -> None:
        """Lower a task's priority (new value must not be higher). O(log n)."""
        i = self._pos.get(task_id)
        if i is None:
            raise KeyError(f"task id {task_id} not in queue")
        if new_priority > self._heap[i].priority:
            raise ValueError("new priority is higher than current priority")
        self.change_priority(task_id, new_priority)

    def is_valid_heap(self) -> bool:
        """Debug helper: verify heap order and position map. O(n)."""
        for i in range(1, len(self._heap)):
            if _before(self._heap[i], self._heap[self._parent(i)]):
                return False
        return all(self._heap[i].task_id == t for t, i in self._pos.items()) \
            and len(self._pos) == len(self._heap)
