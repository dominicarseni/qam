import pennylane as qml
import numpy as np
from collections.abc import Iterable
from ._mempool import MemPool

class QAM:
    """
    Quantum associative memory model using a memory pool object with wires
    for the records in memory and a control qubit register to enable phase operations/retrieval.
    """

    def __init__(self, qCount: int, key: int | None = None) -> None:
        """
        Initialize a QAM object.

        Parameters
        ----------
        qCount : int
            Number of qubits used to store memory state.
        key : int | None, optional
            key used for retrieval. If None, key must be set later.
        
        Raises
        ------
        TypeError
            If qCount is not an integer.
        ValueError
            If qCount is int but not positive.
        """
        if not isinstance(qCount, int):
            raise TypeError("Qubit count must be an integer!")
        
        if qCount <= 0:
            raise ValueError("Qubit count must be positive!")

        self.memory: MemPool = MemPool(qCount)
        self.memQubitCount: int = qCount
        self.qubitCount: int = qCount + 1
        self.controlWire: int = qCount
        self.key: int | None = None
        self.dev = qml.device("default.qubit", wires = self.qubitCount)

        if key is not None:
            self.setKey(key)

    def setKey(self, key : int) -> None:
        """
        Set key used for retrieval.

        Parameters
        ----------
        key : int
            Integer key used for retrieval.

        Raises
        ------
        TypeError
            If key is not an integer.
        ValueError
            If key is outside allowed range.
        """
        if not isinstance(key, int):
            raise TypeError("Key must be an integer!")

        if key < 0 or key > self.memory.maxVal:
            raise ValueError(f"Key must be between 0 and {self.memory.maxVal}!")
        self.key = key
    
    def addRecords(self, inputs: Iterable[int]) -> None:
        """
        Store records in memory pool.

        Parameters
        ----------
        inputs : Iterable[int]
            Integer records being stored.
        """
        self.memory.addRecords(inputs)

    def removeRecords(self, inputs: Iterable[int]) -> None:
        """
        Remove records from memory pool.

        Parameters
        ----------
        inputs : Iterable[int]
            Integer records being removed.
        """
        self.memory.removeRecords(inputs)
    
    def clear(self) -> None:
        """
        Clear all records from memory pool.
        """
        self.memory.clear()
    
    def printInitState(self) -> None:
        """
        Print the initial state in memory.
        """
        self.memory.printState()
    
    def printFinalStateData(self):
        """
        Print Hamming distances, phases, and final amplitudes for control = 0.

        Raises
        ------
        ValueError
            If key is not set or memory pool does not contain records.
        """
        self._checkReady()

        state = self._finalStateCircuit()()
        theta = np.pi / (2 * self.memQubitCount)

        print("\nRecord | Hamming Distance | Phase | Amplitude if Control = 0")
        print("-" * 65)

        for rec in self.memory.records:
            dist = self._getHammingDist(rec)
            phase = theta * dist
            amp = state[(rec << 1) | 0]

            print(f"{rec:>6} | {dist:>16} | {phase:>7.4f} | {amp:>20.6}")

    def displayPrepCircuit(self) -> None:
        import matplotlib.pyplot as plt
        """
        Display circuit used to prepare initial memory state.
        """
        self.memory.displayCircuit()

    def displayRetrievalCircuit(self) -> None:
        import matplotlib.pyplot as plt
        """
        Display retrieval circuit.

        Raises
        ------
        ValueError
            If key is not set or memory pool does not contain records.
        """
        self._checkReady()
        
        decomp = qml.transforms.decompose(
            self._retrievalOnly, 
            gate_set = {qml.RX, qml.RY, qml.RZ, qml.CNOT}
        )

        fig, ax = qml.draw_mpl(decomp)()
        plt.show()

    def retrieve(self, runs: int) -> tuple[np.ndarray, int, int]:
        """
        Run retrieval circuit and record measurement data.

        Parameters
        ----------
        runs : int
            Number of times circuit is run (shots).
        
        Returns
        -------
        tuple[np.ndarray, int, int]
            Times each record was measured, most frequently measured record,
            number of discarded measurements (control = 1).
        
        Raises
        ------
        TypeError
            If runs is not an integer.
        ValueError
            If runs is not positive.
        """
        self._checkReady()

        if not isinstance(runs, int):
            raise TypeError("Runs must be an integer!")
        
        if runs <= 0:
            raise ValueError("Runs must be positive!")

        dev = qml.device("default.qubit", wires = self.qubitCount)

        @qml.set_shots(runs)
        @qml.qnode(dev)
        def circuit() -> np.ndarray:
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
        
            if rec in counts: 
                counts[rec] += 1

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

    #--------------------------------------------------------------------
    #                      PRIVATE HELPERS
    #--------------------------------------------------------------------

    def _finalStateCircuit(self):
        """
        Build full retrieval QNode that returns pre-measurement state.
        """

        @qml.qnode(self.dev)
        def circuit() -> np.ndarray:
            self.memory.getCircuit(wires = range(self.memQubitCount))
            self._retrievalOnly()
            return qml.state()
        
        return circuit
    
    def _retrievalOnly(self) -> None:
        """
        Apply retrieval circuit.
        """

        qml.Hadamard(wires = self.controlWire)
        self._applyPhaseUnitary()
        qml.Hadamard(wires = self.controlWire)

    def _applyPhaseUnitary(self) -> None:
        """
        Apply diagonal phase unitary using Hamming distances.
        """
        theta = np.pi / (2 * self.memQubitCount)
        phases = np.ones(2 ** self.qubitCount, dtype = complex)

        for rec in self.memory.records:
            h = self._getHammingDist(rec)
            phases[rec << 1 | 0] = np.exp(1j * theta * h)
            phases[rec << 1 | 1] = np.exp(-1j * theta * h)

        qml.DiagonalQubitUnitary(phases, wires = range(self.qubitCount))

    def _checkReady(self) -> None:
        """
        Check that QAM object can be retrieved from.

        Raises
        ------
        ValueError
            If key is not set or memory pool does not contain records.
        """
        if self.key is None:
            raise ValueError("Set key first!")
        if len(self.memory.records) == 0:
            raise ValueError("No records stored!")
        
    def _getHammingDist(self, rec: int) -> int:
        """
        Compute Hamming distance between the key and a record.
        """
        if self.key is None:
            raise ValueError("Set key first!")
        return (self.key ^ rec).bit_count()
    