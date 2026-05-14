import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .qam import QAM

class QAMGUI:
    
    def __init__(self, root):
        self.root = root
        self.qam = None
        self.canvas = None

        self.root.geometry("900x600")
        self.root.title("Quantum Associative Memory")

        self.buildLayout()
        self.updateChart()

    #----------- Check for Valid Inputs -----------------
    
    def checkInt(self, input):
        return input == "" or input.isdigit()
    
    def checkRecordInput(self, input):
        return all(char.isdigit() or char in " ," for char in input)
    
    #--------------- Button Events ------------------------
    
    def add(self):
        if not self.makeQAM():
            return

        input = self.recordsEntry.get().strip()
        
        if input == "":
            return
        
        records = [int(x) for x in input.replace(",", " ").split()]
        self.qam.addRecords(records)

    def clear(self):
        if self.qam is not None:
            self.qam.clear()

        self.updateChart()

    def insert(self):
        if self.qam is None:
            self.makeQAM()

        runsInput = self.runsEntry.get().strip()
        keyInput = self.keyEntry.get().strip()

        if runsInput == "" or keyInput == "":
            messagebox.showerror("Input Error", "Specify both run count and key!")
            return
        
        runs = int(runsInput)
        key = int(keyInput)

        self.qam.key = key
        counts, best, discarded = self.qam.retrieve(runs)

        self.updateChart(counts)

    def resetPlot(self):
        self.updateChart()

    def makeQAM(self):
        qcInput = self.qubitCountEntry.get().strip()

        if qcInput == "":
            messagebox.showerror("Input Error", "Specify the qubit count!")
            return
        
        qCount = int(qcInput)

        if self.qam is None or qCount != self.qam.memQubitCount:
            self.qam = QAM(qCount)
            self.updateChart()
        
        return True

    #----------------- Build Layout --------------------

    def buildLayout(self):
        intCheck = self.root.register(self.checkInt)
        recCheck = self.root.register(self.checkRecordInput)

        self.leftFrame = tk.Frame(self.root)
        self.rightFrame = tk.Frame(self.root)

        self.leftFrame.grid(row = 0, column = 0, sticky = "nw", padx = 20, pady = 20)
        self.rightFrame.grid(row = 0, column = 1, sticky = "nsew", padx = 20, pady = 20)

        self.root.grid_columnconfigure(1, weight = 1)
        self.root.grid_rowconfigure(0, weight = 1)

        # Set Qubit Count Fields
        tk.Label(self.leftFrame, text = "QUBITS", font = ("calibre", 10, "bold")).grid(
            row = 0, column = 0, sticky = "w"
        )

        self.qubitCountEntry = tk.Entry(
            self.leftFrame,
            width = 30,
            validate = "key",
            validatecommand = (intCheck, "%P")
        )

        self.qubitCountEntry.grid(row = 1, column = 0, sticky = "w", pady = (0, 15))

        # Records
        tk.Label(self.leftFrame, text = "RECORDS", font = ("calibre", 10, "bold")).grid(
            row = 2, column = 0, sticky = "w"
        )

        self.recordsEntry = tk.Entry(
            self.leftFrame,
            width = 30,
            validate = "key",
            validatecommand = (recCheck, "%P")
        )

        self.recordsEntry.grid(row = 3, column = 0, sticky = "w")

        btnFrame = tk.Frame(self.leftFrame)
        btnFrame.grid(row = 4, column = 0, sticky = "e", pady = (5, 15))

        tk.Button(btnFrame, text = "Clear", command = self.clear).grid(
            row = 0, column = 0, padx = (0, 5)
        )

        tk.Button(btnFrame, text = "Add", command = self.add).grid(
            row = 0, column = 1
        )

        # Runs
        tk.Label(self.leftFrame, text = "RUNS", font = ("calibre", 10, "bold")).grid(
            row = 5, column = 0, sticky = "w"
        )

        self.runsEntry = tk.Entry(
            self.leftFrame,
            width = 30,
            validate = "key",
            validatecommand = (intCheck, "%P")
        )
        self.runsEntry.grid(row = 6, column = 0, sticky = "w", pady = (0, 15))

        # Key
        tk.Label(self.leftFrame, text = "KEY", font = ("calibre", 10, "bold")).grid(
            row = 7, column = 0, sticky = "w"
        )

        self.keyEntry = tk.Entry(
            self.leftFrame,
            width = 30,
            validate = "key",
            validatecommand = (intCheck, "%P")
        )

        self.keyEntry.grid(row = 8, column = 0, sticky = "w")

        actionFrame = tk.Frame(self.leftFrame)
        actionFrame.grid(row = 9, column = 0, sticky = "e", pady = (5, 0))

        tk.Button(actionFrame, text = "Insert", command = self.insert).grid(
            row = 0, column = 0, padx = (0, 5)
        )

        tk.Button(actionFrame, text = "Remove", command = self.resetPlot).grid(
            row = 0, column = 1,
        )

    # ----------------- Bar Chart ------------------

    def updateChart(self, counts = None):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()

        fig = Figure(figsize = (6, 5), dpi = 100)
        ax = fig.add_subplot(111)

        ax.set_title("Retrieval Results")
        ax.set_xlabel("Records")
        ax.set_ylabel("Times Measured")

        if counts is not None and self.qam is not None:
            labels = [format(rec, f"0{self.qam.memQubitCount}b")
                for rec in self.qam.memory.records
            ]
            
            ax.bar(labels, counts)
            ax.tick_params(axis = "x", rotation = 45)

        self.canvas = FigureCanvasTkAgg(fig, master = self.rightFrame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row = 0, column = 0, sticky = "nsew")
            
        





    
