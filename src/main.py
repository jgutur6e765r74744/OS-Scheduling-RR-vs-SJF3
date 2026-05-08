import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from fpdf import FPDF
from gui import SchedulerApp

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




if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()