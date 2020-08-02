"""
This module serves as an entry point for objects in System.Drawing.
"""

from clr import System

from .datatypes import Point, Size, Rectangle
from .utils import get_wrapper_class


def __getattr__(name):
    _original_class = getattr(System.Drawing, name)
    return get_wrapper_class(_original_class)
