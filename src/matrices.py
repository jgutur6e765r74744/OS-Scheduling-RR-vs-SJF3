def calculate_metrics(processes):

    results = []
    for p in processes:
        tat = p.completion - p.arrival
        wt = tat - p.burst
        rt = (p.start_time - p.arrival) if p.start_time != -1 else 0
        results.append((p.pid, wt, tat, rt))
    return results


def get_average(metrics):
    if not metrics:
        return (0, 0, 0)
    n = len(metrics)
    return (
        sum(x[1] for x in metrics) / n,   
        sum(x[2] for x in metrics) / n,   
        sum(x[3] for x in metrics) / n,     
   )


def create_metrics_matrix(metrics):
    if not metrics:
        return []
    
    matrix = [["PID", "WT", "TAT", "RT"]]
    for pid, wt, tat, rt in metrics:
        matrix.append([pid, f"{wt:.2f}", f"{tat:.2f}", f"{rt:.2f}"])
    
    return matrix


def create_comparison_matrix(rr_metrics, sjf_metrics):
    rr_avg = get_average(rr_metrics)
    sjf_avg = get_average(sjf_metrics)
    
    comparison = [
        ["Algorithm", "Avg WT", "Avg TAT", "Avg RT"],
        ["Round Robin", f"{rr_avg[0]:.2f}", f"{rr_avg[1]:.2f}", f"{rr_avg[2]:.2f}"],
        ["SJF", f"{sjf_avg[0]:.2f}", f"{sjf_avg[1]:.2f}", f"{sjf_avg[2]:.2f}"]
    ]
    
    return comparison
