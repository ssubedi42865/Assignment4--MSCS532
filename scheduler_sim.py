"""Preemptive priority scheduler simulation built on PriorityQueue.

Policy: at every time unit the ready task with the highest priority runs.
A newly arrived higher-priority task preempts the running one.
Optional aging: every `aging_interval` time units, waiting tasks gain +1
priority (implemented with increase_key) to prevent starvation.

Metrics reported per task: waiting time, turnaround time, completion time,
and whether the deadline was met.
"""

import random
from typing import Dict, List, Optional

from priority_queue import PriorityQueue, Task


def simulate(tasks: List[Task], aging_interval: Optional[int] = None) -> Dict:
    pending = sorted(tasks, key=lambda t: (t.arrival_time, t.task_id))
    # work on copies so the caller's tasks are untouched
    pending = [Task(t.task_id, t.priority, t.arrival_time, t.deadline,
                    t.burst_time, t.name) for t in pending]
    original_priority = {t.task_id: t.priority for t in pending}
    arrival = {t.task_id: t.arrival_time for t in pending}
    burst = {t.task_id: t.burst_time for t in pending}

    pq = PriorityQueue()
    time, idx = 0, 0
    finish: Dict[int, int] = {}
    timeline: List[Optional[int]] = []
    preemptions = 0
    last_run: Optional[int] = None

    while idx < len(pending) or not pq.is_empty():
        while idx < len(pending) and pending[idx].arrival_time <= time:
            pq.insert(pending[idx])
            idx += 1
        if pq.is_empty():
            timeline.append(None)
            last_run = None
            time += 1
            continue

        current = pq.extract_max()
        if last_run is not None and last_run != current.task_id \
                and last_run not in finish:
            preemptions += 1
        last_run = current.task_id
        timeline.append(current.task_id)
        current.remaining -= 1
        time += 1

        if current.remaining == 0:
            finish[current.task_id] = time
        else:
            pq.insert(current)

        # aging: bump everyone still waiting
        if aging_interval and time % aging_interval == 0:
            for t in list(pq._heap):
                pq.increase_key(t.task_id, t.priority + 1)

    results = []
    for t in pending:
        tid = t.task_id
        turnaround = finish[tid] - arrival[tid]
        waiting = turnaround - burst[tid]
        met = None if t.deadline is None else finish[tid] <= t.deadline
        results.append({"id": tid, "priority": original_priority[tid],
                        "arrival": arrival[tid], "burst": burst[tid],
                        "finish": finish[tid], "waiting": waiting,
                        "turnaround": turnaround, "deadline_met": met})
    n = len(results)
    with_dl = [r for r in results if r["deadline_met"] is not None]
    summary = {
        "avg_waiting": sum(r["waiting"] for r in results) / n,
        "avg_turnaround": sum(r["turnaround"] for r in results) / n,
        "makespan": time,
        "preemptions": preemptions,
        "deadlines_met": sum(1 for r in with_dl if r["deadline_met"]),
        "deadline_tasks": len(with_dl),
        "max_waiting": max(r["waiting"] for r in results),
    }
    return {"results": results, "summary": summary, "timeline": timeline}


def fifo_baseline(tasks: List[Task]) -> Dict:
    """Non-preemptive first-come-first-served baseline for comparison."""
    ts = sorted(tasks, key=lambda t: (t.arrival_time, t.task_id))
    time, waits, turns, met, dl = 0, [], [], 0, 0
    results = []
    for t in ts:
        time = max(time, t.arrival_time) + t.burst_time
        turn = time - t.arrival_time
        turns.append(turn)
        waits.append(turn - t.burst_time)
        results.append({"id": t.task_id, "priority": t.priority, "waiting": turn - t.burst_time})
        if t.deadline is not None:
            dl += 1
            met += time <= t.deadline
    n = len(ts)
    return {"avg_waiting": sum(waits) / n, "avg_turnaround": sum(turns) / n,
            "makespan": time, "deadlines_met": met, "deadline_tasks": dl,
            "max_waiting": max(waits), "results": results}


