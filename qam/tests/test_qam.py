"""
Unit and regression test for the qam package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import qam


def test_qam_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "qam" in sys.modules
