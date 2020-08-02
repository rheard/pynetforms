from collections import defaultdict

from clr import System, GetClrType

from . import components, controls, converters, drawing, utils
from .forms import Form

__WRAPPED_METHODS = dict()
__ARGUMENT_TYPES = defaultdict(list)

for method in GetClrType(System.Windows.Forms.Application).GetMethods():
    __ARGUMENT_TYPES[method.Name].append(tuple(
        param_info.ParameterType for param_info in method.GetParameters()
    ))


def __getattr__(name):
    name = utils.python_name_to_csharp_name(name)

    if name not in __WRAPPED_METHODS:
        method_ = getattr(System.Windows.Forms.Application, name)

        if not callable(method_):
            raise AttributeError(name)

        __WRAPPED_METHODS[name] = utils.wrap_csharp_method(method_, __ARGUMENT_TYPES[name])

    return __WRAPPED_METHODS[name]
