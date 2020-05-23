from collections import defaultdict
from functools import wraps

from clr import System, GetClrType

from . import controls, utils, converters
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
        method = getattr(System.Windows.Forms.Application, name)

        if not callable(method):
            raise AttributeError(name)

        @wraps(method)
        def wrapper(*args):
            for arg_types in __ARGUMENT_TYPES[name]:
                if len(args) != len(arg_types):
                    continue

                try:
                    args_ = tuple(converters.ValueConverter(arg_types[arg_i]).to_csharp(arg)
                                  for arg_i, arg in enumerate(args))
                    return converters.ValueConverter.to_python(method(*args_))
                except:
                    pass
            else:
                raise ValueError("Could not convert all arguments {} for {}".format(args, method))

        __WRAPPED_METHODS[name] = wrapper

    return __WRAPPED_METHODS[name]
