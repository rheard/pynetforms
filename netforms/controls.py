import logging

import clr

from clr import System

from .utils import get_wrapper_class

logger = logging.getLogger(__name__)


def __getattr__(name):
    _original_class = getattr(System.Windows.Forms, name)

    if not clr.GetClrType(_original_class).IsSubclassOf(System.Windows.Forms.Control):
        raise AttributeError(name)

    return get_wrapper_class(_original_class)


class SplitContainer(__getattr__("SplitContainer")):
    list_arguments = ["Controls", ]
