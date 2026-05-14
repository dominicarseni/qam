import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .mempool import MemPool
import tkinter as tk

class QAM:

    def __init__(self, qCount, key = None):
        self.memory = MemPool(qCount)
        self.memQubitCount = qCount
        self.qubitCount = qCount + 1
        self.controlWire = qCount
        self.key = key
        self.dev = qml.device("default.qubit", wires = self.qubitCount)

    def setKey(self, key):
        if key < 0 or key > 2 ** self.memory.maxVal:
            raise ValueError(f"Key must be between 0 and {2 ** self.memQubitCount}!"
            )
        self.key = key
    
    def addRecords(self, inputs):
        self.memory.addRecords(inputs)

    def removeRecords(self, inputs):
        self.memory.removeRecords(inputs)

    def printInitState(self):
        self.memory.printState()
    
    def printFinalState(self):
        self._checkReady()
        print(self._finalStateCircuit()())

    def displayPrepCircuit(self):
        self.memory.displayCircuit()

    def displayRetrievalCircuit(self):
        self._checkReady()
        
        decomp = qml.transforms.decompose(
            self._retrievalOnly, 
            gate_set = {qml.RX, qml.RY, qml.RZ, qml.CNOT}
        )
        fig, ax = qml.draw_mpl(decomp)()
        plt.show()

    def retrieve(self, runs):
        self._checkReady()

        dev = qml.device("default.qubit", wires = self.qubitCount, shots = runs)

        @qml.qnode(dev)
        def circuit():
            self.memory.getCircuit(wires = range(self.memQubitCount))
            self._retrievalOnly()
            return qml.sample(wires = range(self.qubitCount))
        
        samples = circuit()

        counts = {rec: 0 for rec in self.memory.records}
        discarded = 0

        for sample in samples:
 
            control = int(sample[-1])

            if control == 1: 
                discarded += 1
                continue

            rec = int("".join(str(b) for b in sample[:-1]), 2)
        
            if rec in counts: counts[rec] += 1

        countsArray = np.array([counts[rec] for rec in self.memory.records])
        bestRecord = self.memory.records[int(np.argmax(countsArray))]

        print("\nRetrieval Results")
        print("-" * 32)
        print(f"{'Record':<12}{'Times Measured':>16}")
        print("-" * 32)

        for rec in self.memory.records:
            label = format(rec, f"0{self.memQubitCount}b")
            print(f"{label:<12}{counts[rec]:>16}")

        print("-" * 32)
        print(f"Most Frequently Measured : "
              f"{format(bestRecord, f'0{self.memQubitCount}b')}"
              )
        
        print(f"Discarded Measurements : {discarded}")



        return countsArray, bestRecord, discarded
    
    def clear(self):
        self.memory.clear()
    
    def printFinalState(self):
        self._checkReady()

        state = self._finalStateCircuit()()
        theta = np.pi / (2 * self.memQubitCount)

        print("\nRecord | Hamming Distance | Phase | Amplitude if Control = 0")
        print("-" * 65)

        for rec in self.memory.records:
            dist = self._getHammingDist(rec)
            phase = theta * dist
            amp = state[self._idx(rec, 0)]

            print(f"{rec:>6} | {dist:>16} | {phase:>7.4f} | {amp:>20.6}")

    #--------------------------------------------------------------------
    #                      PRIVATE HELPERS
    #--------------------------------------------------------------------

    def _finalStateCircuit(self):
        @qml.qnode(self.dev)

        def circuit():
            self.memory.getCircuit(wires = range(self.memQubitCount))
            self._retrievalOnly()
            return qml.state()
        
        return circuit
    
    def _retrievalOnly(self):
        qml.Hadamard(wires = self.controlWire)
        self._applyPhaseUnitary()
        qml.Hadamard(wires = self.controlWire)

    def _applyPhaseUnitary(self):
        theta = np.pi / (2 * self.memQubitCount)
        phases = np.ones(2 ** self.qubitCount, dtype = complex)

        for rec in self.memory.records:
            h = self._getHammingDist(rec)
            phases[rec << 1 | 0] = np.exp(1j * theta * h)
            phases[rec << 1 | 1] = np.exp(-1j * theta * h)

        qml.DiagonalQubitUnitary(phases, wires = range(self.qubitCount))

    def _checkReady(self):
        if self.key is None:
            raise ValueError("Set key first!")
        if len(self.memory.records) == 0:
            raise ValueError("No records stored!")
        
    def _getHammingDist(self, rec):
        return (self.key ^ rec).bit_count()
    