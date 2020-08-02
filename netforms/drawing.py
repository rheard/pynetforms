"""
This module serves as an entry point for objects in System.Drawing.
"""

from clr import System

from expanded_clr.datatypes import Point, Size, Rectangle  # These need to be available here
from expanded_clr.utils import get_wrapper_class, python_name_to_csharp_name


def __getattr__(name):
    name = python_name_to_csharp_name(name)
    _original_class = getattr(System.Drawing, name)
    return get_wrapper_class(_original_class)
