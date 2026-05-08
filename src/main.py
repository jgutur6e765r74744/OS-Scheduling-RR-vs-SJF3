import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from collections import deque
from fpdf import FPDF

# ================= PROCESS CLASS =================
class Process:
    def __init__(self, pid, arrival, burst):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start_time = -1
        self.completion = 0

# ================= HELPER FUNCTIONS =================
def build_processes(raw_data):
    return [Process(p["pid"], p["arrival"], p["burst"]) for p in raw_data]

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

# ================= ROUND ROBIN ALGORITHM =================
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

# ================= SJF (PREEMPTIVE) ALGORITHM =================
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

# ================= CHARTS & VISUALIZATION =================
def draw_gantt(gantt, title):
    fig, ax = plt.subplots(figsize=(9, 3))
    
    unique_pids = list(set([item[0] for item in gantt]))
    colors = list(mcolors.TABLEAU_COLORS.values())
    color_map = {pid: colors[i % len(colors)] for i, pid in enumerate(unique_pids)}

    y_level = 10
    height = 5
    xticks = set([0])

    for pid, start, end in gantt:
        ax.broken_barh([(start, end - start)], (y_level, height), 
                       facecolors=color_map[pid], edgecolor='black', linewidth=1.2)
        ax.text(start + (end - start)/2, y_level + height/2, pid, 
                ha='center', va='center', fontweight='bold', color='white', fontsize=10)
        xticks.add(start)
        xticks.add(end)

    ax.set_ylim(5, 20)
    ax.set_xlim(0, max(xticks) + 1 if xticks else 10)
    ax.set_xlabel('Time (Units)', fontweight='bold')
    ax.set_title(title, fontweight='bold', color='#333')
    ax.set_yticks([]) 
    
    ax.set_xticks(sorted(list(xticks)))
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    plt.show()

def draw_comparison_chart(rr_avg, sjf_avg):
    labels = ['Avg Waiting Time', 'Avg Turnaround Time', 'Avg Response Time']
    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 4))
    
    ax.bar([pos - width/2 for pos in x], rr_avg, width, label='Round Robin', color='#3498db', edgecolor='black')
    ax.bar([pos + width/2 for pos in x], sjf_avg, width, label='SJF (Preemptive)', color='#e74c3c', edgecolor='black')

    ax.set_ylabel('Time (Units)', fontweight='bold')
    ax.set_title('Performance Comparison: RR vs SJF', fontweight='bold')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontweight='bold')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

