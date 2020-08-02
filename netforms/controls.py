"""
This module exists to serve as an entry point for objects in System.Windows.Forms which are controls,
    but not a Form (which are available in forms.py).
"""

import logging

import clr

from clr import System

from . import utils

logger = logging.getLogger(__name__)


def __getattr__(name):
    _original_class = getattr(System.Windows.Forms, name)
    _original_clr_class = clr.GetClrType(_original_class)

    if not _original_clr_class.IsSubclassOf(System.Windows.Forms.Control) \
            or _original_clr_class.IsSubclassOf(System.Windows.Forms.Form):
        # This isn't a control, or its a Form (which are found in forms.py)
        raise AttributeError(name)

    return utils.get_wrapper_class(_original_class)
