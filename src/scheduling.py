from collections import deque
from models import Process, SCENARIOS
from matrices import calculate_metrics, get_average


def build_processes(raw_data):
    return [Process(p["pid"], p["arrival"], p["burst"]) for p in raw_data]

def run_round_robin(processes, quantum):
    time = 0
    ready_queue = deque()
    gantt_chart = []
    processes.sort(key=lambda x: x.arrival)
    i = 0

    while i < len(processes) or ready_queue:
        while i < len(processes) and processes[i].arrival <= time:
            ready_queue.append(processes[i])
            i += 1

        if not ready_queue:
            time += 1
            continue

        current = ready_queue.popleft()
        if current.start_time == -1:
            current.start_time = time

        exec_time = min(quantum, current.remaining)
        gantt_chart.append((current.pid, time, time + exec_time))
        
        time += exec_time
        current.remaining -= exec_time

        while i < len(processes) and processes[i].arrival <= time:
            ready_queue.append(processes[i])
            i += 1

        if current.remaining > 0:
            ready_queue.append(current)
        else:
            current.completion = time

    return gantt_chart

def run_sjf(processes):
    time = 0
    gantt_chart = []
    while True:
        available = [p for p in processes if p.arrival <= time and p.remaining > 0]
        if not available:
            if all(p.remaining == 0 for p in processes):
                break
            time += 1
            continue

        current = min(available, key=lambda x: x.remaining)
        if current.start_time == -1:
            current.start_time = time

        gantt_chart.append((current.pid, time, time + 1))
        current.remaining -= 1
        time += 1

        if current.remaining == 0:
            current.completion = time

    return gantt_chart

def merge_gantt(gantt):
    merged = []
    for pid, start, end in gantt:
        if not merged:
            merged.append([pid, start, end])
        elif merged[-1][0] == pid and merged[-1][2] == start:
            merged[-1][2] = end 
        else:
            merged.append([pid, start, end])
    return merged
