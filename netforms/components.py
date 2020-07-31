import clr

from clr import System

from .utils import get_wrapper_class


def __getattr__(name):
    _original_class = getattr(System.Windows.Forms, name, None)

    if _original_class is None:
        _original_class = getattr(System.ComponentModel, name)

    elif not clr.GetClrType(_original_class).IsSubclassOf(System.ComponentModel.Component):
        raise AttributeError(name)

    return get_wrapper_class(_original_class)


class MenuStrip(__getattr__('MenuStrip')):
    list_arguments = ["Items", ]


class StatusStrip(__getattr__('StatusStrip')):
    list_arguments = ["Items", ]


class ContextMenuStrip(__getattr__('ContextMenuStrip')):
    list_arguments = ["Items", ]


class ToolStripMenuItem(__getattr__('ToolStripMenuItem')):
    list_arguments = ["DropDownItems", ]
