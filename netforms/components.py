"""
This module exists to serve as an entry point for objects in System.Windows.Forms that are components,
    but wouldn't be available in controls or forms. For example `ToolStripMenuItem` is a component,
    not a control.

If an object isn't found in System.Windows.Forms, System.ComponentModel will also be checked.
"""

import clr

from clr import System

from expanded_clr import get_wrapper_class, utils


def __getattr__(name):
    name = utils.python_name_to_csharp_name(name)
    _original_class = getattr(System.Windows.Forms, name, getattr(System.ComponentModel, name))
    _original_clr_class = clr.GetClrType(_original_class)

    # Is this a component, but not a control (which are available in controls.py or forms.py)?
    if not _original_clr_class.IsSubclassOf(System.ComponentModel.Component) \
            or _original_clr_class.IsSubclassOf(System.Windows.Forms.Control):
        # This isn't a control, or its a Form (which are found in forms.py)
        raise AttributeError(name)

    return get_wrapper_class(_original_class)
