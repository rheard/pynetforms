import logging

from clr import System

from System.Windows.Forms import Control  # So people can import it from here for isinstance(object, Control).

from .utils import csharp_value_to_python, python_value_to_csharp, python_name_to_csharp_name, get_field_type

logger = logging.getLogger(__name__)


def __getattr__(name):
    orig_class = getattr(System.Windows.Forms, name, None)

    if not orig_class:
        raise AttributeError(name)

    class NewClass(orig_class):
        def __init__(self, *args, **kwargs):
            super(NewClass, self).__init__(*args)
            for prop_name, val in kwargs.items():
                setattr(self, prop_name, val)

        def __getattribute__(self, item):
            return csharp_value_to_python(super(NewClass, self).__getattribute__(item))

        def __setattr__(self, name, value):
            # TODO: Instead of getting the field type here, every time,
            #   considering iterating over all the properties in __init__
            #   and creating a dict for the fields with special types.
            if name.istitle():
                self_type = self.GetType()
                return super(NewClass, self).__setattr__(
                    name,
                    python_value_to_csharp(get_field_type(self_type, name), value)
                )

            return setattr(self, python_name_to_csharp_name(name), value)

        def __getattr__(self, name):
            if name.istitle():
                raise AttributeError(name)

            return getattr(self, python_name_to_csharp_name(name))

    NewClass.__name__ = NewClass.__qualname__ = name
    NewClass.__module__ = __name__
    return NewClass
