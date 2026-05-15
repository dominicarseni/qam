"""A Python package implementing quantum associative memory algorithms using PennyLane."""

# Add imports here
from .qam import QAM

__all__ = ["QAM", "QAMGUI"]

def __getattr__(name):
    if name == "QAMGUI":
        from .qamgui import QAMGUI
        return QAMGUI

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


from ._version import __version__
