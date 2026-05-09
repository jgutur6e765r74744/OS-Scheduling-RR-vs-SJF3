Round Robin vs SJF Comparison Project 

1:Project Description

This project is a CPU Scheduling Simulator built using Python and Tkinter GUI. It compares two scheduling algorithms: Round Robin (RR) and Preemptive Shortest Job First (SJF) using the same set of processes.

Users can input process details (ID, arrival time, burst time) and define a time quantum for Round Robin. The system then simulates both algorithms and evaluates their performance using key metrics: • Waiting Time (WT) • Turnaround Time (TAT) • Response Time (RT)

Results are displayed through tables and Gantt charts for visualization, along with a PDF report that summarizes the comparison between both algorithms

2:Project Requirements • Python 3.x • Tkinter (GUI) • Matplotlib (Charts + Gantt) • FPDF (PDF Report) • deque (for Round Robin queue)

Functional Requirements: • Add processes via GUI • Load test scenarios • Validate input data • Run Round Robin & Preemptive SJF • Display Gantt charts and metrics (WT, TAT, RT) • Show comparison results • Export PDF report 3: 



team members: 






4: Build Steps 1. Install Python 3.x on your system 2. Install required libraries using: pip install matplotlib fpdf 3. Download or clone the project files 4. Open the project in any Python IDE (VS Code / PyCharm / etc.)

5:Run the main file: python main.py 2. Open the GUI window 3. Add process details (ID, Arrival Time, Burst Time) 4. Enter the Round Robin quantum 5. Click Run Simulation 6. View Gantt charts, metrics, and comparison results 7. Click Export PDF to save the report,

6:Test Scenarios

Scenario 1 (Normal Case) • Multiple processes with different arrival and burst times • Quantum = 2

Scenario 2 (Edge Case) • One long process + multiple short processes • Tests fairness and starvation behavior

Scenario 3 (Invalid Input Case) • Negative burst time • Empty process ID • Invalid quantum value
