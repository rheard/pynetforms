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
        __empty_arg = object()

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
            csharp_name = python_name_to_csharp_name(name)
            self_type = self.GetType()
            field_type = get_field_type(self_type, csharp_name)
            if field_type is not None:
                return super(NewClass, self).__setattr__(csharp_name, python_value_to_csharp(field_type, value))

            return super(NewClass, self).__setattr__(name, value)

        def __getattr__(self, name):
            if not name.startswith('_') and not name.istitle():
                csharp_val = getattr(self, python_name_to_csharp_name(name), self.__empty_arg)
                if csharp_val is not self.__empty_arg:
                    return csharp_val

            raise AttributeError(name)

        def __instancecheck__(self, instance):
            return isinstance(instance, orig_class)

    NewClass.__name__ = NewClass.__qualname__ = name
    NewClass.__module__ = __name__
    return NewClass
