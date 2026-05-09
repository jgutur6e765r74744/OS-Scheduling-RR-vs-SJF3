import tkinter as tk
from tkinter import messagebox, ttk
from scheduling import (
    build_processes, run_round_robin, run_sjf, merge_gantt
)
from matrices import calculate_metrics, get_average
from models import SCENARIOS


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS CPU Scheduling Project")
        self.root.geometry("950x850")
        self.root.configure(bg="#ecf0f1")

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

        scenario_frame = tk.Frame(root, bg="#ecf0f1")
        scenario_frame.pack(pady=10)

        tk.Label(scenario_frame, text="Load Scenario:", fg="#2c3e50", bg="#ecf0f1",
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 8))

        tk.Button(scenario_frame, text="Scenario 1", command=lambda: self.load_scenario("Scenario 1"),
                  bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=14).grid(row=1, column=0, padx=6)
        tk.Button(scenario_frame, text="Scenario 2", command=lambda: self.load_scenario("Scenario 2"),
                  bg="#16a085", fg="white", font=("Arial", 10, "bold"), width=14).grid(row=1, column=1, padx=6)
        tk.Button(scenario_frame, text="Scenario 3", command=lambda: self.load_scenario("Scenario 3"),
                  bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=14).grid(row=1, column=2, padx=6)

        self.loaded_tree = self.create_process_table("Loaded Scenario Processes", ("PID", "Arrival", "Burst"))
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

    def create_process_table(self, title, cols):
        tk.Label(self.root, text=title, fg="#34495e", bg="#ecf0f1",
                 font=("Arial", 12, "bold")).pack(pady=(10, 5))

        table = ttk.Treeview(self.root, columns=cols, show="headings", height=4)
        for c in cols:
            table.heading(c, text=c)
            table.column(c, width=120, anchor="center")

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
            self.update_process_table()
            self.entry_pid.delete(0, tk.END)
            self.entry_arr.delete(0, tk.END)
            self.entry_brs.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Format Error", "Please enter valid integers for Arrival and Burst.")

    def load_scenario(self, scenario_name):
        scenario = SCENARIOS.get(scenario_name)
        if not scenario:
            return messagebox.showerror("Error", "Unknown scenario selected.")

        self.clear_all()
        self.processes_data = [p.copy() for p in scenario["processes"]]
        self.entry_qnt.delete(0, tk.END)
        self.entry_qnt.insert(0, str(scenario["quantum"]))
        self.update_process_table()

        if self.processes_data:
            first = self.processes_data[0]
            self.entry_pid.delete(0, tk.END)
            self.entry_arr.delete(0, tk.END)
            self.entry_brs.delete(0, tk.END)
            self.entry_pid.insert(0, first["pid"])
            self.entry_arr.insert(0, str(first["arrival"]))
            self.entry_brs.insert(0, str(first["burst"]))

    def clear_all(self):
        self.processes_data.clear()
        self.rr_avg_res = None
        self.sjf_avg_res = None
        for table in [self.tree_rr, self.tree_sjf, self.tree_comp, self.loaded_tree]:
            for item in table.get_children():
                table.delete(item)

    def update_table(self, table, data):
        for i in table.get_children(): table.delete(i)
        for row in data:
            formatted_row = [row[0]] + [f"{val:.2f}" if isinstance(val, float) else val for val in row[1:]]
            table.insert("", "end", values=formatted_row)

    def update_process_table(self):
        for i in self.loaded_tree.get_children():
            self.loaded_tree.delete(i)
        for p in self.processes_data:
            self.loaded_tree.insert("", "end", values=(p["pid"], p["arrival"], p["burst"]))

    def validate_processes(self):
        if not self.processes_data:
            return "Add processes first!"

        seen = set()
        for p in self.processes_data:
            pid = str(p.get("pid", "")).strip()
            if not pid:
                return "Process ID cannot be empty."
            if pid in seen:
                return f"Duplicate Process ID found: {pid}."
            seen.add(pid)

            arrival = p.get("arrival")
            burst = p.get("burst")
            if not isinstance(arrival, int) or arrival < 0:
                return "Arrival time must be a non-negative integer."
            if not isinstance(burst, int) or burst <= 0:
                return "Burst time must be a positive integer."
        return None

    def start_sim(self):
        validation_error = self.validate_processes()
        if validation_error:
            return messagebox.showerror("Invalid Input", validation_error)

        try:
            q = int(self.entry_qnt.get())
            if q <= 0:
                return messagebox.showerror("Error", "Quantum must be > 0.")
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

        from main import draw_gantt, draw_comparison_chart
        draw_gantt(gantt_rr, f"Round Robin Scheduling (Quantum = {q})")
        draw_gantt(gantt_sjf, "SJF (Preemptive) Scheduling")
        draw_comparison_chart(self.rr_avg_res, self.sjf_avg_res)

    def export_data(self):
        if not self.rr_avg_res:
            return messagebox.showinfo("Tip", "Run simulation first before exporting.")
        from main import export_pdf
        export_pdf(self.rr_avg_res, self.sjf_avg_res, self.processes_data)
        messagebox.showinfo("Exported", "Report saved successfully as 'Scheduling_Comparison_Report.pdf'.")
