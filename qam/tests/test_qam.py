"""
Unit and regression test for the qam package.
"""

# Import package, test suite, and other packages as needed
import numpy as np
import pytest
import matplotlib.pyplot as plt
from qam import QAM

def test_qam_init():
    qam = QAM(4)

    assert qam.memQubitCount == 4
    assert qam.qubitCount == 5
    assert qam.controlWire == 4
    assert qam.key is None

def test_qam_init_with_key():
    qam = QAM(4, key = 7)

    assert qam.key == 7

def test_qam_init_bad_qCount():
    with pytest.raises(TypeError):
        QAM("4")
    
    with pytest.raises(ValueError):
        QAM(0)

    with pytest.raises(ValueError):
        QAM(-1)
    
def test_set_key():
    qam = QAM(4)
    qam.setKey(7)

    assert qam.key == 7

def test_set_key_bad_input():
    qam = QAM(4)
    with pytest.raises(TypeError):
        qam.setKey("7")

        with pytest.raises(TypeError):
            qam.setKey("7")

        with pytest.raises(ValueError):
            qam.setKey(-1)

        with pytest.raises(ValueError):
            qam.setKey(16)

def test_add_records():
    qam = QAM(4)

    qam.addRecords([0, 4, 8, 12])

    assert qam.memory.records == [0, 4, 8, 12]
    assert qam.memory.recordCount == 4
    assert qam.memory.state is not None

def test_remove_records():
    qam = QAM(4)
    qam.addRecords([0, 4, 8, 12])

    qam.removeRecords([4, 12])

    assert qam.memory.records == [0, 8]
    assert qam.memory.recordCount == 2

def test_clear():
    qam = QAM(4)
    qam.addRecords([0, 4, 8, 12])

    qam.removeRecords([4, 12])

    assert qam.memory.records == [0, 8]
    assert qam.memory.recordCount == 2

def test_print_init_state(capsys):
    qam = QAM(2)
    qam.addRecords([0, 1])

    qam.printInitState()

    captured = capsys.readouterr()

    assert "[" in captured.out
    assert "]" in captured.out

def test_print_final_state_data(capsys):
    qam = QAM(2, key = 0)
    qam.addRecords([0, 1])

    qam.printFinalStateData()

    captured = capsys.readouterr()

    assert "Record" in captured.out
    assert "Hamming Distance" in captured.out
    assert "Amplitude if Control = 0" in captured.out

def test_display_prep_circuit(monkeypatch):
    qam = QAM(2)
    qam.addRecords([0, 1])

    shown = {"called": False}

    def fake_show():
        shown["called"] = True
    
    monkeypatch.setattr(plt, "show", fake_show)

    qam.displayPrepCircuit()

    assert shown["called"] is True

def test_display_retrieval_circuit(monkeypatch):
    qam = QAM(2, key = 0)
    qam.addRecords([0, 1])
    
    shown = {"called": False}

    def fake_show():
        shown["called"] = True

    monkeypatch.setattr(plt, "show", fake_show)

    qam.displayRetrievalCircuit()

    assert shown["called"] is True

def test_retrieve():
    qam = QAM(2, key = 0)
    qam.addRecords([0, 1])

    counts, best_record, discarded = qam.retrieve(100)

    assert isinstance(counts, np.ndarray)
    assert(len(counts)) == 2
    assert best_record in [0, 1]
    assert isinstance(discarded, int)
    assert discarded >= 0
    assert np.sum(counts) + discarded <= 100

def test_retrieve_bad_runs():
    qam = QAM(2, key = 0)
    qam.addRecords([0, 1])

    with pytest.raises(TypeError):
        qam.retrieve("100")

    with pytest.raises(ValueError):
        qam.retrieve(0)
    
    with pytest.raises(ValueError):
        qam.retrieve(-10)

def test_retrieve_without_key():
    qam = QAM(2)
    qam.addRecords([0, 1])

    with pytest.raises(ValueError):
        qam.retrieve(100)
    
def test_retrieve_without_records():
    qam = QAM(2, key = 0)

    with pytest.raises(ValueError):
        qam.retrieve(100)

def test_print_final_state_data_values(capsys):
    qam = QAM(2, key = 0)
    qam.addRecords([0, 1])

    qam.printFinalStateData()
    captured = capsys.readouterr()
    output = captured.out

    assert "Record | Hamming Distance | Phase | Amplitude if Control = 0" in output

    assert "     0 |                0 |  0.0000" in output
    assert "(0.707107+0j)" in output

    assert "     1 |                1 |  0.7854" in output
    assert "(0.5+" in output