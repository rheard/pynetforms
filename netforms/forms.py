from clr import System, GetClrType

from .utils import __WRAPPER_CLASSES, get_wrapper_class


class Form(get_wrapper_class(System.Windows.Forms.Form)):
    def __init__(self, *args, controls=None, **kwargs):
        super(Form, self).__init__(*args, **kwargs)

        self.SuspendLayout()
        for control in controls or []:
            self.controls.add(control)
        self.ResumeLayout(False)

        self.initialize_components()

    def initialize_components(self):
        self.initialize_component()

    def initialize_component(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        pass


__WRAPPER_CLASSES[System.Windows.Forms.Form] = Form


def __getattr__(name):
    _original_class = getattr(System.Windows.Forms, name)

    if GetClrType(_original_class).IsSubclassOf(System.Windows.Forms.Control):
        raise AttributeError(name)

    return get_wrapper_class(_original_class)