def wait_by_class(results: List[Dict], low: int = 3, high: int = 8) -> Dict[str, float]:
    """Average waiting time for low (<=low), mid, and high (>=high) priority tasks."""
    groups = {"low (1-3)": [], "mid (4-7)": [], "high (8-10)": []}
    for r in results:
        p = r["priority"]
        key = "low (1-3)" if p <= low else ("high (8-10)" if p >= high else "mid (4-7)")
        groups[key].append(r["waiting"])
    return {k: (sum(v) / len(v) if v else float("nan")) for k, v in groups.items()}


def demo_tasks() -> List[Task]:
    """Small hand-made workload that is easy to follow in the report."""
    return [
        Task(1, priority=2, arrival_time=0, burst_time=6, deadline=20, name="backup"),
        Task(2, priority=5, arrival_time=1, burst_time=3, deadline=6,  name="alert"),
        Task(3, priority=3, arrival_time=2, burst_time=4, deadline=14, name="report"),
        Task(4, priority=9, arrival_time=4, burst_time=2, deadline=7,  name="security-patch"),
        Task(5, priority=1, arrival_time=5, burst_time=3, deadline=30, name="cleanup"),
        Task(6, priority=5, arrival_time=6, burst_time=2, deadline=12, name="notify"),
    ]


def random_workload(n: int, seed: int = 1) -> List[Task]:
    rnd = random.Random(seed)
    tasks, t = [], 0
    for i in range(1, n + 1):
        t += rnd.randint(2, 6)          # mean gap 4 vs mean burst 3.5 -> ~88% load
        burst = rnd.randint(1, 6)
        tasks.append(Task(i, priority=rnd.randint(1, 10), arrival_time=t,
                          burst_time=burst,
                          deadline=t + burst + rnd.randint(3, 40)))
    return tasks


def print_run(title: str, out: Dict) -> None:
    print(f"\n=== {title} ===")
    print(f"{'id':>3} {'prio':>4} {'arr':>3} {'burst':>5} {'finish':>6} "
          f"{'wait':>4} {'turn':>4} {'deadline':>8}")
    for r in out["results"]:
        dl = "-" if r["deadline_met"] is None else ("met" if r["deadline_met"] else "MISSED")
        print(f"{r['id']:>3} {r['priority']:>4} {r['arrival']:>3} {r['burst']:>5} "
              f"{r['finish']:>6} {r['waiting']:>4} {r['turnaround']:>4} {dl:>8}")
    s = out["summary"]
    print("summary:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()})
    tl = "".join("." if x is None else str(x) for x in out["timeline"])
    print("timeline (task id per time unit):", tl)


def main() -> None:
    tasks = demo_tasks()
    print_run("Priority scheduling (no aging)", simulate(tasks))
    print_run("Priority scheduling with aging every 4 units", simulate(tasks, aging_interval=4))
    f = fifo_baseline(tasks)
    print("\nFIFO baseline:", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in f.items()})

    print("\n=== Random workload comparison (200 tasks, seed 1) ===")
    big = random_workload(200)
    p_out = simulate(big)
    a_out = simulate(big, aging_interval=10)
    fb = fifo_baseline(big)
    for name, s in [("priority", p_out["summary"]), ("priority+aging", a_out["summary"]), ("fifo", fb)]:
        print(f"{name:>15}: avg_wait={s['avg_waiting']:.2f} avg_turn={s['avg_turnaround']:.2f} "
              f"max_wait={s['max_waiting']} deadlines={s['deadlines_met']}/{s['deadline_tasks']}")
    print("\nAverage waiting time by priority class:")
    for name, res in [("priority", p_out["results"]), ("priority+aging", a_out["results"]),
                      ("fifo", fb["results"])]:
        wc = wait_by_class(res)
        print(f"{name:>15}: " + "  ".join(f"{k}={v:.2f}" for k, v in wc.items()))


if __name__ == "__main__":
    main()
