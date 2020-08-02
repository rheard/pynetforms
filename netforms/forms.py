from clr import System, GetClrType

from expanded_clr.datatypes import Padding  # These need to be available here
from expanded_clr.utils import get_wrapper_class, python_name_to_csharp_name


class Form(get_wrapper_class(System.Windows.Forms.Form)):
    """By default, we just want to send a call down the initialize_components stack"""

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

        self.initialize_components()

    def initialize_components(self):
        self.initialize_component()

    def initialize_component(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        pass


def __getattr__(name):
    name = python_name_to_csharp_name(name)
    _original_class = getattr(System.Windows.Forms, name)
    _original_clr_class = GetClrType(_original_class)

    if (_original_clr_class.IsSubclassOf(System.Windows.Forms.Control)
        and not _original_clr_class.IsSubclassOf(System.Windows.Forms.Form)) \
            or _original_clr_class.IsSubclassOf(System.ComponentModel.Component):
        # Either this is a control that isn't a form (which are available in controls.py),
        #   or its a component (which are available in components.py).
        raise AttributeError(name)

    return get_wrapper_class(_original_class)
