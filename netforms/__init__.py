from collections import defaultdict

from expanded_clr.utils import wrap_csharp_method, python_name_to_csharp_name
from clr import System, GetClrType

from . import components, controls, drawing
from .forms import Form

__ARGUMENT_TYPES = defaultdict(list)

for method in GetClrType(System.Windows.Forms.Application).GetMethods():
    __ARGUMENT_TYPES[method.Name].append(tuple(
        param_info.ParameterType for param_info in method.GetParameters()
    ))


def __getattr__(name):
    """This module is also an entry point for items found in System.Windows.Forms.Application"""
    name = python_name_to_csharp_name(name)
    _original_method = getattr(System.Windows.Forms.Application, name)

    if not _original_method or name not in __ARGUMENT_TYPES:
        raise AttributeError(name)

    return wrap_csharp_method(_original_method, __ARGUMENT_TYPES[name])
