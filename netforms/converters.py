"""Converters are responsible from translating types between Python and C#"""

import logging

from clr import System, GetClrType

from . import utils

logger = logging.getLogger(__name__)


class ValueConverter(object):
    """
    Handle conversions between C# values and Python values for a particular C# class.

    Attributes:
        klasses (set): The C# class we're converting from. Not a RuntimeType, but an actual class.
    """
    klasses = set()

    def __new__(cls, klass=None):
        """Find the converter for klass, see get_converter."""
        if cls is ValueConverter:
            converter = cls.get_converter(klass)
            if converter:
                return converter

        return super(ValueConverter, cls).__new__(cls)

    def __init__(self, klass=None):
        if isinstance(klass, System.Type):
            self.clr_type = klass
            self.klass = utils.get_class_from_name(klass.ToString())
        else:
            self.klass = klass
            self.clr_type = GetClrType(self.klass)

    @classmethod
    def get_converter(cls, klass):
        """
        Find the converter for klass.

        Args:
            klass (System.Type, or class): The class to get the converter for. Can be a regular C# class
                or a RuntimeType.
        """
        if not isinstance(klass, System.Type):
            klass = GetClrType(klass)

        for converter in cls.__subclasses__():
            for klass_ in converter.klasses:
                if klass.Equals(klass_) or klass.IsSubclassOf(klass_):
                    return converter(klass_)

            # Also recursively check this subclass' subclasses.
            subclass_converter = converter.get_converter(klass)
            if subclass_converter:
                return subclass_converter

        return None

    @classmethod
    def to_python(cls, value):
        """
        Convert the C# value to Python.

        The basic operation is to just return the value...
        """
        # Since we're converting from C#, we have the type readily available.
        GetType = getattr(value, 'GetType', None)
        if GetType and cls is ValueConverter:
            converter = cls.get_converter(GetType())
            if converter:
                return converter.to_python(value)

        return value

    def to_csharp(self, value, force=False):
        """
        Convert the Python value to C#.

        The basic operation is to just return the value...
        """
        return value


class NamedTupleConverter(ValueConverter):
    """
    Handles conversion for classes that can be handled with a basic named tuple.

    Going from Python to C#, the default behavior is to call klass(*value).

    Going from C# to Python, the default behavior is to create a set of arguments, one for
        each field value for field in fields. That set of arguments is then provided to the python_klass.

    Attributes:
        python_klass: The Python class to use. By default, fields will be supplied as arguments.
    """
    @classmethod
    def to_python(cls, value):
        """Convert the input C# value to Python."""
        args = (getattr(value, field) for field in cls.python_klass._fields)
        args = (ValueConverter.to_python(value) if isinstance(value, System.Object) else value for value in args)
        return cls.python_klass(*args)

    def to_csharp(self, value, force=False):
        """Convert the input Python value to C#."""
        if isinstance(value, self.klass):
            return value

        wrapper_class = utils.get_wrapper_class(self.klass)

        # Convert the subitems too.
        value = tuple(ValueConverter(wrapper_class.attributes[field]).to_csharp(value[field_i])

                      for field_i, field in enumerate(self.python_klass._fields)

                      if field in wrapper_class.attributes)

        return self.klass(*value)


class BasicTypeConverter(ValueConverter):
    """
    Converts a basic Python type to a basic C# type.

    Attributes:
        python_type (type): The python type to convert to before calling the C# method.
        python_types (tuple, optional): A tuple of python types that this **supports**. The above python_type is
            automatically considered here.
    """
    def to_csharp(self, value, force=False):
        if isinstance(value, self.klass):
            return value

        python_types = getattr(self, 'python_types', tuple()) + (self.python_type, )

        if not force and not isinstance(value, python_types):
            raise TypeError(value)

        return self.klass(self.python_type(value))


class StrConverter(BasicTypeConverter):
    klasses = {System.String}
    python_type = str


class IntConverter(BasicTypeConverter):
    klasses = {System.Int32}
    python_type = int
    python_types = (float, )

    def to_csharp(self, value, force=False):
        if isinstance(value, float) and not value.is_integer():
            raise TypeError(f"Got {value} but expected an integer!")

        return super(IntConverter, self).to_csharp(value, force)


class ByteConverter(ValueConverter):
    klasses = {System.Byte}

    def to_csharp(self, value, force=False):
        if not isinstance(value, int) or not 0 <= value <= 255:
            raise TypeError(f"Value {value!r} is not an acceptable byte value!")

        return bytes([value])


class FloatConverter(BasicTypeConverter):
    klasses = {System.Double, System.Single}
    python_type = float
    python_types = (int, )


class BoolConverter(BasicTypeConverter):
    klasses = {System.Boolean}
    python_type = bool


class WrappedConverter(ValueConverter):
    """Handles wrapping classes to handle name and type conversions"""
    klasses = {System.Windows.Forms.Control, System.Windows.Forms.Padding, System.EventHandler,
               System.ComponentModel.Component, System.ComponentModel.Container,
               System.Drawing.Image, System.Drawing.Font, System.Drawing.Icon, System.Drawing.Color,
               System.Windows.Forms.ScrollProperties, System.Windows.Forms.ScrollableControl.DockPaddingEdges}

    def to_csharp(self, value, force=False):
        return getattr(value, "instance", value)

    def to_python_event(self, value):
        return utils.get_wrapper_class(self.klass)(instance=value)

    @classmethod
    def to_python(cls, value):
        return utils.get_wrapper_class(value.GetType())(instance=value)


class WrappedListConverter(WrappedConverter):
    """Handles wrapping arrays and collections of objects"""
    klasses = {System.Windows.Forms.Control.ControlCollection, System.Array[System.Windows.Forms.Control],
               System.Windows.Forms.ToolStripItemCollection, System.Array[System.Windows.Forms.ToolStripItem],
               System.Array[System.Windows.Forms.Form]}

    def to_csharp(self, value, force=False):
        if hasattr(value, "instance"):
            return value.instance

        if isinstance(value, self.klass):
            return value

        contains_method = self.clr_type.GetMethod('Contains')
        if contains_method:
            # To get the collection's element type, we're going to get the argument type for Contains.
            element_type = contains_method.GetParameters()[0].ParameterType
        else:
            # To get an array's element type, we're going to get the return type for Get.
            element_type = self.clr_type.GetMethod("Get").ReturnType

        return [ValueConverter(element_type).to_csharp(value_, force) for value_ in value]
