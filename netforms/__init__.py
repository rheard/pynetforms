from . import controls, utils
from .forms import Form

from clr import System


def __getattr__(name):
    return getattr(System.Windows.Forms.Application, name,
                   getattr(System.Windows.Forms.Application, utils.python_name_to_csharp_name(name)))
