from clr import System, GetClrType

from .utils import python_name_to_csharp_name, csharp_value_to_python, python_value_to_csharp, get_field_type


class Form(System.Windows.Forms.Form):
    __empty_arg = object()

    def __init__(self, *args, controls=None, **kwargs):
        super(Form, self).__init__(*args)

        self.SuspendLayout()
        for control in controls or []:
            self.controls.add(control)

        for prop_name, val in kwargs.items():
            setattr(self, prop_name, val)
        self.ResumeLayout(False)

        self.components = None
        self.initialize_components()

    def __setattr__(self, name, value):
        csharp_name = python_name_to_csharp_name(name)
        self_type = self.GetType()
        field_type = get_field_type(self_type, csharp_name)
        if field_type is not None:
            return super(Form, self).__setattr__(csharp_name, python_value_to_csharp(field_type, value))
        
        return super(Form, self).__setattr__(name, value)

    def __getattr__(self, name):
        if not name.startswith('_') and not name.istitle():
            csharp_val = getattr(self, python_name_to_csharp_name(name), self.__empty_arg)
            if csharp_val is not self.__empty_arg:
                return csharp_val

        raise AttributeError(name)

    def __getattribute__(self, item):
        return csharp_value_to_python(super(Form, self).__getattribute__(item))

    def initialize_components(self):
        self.initialize_component()

    def initialize_component(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        pass
