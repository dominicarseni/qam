import pennylane as qml
import numpy as np
import math
from collections.abc import Iterable
class MemPool:

    """
    Internal memory pool implementation used by QAM. Not part of the public API, users interact with
    QAM and QAMGUI.
    
    Stores integers records as basis states in the computational basis
    in an equal superposition.
    """
    
    def __init__(self, qCount: int) -> None:
        """
        Initializes a memory pool object.

        Parameters
        ----------
        qCount : int
            Number of qubits used to store records.

        Raises
        ------
        ValueError
            If qCount is not a positive integer.
        """

        if not isinstance(qCount, int) or qCount <= 0:
            raise ValueError("Qubit count must be a positive integer!")
        
        self.records = []
        self.qubitCount = qCount
        self.maxVal = 2**self.qubitCount - 1
        self.recordCount = 0
        self.state = None

        self.dev = qml.device("default.qubit", wires = self.qubitCount)
    
    def addRecords(self, inputs: Iterable[int]) -> None:
        """
        Store records on the memory pool.

        Parameters
        ----------
        inputs: Iterable[int]
            Integer records to add.

        Raises
        ------
        TypeError
            If inputs is not an array or contains non-integers.
        ValueError
            If inputs is empty or contains values outside the all.
        ValueError
            If inputs is empty or contains values outside of allowed range.
        """
    
        records = self._checkInputs(inputs)
        self.records = sorted(set(self.records + records))
        self.recordCount = len(self.records)
        self._buildState()

    def removeRecords(self, inputs: Iterable[int]) -> None:
        """
        Remove records from the memory pool.

        Parameters
        ----------
        inputs : Iterable[int]
            Records to remove.

        Raises
        ------
        TypeError
            If inputs is not iterable or contains non-integers.
        ValueError
            If inputs is empty or contains values outside the allowed range.
        """
        records = self._checkInputs(inputs)

        self.records = sorted(
            [rec for rec in self.records if rec not in records]
        )

        self.recordCount = len(self.records)
        self._buildState()

    def clear(self) -> None:
        """
        Remove all records from memory pool and reset superposition.
        """
        self.records = []
        self.recordCount = 0
        self.state = None

    def printState(self) -> None:
        """
        Print the quantum state representing the memory pool.
        
        Raises
        ------
        ValueError
            If no records are stored.
        """
        if self.state is None:
            raise ValueError("No records stored!")
        
        print(self.state)

    def displayCircuit(self) -> None:
        import matplotlib.pyplot as plt
        """
        Display the circuit that prepares the state.

        Raises
        ------
        ValueError
            If there are no records in the memory pool.
        """

        if self.state is None:
            raise ValueError("No records stored!")
        
        @qml.qnode(self.dev)
        def prepCircuit() -> np.ndarray:
            qml.StatePrep(self.state, wires = range(self.qubitCount))
            return qml.state()
        
        decomp = qml.transforms.decompose(prepCircuit)
        fig, ax = qml.draw_mpl(decomp)()
        plt.show()
        
        

    def getCircuit(self, wires: Iterable[int] | None = None) -> None:
        """
        Make circuit that prepares quantum memory state.

        Parameters
        ----------
        wires : Iterable[int] | None, optional
            Wires on which to make the circuit. If None, uses memory pool's
            default wires.

        Raises
        ------
        ValueError
            If the memory pool contains no records.
        TypeError
            If wires parameter is not an arrray.
        ValueError
            If the number of wires is not equal to the number of memory qubits.
        """

        if self.state is None:
            raise ValueError("No records stored!")
        
        if wires is None:
            wires = range(self.qubitCount)

        wires = list(wires)

        if len(wires) != self.qubitCount:
            raise ValueError(
                f"Expected {self.qubitCount} wires, was {len(wires)}!"
            )
        
        qml.StatePrep(self.state, wires = wires)

    def _checkInputs(self, inputs: Iterable[int]) -> list[int]:
        """
        Check for valid input records.

        Parameters
        ----------
        inputs : Iterable[int]
            Candidate records.
        
        Returns
        ------
        list[int]
            Validated records as a list.

        Raises
        ------
        TypeError
            If inpts is not iterable or contains non-integers.
        ValueError
            If inputs is empty or contains values outside allowed range.
        """

        if isinstance(inputs, (str, bytes)):
            raise TypeError("Input must be an array of integers!")

        try:
            records = list(inputs)
        except TypeError as exc:
            raise TypeError("Input must be an array of integers!") from exc
        
        if len(records) == 0:
            raise ValueError("No records were given!")

        for rec in records:
            if not isinstance(rec, int):
                raise TypeError("All records must be integers!")
            
            if rec < 0 or rec > self.maxVal:
                raise ValueError(f"Inputs must be between 0 and {self.maxVal}!")

        return records
        
    def _buildState(self) -> None:
        """
        Build normalized memory state with stored records.
        """
        
        if len(self.records) == 0: 
            self.state = None
            return
        
        self.state = np.zeros(self.maxVal + 1, dtype = complex)

        amp = 1 / np.sqrt(len(self.records))
    
        for rec in self.records:
            self.state[rec] = amp

    
    def _buildCircuit(self) -> None:
        """
        Build QNode object that creates and returns memory state.
        """
        @qml.qnode(self.dev)
        def circuit():
            qml.StatePrep(self.state, wires=range(self.qubitCount))
            return qml.state()
        
        self.circuit = circuit
    
    