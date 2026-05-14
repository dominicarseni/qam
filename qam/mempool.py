import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt
import math

class MemPool:
    
    def __init__(self, qCount):

        if not isinstance(qCount, int) or qCount <= 0:
            raise ValueError("Qubit count must be a positive integer!")
        
        self.records = []
        self.qubitCount = qCount
        self.maxVal = 2**self.qubitCount - 1
        self.recordCount = 0
        self.state = None

        self.dev = qml.device("default.qubit", wires = self.qubitCount)
    
    def addRecords(self, inputs):

        self._checkInputs(inputs)

        self.records = sorted(set(self.records + inputs))
        self._buildState()

    def removeRecords(self, inputs):
        self._checkInputs(inputs)

        self.records = sorted([rec for rec in self.records if rec not in inputs])
        self.buildState()

    def clear(self):
        self.records = []
        self.state = None

    def printState(self):
        if self.state is None:
            raise ValueError("No records stored!")
        
        print(self.circuit())

    def displayCircuit(self):
        if self.state is None:
            raise ValueError("No records stored!")
        
        decomp = qml.transforms.decompose(self.prepCircuit)
        fig, ax = qml.draw_mpl(decomp)()
        plt.show()

    def getCircuit(self, wires = None):

        if self.state is None:
            raise ValueError("No records stored!")
        
        if self.state is None:
            raise ValueError("No records stored!")
        
        if wires is None:
            wires = range(self.qubitCount)

        qml.StatePrep(self.state, wires = wires)

    def _checkInputs(self, inputs):

        if inputs is None: raise ValueError("Input cannot be null!")
        if len(inputs) == 0: raise ValueError("No records were given!")

        for rec in inputs:
            if not isinstance(rec, int): 
                raise ValueError("All records must be positive integers!")
            
            if rec < 0 or rec > self.maxVal: 
                raise ValueError(f"Inputs must be between 0 and {self.maxVal}!")
        
    def _buildState(self):
        
        if len(self.records) == 0: 
            self.state = None
            return
        
        self.state = np.zeros(self.maxVal + 1, dtype = complex)

        amp = 1 / np.sqrt(len(self.records))
    
        for rec in self.records:
            self.state[rec] = amp

    
    def _buildCircuit(self):
        @qml.qnode(self.dev)
        def circuit():
            qml.StatePrep(self._buildState(), wires=range(self.qubitCount))
            return qml.state()
        
        self.circuit = circuit
    
    