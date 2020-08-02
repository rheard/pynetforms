from clr import System, GetClrType

from .converters import NamedTupleConverter
from .utils import get_wrapper_class, csharp_namedtuple


class Form(get_wrapper_class(System.Windows.Forms.Form)):
    def __init__(self, *args, controls=None, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

        for control in controls or []:
            self.controls.add(control)

        self.initialize_components()

    def initialize_components(self):
        self.initialize_component()

    def initialize_component(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        pass


def __getattr__(name):
    _original_class = getattr(System.Windows.Forms, name)
    _original_clr_class = GetClrType(_original_class)

    if (_original_clr_class.IsSubclassOf(System.Windows.Forms.Control)
        and not _original_clr_class.IsSubclassOf(System.Windows.Forms.Form)) \
            or _original_clr_class.IsSubclassOf(System.ComponentModel.Component):
        # Either this is a control that isn't a form (which are available in controls.py),
        #   or its a component (which are available in components.py).
        raise AttributeError(name)

    return get_wrapper_class(_original_class)


Padding = csharp_namedtuple('Padding', 'Left Top Right Bottom')


# Note, these converters need to go here instead of in converters.py because of circular import foo
class PaddingConverter(NamedTupleConverter):
    klasses = {System.Windows.Forms.Padding}
    python_klass = Padding
