class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = -1
        self.completion = 0


SCENARIOS = {
    "Scenario 1": {
        "quantum": 2,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 7},
            {"pid": "P2", "arrival": 1, "burst": 3},
            {"pid": "P3", "arrival": 2, "burst": 8},
            {"pid": "P4", "arrival": 5, "burst": 2},
        ],
    },
    "Scenario 2": {
        "quantum": 4,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": 20},
            {"pid": "P2", "arrival": 1, "burst": 2},
            {"pid": "P3", "arrival": 2, "burst": 2},
        ],
    },
    "Scenario 3": {
        "quantum": 0,
        "processes": [
            {"pid": "P1", "arrival": 0, "burst": -5},
            {"pid": "", "arrival": 1, "burst": 3},
        ],
    },
}
