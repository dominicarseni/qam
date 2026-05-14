"""
Two-qubit QAM Demo:

Create a QAM object which uses 2 qubits to store the memory state. With two qubits, the allowed
integer record values are 0 to 3 (00, 01, 10, 11 in binary, respectively). The records are added
to the memory pool, and the initial state and final state retrieval data are printed. Retrieval
is performed with a specified number of shots.
"""

from qam import QAM

def main() -> None:
    """
    Run 2-qubit QAM retrieval example.
    """

    # Create a QAM object which stores the memory state in 2 qubits.
    # The key the pattern which memory records are compared to for retrieval.
    qam = QAM(2, key = 0)

    # Store 0 and 1 in memory, correspondig to 00 and 01 in binary.
    qam.addRecords([0, 1])

    # Print records stored in the memory pool as integers.
    print("Stored Records as Integers: ")
    print(qam.memory.records)

    # Print the same records in binary.
    print("\nStored Records in Binary Form: ")
    for rec in qam.memory.records:
        print(format(rec, "02b"))
    
    # Print the initial state in memory.
    print("\nInitial Memory State: ")
    qam.printInitState()

    # Print final state data before measurement.
    print("\nFinal State Data: ")
    qam.printFinalStateData()

    # Run the retrieval circuit with specified number of runs.
    print("\nRetrieval Results: ")
    counts, best_record, discarded = qam.retrieve(1000)

    print("\nOutput: ")
    print(f"Times Measured: {counts}")
    print(f"Most Frequently Measured Record: {best_record} ({format(best_record, '02b')})")
    print(f"Discarded Measurements: {discarded}")

if __name__ == "__main__":
    main()
