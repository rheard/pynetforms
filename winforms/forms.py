from clr import System

from .utils import python_name_to_csharp_name, csharp_value_to_python, python_value_to_csharp


class Form(System.Windows.Forms.Form):
    def __init__(self, *args, controls=None, **kwargs):
        super(Form, self).__init__(*args)

        self.SuspendLayout()
        for control in controls or []:
            self.controls.add(control)

        for prop_name, val in kwargs.items():
            setattr(self, prop_name, val)
        self.ResumeLayout(False)

        self.initialize_components()

    def __setattr__(self, name, value):
        if name.istitle():
            self_type = self.GetType()
            return super(Form, self).__setattr__(name, python_value_to_csharp(self_type, value))

        return setattr(self, python_name_to_csharp_name(name), value)

    def __getattr__(self, name):
        if name.istitle():
            return super(Form, self).__getattr__(name)

        return getattr(self, python_name_to_csharp_name(name))

    def __getattribute__(self, item):
        return csharp_value_to_python(super(Form, self).__getattribute__(item))

    def initialize_components(self):
        self.initialize_component()

    def initialize_component(self):
        self.InitializeComponent()

    def InitializeComponent(self):
        self.components = System.ComponentModel.Container()
