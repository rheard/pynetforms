"""
This module exists to serve as an entry point for objects in System.Windows.Forms which are controls,
    but not a Form (which are available in forms.py).
"""

import clr

from clr import System

from expanded_clr import get_wrapper_class, utils


def __getattr__(name):
    name = utils.python_name_to_csharp_name(name)
    _original_class = getattr(System.Windows.Forms, name)
    _original_clr_class = clr.GetClrType(_original_class)

    if not _original_clr_class.IsSubclassOf(System.Windows.Forms.Control) \
            or _original_clr_class.IsSubclassOf(System.Windows.Forms.Form):
        # This isn't a control, or its a Form (which are found in forms.py)
        raise AttributeError(name)

    return get_wrapper_class(_original_class)
