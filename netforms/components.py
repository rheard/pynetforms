import clr

from clr import System

from . import utils


def __getattr__(name):
    _original_class = getattr(System.Windows.Forms, name, getattr(System.ComponentModel, name))
    _original_clr_class = clr.GetClrType(_original_class)

    # Is this a component, but not a control (which are available in controls.py or forms.py)?
    if not _original_clr_class.IsSubclassOf(System.ComponentModel.Component) \
            or _original_clr_class.IsSubclassOf(System.Windows.Forms.Control):
        # This isn't a control, or its a Form (which are found in forms.py)
        raise AttributeError(name)

    return utils.get_wrapper_class(_original_class)
