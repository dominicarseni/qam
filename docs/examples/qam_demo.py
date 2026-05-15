"""
QAM Demo:

Create a QAM object which uses 2 qubits to store the memory state. With two qubits, the allowed
integer record values are 0 to 3 (00, 01, 10, 11 in binary, respectively). The records are added
to the memory pool, and the initial state and final state retrieval data are printed. Retrieval
is performed with a specified number of shots.

Additionally, show that a 4 qubit QAM object allows for a greater range of inputs.


"""

from qam import QAM

def main() -> None:
    """
    Run 2-qubit QAM retrieval example.
    """

    # Create a QAM object which stores the memory state in 2 qubits.
    # The key the pattern which memory records are compared to for retrieval.
    qam = QAM(2, key = 0)

    # Store 0 and 1 in memory, correspondig to 00 and 01 in binary. Duplicates are not allowed,
    # so the record 1 will only be added once.
    qam.addRecords([0, 1, 1])

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

    # See how the initial state is prepared by displaying the circuit.
    qam.displayPrepCircuit()

    # Print final state data before measurement.
    print("\nFinal State Data: ")
    qam.printFinalStateData()

    # See how the final state is prepared.
    qam.displayRetrievalCircuit()

    # Run the retrieval circuit with specified number of runs. 
    print("\nRetrieval Results: ")
    counts, best_record, discarded = qam.retrieve(1000)

    print("\nOutput: ")
    print(f"Times Measured: {counts}")
    print(f"Most Frequently Measured Record: {best_record} ({format(best_record, '02b')})")
    print(f"Discarded Measurements: {discarded}")

    # Now replace 1000 with 100. How does the accuracy of the result depend on the number of runs? 

    # Remove all records from the QAM.
    qam2.clear()

    # If you need to store more records, create a QAM object with more qubits, e.g. 4.
    # The key can be set separately.
    qam2 = QAM(4)

    # Records can now take values from 0 to 15.
    qam2.addRecords([5, 8, 9, 14])

    # Remove a record.
    qam2.removeRecords([5, 9])

    # Now set the key.
    qam2.setKey(10)

    # Make sure the key is what you expect.
    print(qam2.key)


if __name__ == "__main__":
    main()