# ================= PDF EXPORT =================
def export_pdf(rr_avg, sjf_avg, raw_processes):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(200, 10, "OS Scheduling Comparison Report", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. Input Processes:", ln=True)
    pdf.set_font("Arial", '', 12)
    for p in raw_processes:
        pdf.cell(200, 8, f"PID: {p['pid']} | Arrival: {p['arrival']} | Burst: {p['burst']}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "2. Final Comparison (Averages):", ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Algorithm", border=1, align='C')
    pdf.cell(45, 10, "Avg Waiting", border=1, align='C')
    pdf.cell(45, 10, "Avg Turnaround", border=1, align='C')
    pdf.cell(45, 10, "Avg Response", border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", '', 12)
    pdf.cell(50, 10, "Round Robin", border=1, align='C')
    pdf.cell(45, 10, f"{rr_avg[0]:.2f}", border=1, align='C')
    pdf.cell(45, 10, f"{rr_avg[1]:.2f}", border=1, align='C')
    pdf.cell(45, 10, f"{rr_avg[2]:.2f}", border=1, align='C')
    pdf.ln()

    pdf.cell(50, 10, "SJF", border=1, align='C')
    pdf.cell(45, 10, f"{sjf_avg[0]:.2f}", border=1, align='C')
    pdf.cell(45, 10, f"{sjf_avg[1]:.2f}", border=1, align='C')
    pdf.cell(45, 10, f"{sjf_avg[2]:.2f}", border=1, align='C')
    
    pdf.output("Scheduling_Comparison_Report.pdf")

# ================= GUI APP =================
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS CPU Scheduling Project")
        self.root.geometry("950x850")
        self.root.configure(bg="#ecf0f1") # لون فاتح ومريح للعين

        self.processes_data = []
        self.rr_avg_res = None
        self.sjf_avg_res = None

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=('Arial', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'), background="#bdc3c7")

        tk.Label(root, text="Round Robin vs SJF Simulator",
                 font=("Arial", 18, "bold"), fg="#2c3e50", bg="#ecf0f1").pack(pady=15)

        input_frame = tk.Frame(root, bg="#ecf0f1")
        input_frame.pack(pady=10)

        self.entry_pid = self.create_input(input_frame, "Process ID:", 0)
        self.entry_arr = self.create_input(input_frame, "Arrival Time:", 1)
        self.entry_brs = self.create_input(input_frame, "Burst Time:", 2)
        self.entry_qnt = self.create_input(input_frame, "RR Quantum:", 3)

        btn_frame = tk.Frame(root, bg="#ecf0f1")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Process", command=self.add_process,
                  bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=0, padx=8)

        tk.Button(btn_frame, text="Run Simulation", command=self.start_sim,
                  bg="#2980b9", fg="white", font=("Arial", 11, "bold"), width=15).grid(row=0, column=1, padx=8)

        tk.Button(btn_frame, text="Export PDF", command=self.export_data,
                  bg="#8e44ad", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=2, padx=8)

        tk.Button(btn_frame, text="Clear Data", command=self.clear_all,
                  bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=12).grid(row=0, column=3, padx=8)

        self.tree_rr = self.create_table("Round Robin Details")
        self.tree_sjf = self.create_table("SJF Details")
        self.tree_comp = self.create_table("Final Average Comparison", comparison=True)

    def create_input(self, parent, label_text, col):
        frame = tk.Frame(parent, bg="#ecf0f1")
        frame.grid(row=0, column=col, padx=10)
        tk.Label(frame, text=label_text, fg="#2c3e50", bg="#ecf0f1", font=("Arial", 10, "bold")).pack()
        e = tk.Entry(frame, font=("Arial", 11), width=12, justify="center")
        e.pack(pady=5)
        return e

    def create_table(self, title, comparison=False):
        tk.Label(self.root, text=title, fg="#34495e", bg="#ecf0f1",
                 font=("Arial", 12, "bold")).pack(pady=(10, 5))

        cols = ("Algorithm", "Avg WT", "Avg TAT", "Avg RT") if comparison else ("PID", "WT", "TAT", "RT")
        table = ttk.Treeview(self.root, columns=cols, show="headings", height=4 if comparison else 5)

        for c in cols:
            table.heading(c, text=c)
            table.column(c, width=170, anchor="center")

        table.pack()
        return table

    def add_process(self):
        try:
            pid = self.entry_pid.get().strip()
            if not pid: return messagebox.showwarning("Missing Data", "Process ID cannot be empty.")
            
            arr = int(self.entry_arr.get())
            brs = int(self.entry_brs.get())

            if arr < 0 or brs <= 0:
                return messagebox.showerror("Invalid Input", "Arrival must be >= 0 and Burst must be > 0.")
            if any(p["pid"] == pid for p in self.processes_data):
                return messagebox.showerror("Duplicate", "Process ID already exists.")

            self.processes_data.append({"pid": pid, "arrival": arr, "burst": brs})
            
            self.entry_pid.delete(0, tk.END)
            self.entry_arr.delete(0, tk.END)
            self.entry_brs.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Format Error", "Please enter valid integers for Arrival and Burst.")

    def clear_all(self):
        self.processes_data.clear()
        for table in [self.tree_rr, self.tree_sjf, self.tree_comp]:
            for item in table.get_children():
                table.delete(item)

    def update_table(self, table, data):
        for i in table.get_children(): table.delete(i)
        for row in data:
            formatted_row = [row[0]] + [f"{val:.2f}" if isinstance(val, float) else val for val in row[1:]]
            table.insert("", "end", values=formatted_row)

    def start_sim(self):
        if not self.processes_data:
            return messagebox.showwarning("Wait", "Add processes first!")
        try:
            q = int(self.entry_qnt.get())
            if q <= 0: return messagebox.showerror("Error", "Quantum must be > 0.")
        except ValueError:
            return messagebox.showerror("Error", "Enter a valid Quantum integer.")

        rr_procs = build_processes(self.processes_data)
        sjf_procs = build_processes(self.processes_data)

        gantt_rr = run_round_robin(rr_procs, q)
        gantt_sjf = merge_gantt(run_sjf(sjf_procs))

        metrics_rr = calculate_metrics(rr_procs)
        metrics_sjf = calculate_metrics(sjf_procs)

        self.rr_avg_res = get_average(metrics_rr)
        self.sjf_avg_res = get_average(metrics_sjf)

        self.update_table(self.tree_rr, metrics_rr)
        self.update_table(self.tree_sjf, metrics_sjf)

        comp_data = [
            ("Round Robin", *self.rr_avg_res),
            ("SJF", *self.sjf_avg_res)
        ]
        self.update_table(self.tree_comp, comp_data)

        draw_gantt(gantt_rr, f"Round Robin Scheduling (Quantum = {q})")
        draw_gantt(gantt_sjf, "SJF (Preemptive) Scheduling")
        
        # استدعاء جراف المقارنة هنا 🔥
        draw_comparison_chart(self.rr_avg_res, self.sjf_avg_res)

    def export_data(self):
        if not self.rr_avg_res:
            return messagebox.showinfo("Tip", "Run simulation first before exporting.")
        export_pdf(self.rr_avg_res, self.sjf_avg_res, self.processes_data)
        messagebox.showinfo("Exported", "Report saved successfully as 'Scheduling_Comparison_Report.pdf'.")

# ================= RUN PROGRAM =================
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()