"""
This module serves as an entry point for objects in System.Drawing.
"""

from clr import System

from expanded_clr.datatypes import Point, Size, Rectangle  # These need to be available here
from expanded_clr import get_wrapper_class, utils


def __getattr__(name):
    name = utils.python_name_to_csharp_name(name)
    _original_class = getattr(System.Drawing, name)
    return get_wrapper_class(_original_class)
