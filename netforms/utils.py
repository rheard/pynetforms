import logging

from collections import namedtuple

from clr import System, GetClrType

ControlCollection = System.Windows.Forms.Control.ControlCollection  # For later importing...

logger = logging.getLogger(__name__)


def translate_csharp(klass):
    """
    This decorates a class with methods to convert from Python property names ("is_enabled") to C# names ("IsEnabled").

    This gives a C# class dual names for all properties. For instance, you can do instance.text or instance.Text.
    """
    class Subclass(klass):
        def __getattr__(self, name):
            if name.istitle():
                orig_getattr = getattr(super(Subclass, self), '__getattr__', None)
                if orig_getattr is None:
                    raise AttributeError(name)
                else:
                    return orig_getattr(name)

            return getattr(self, python_name_to_csharp_name(name))

        def __setattr__(self, name, value):
            if name.istitle():
                return super(Subclass, self).__setattr__(name, value)

            return setattr(self, python_name_to_csharp_name(name), value)

    Subclass.__name__ = Subclass.__qualname__ = klass.__name__
    return Subclass


def csharp_namedtuple(*args, **kwargs):
    """Allow for CSharp names and python names."""
    return translate_csharp(namedtuple(*args, **kwargs))


Point = csharp_namedtuple('Point', 'X Y')
Size = csharp_namedtuple('Size', 'Width Height')
Rectangle = csharp_namedtuple('Rectangle', 'Location Size')


class CSharpPythonConverter(object):
    """
    Handle conversions between C# values and Python values for a particular C# class.

    Attributes:
        klass: The C# class we're converting from. Not a RuntimeType, but an actual class.
    """
    def __new__(cls, klass=None):
        """Find the converter for klass, see get_converter."""
        if cls is CSharpPythonConverter:
            converter = cls.get_converter(klass)
            if converter:
                return converter()

        if klass and cls is not CSharpPythonConverter:
            logger.warning('Ignoring argument to subclass of CSharpPythonConverter')

        return super(CSharpPythonConverter, cls).__new__(cls)

    @classmethod
    def get_converter(cls, klass):
        """
        Find the converter for klass.

        Args:
            klass (System.RuntimeType): The RuntimeType for the class to search for.
                If you have an instance, you can simply do `instance.GetType()`.

                If you have a class, you can simply do `clr.GetClrType(class)`.

                If you have a RuntimeType and want the RuntimeType of a property,
                    `clrtype.GetProperty(property_name).PropertyType`
        """
        for converter in cls.__subclasses__():
            if hasattr(converter, 'klass') and klass.Equals(converter.klass):
                return converter

            # Also recursively check this subclass subclasses.
            subclass_converter = converter.get_converter(klass)
            if subclass_converter:
                return subclass_converter

        return None

    @classmethod
    def get_converter_by_value(cls, value):
        """
        Find the converter for a value.

        Args:
            value (object): The object to find the converter for.
        """
        for converter in cls.__subclasses__():
            if hasattr(converter, 'klass') and isinstance(value, converter.klass):
                return converter

            # Also recursively check this subclass subclasses.
            subclass_converter = converter.get_converter_by_value(value)
            if subclass_converter:
                return subclass_converter

        return None

    @classmethod
    def to_python(cls, value):
        """
        Convert the C# value to Python.

        The basic operation (str, int, float, etc) is to just return the value...
        """
        # Since we're converting from C#, we have the type readily available.
        converter = cls.get_converter_by_value(value)
        if converter:
            return converter.to_python(value)

        return value

    @classmethod
    def to_csharp(cls, value):
        """
        Convert the Python value to C#.

        The basic operation (str, int, float, etc) is to just return the value...
        """
        return value


class ConvertNamedTuple(CSharpPythonConverter):
    """
    Handles conversion for classes that can be handled with a basic named tuple.

    Going from Python to C#, the default behavior is to call klass(*value).

    Going from C# to Python, the default behavior is to create a set of arguments, one for
        each field value for field in fields. That set of arguments is then provided to the python_klass.

    Attributes:
        python_klass: The Python class to use. By default, fields will be supplied as arguments.

    TODO: System.Reflection _might_ be able to be used to get the attributes (yes it can) and their ordering to the
        class creator (maybe?), preventing the need to define the above named tuples
        (since they could be spun up on the fly)
    """
    @classmethod
    def to_python(cls, value):
        """Convert the input C# value to Python."""
        args = (getattr(value, field) for field in cls.python_klass._fields)
        args = (csharp_value_to_python(value) if isinstance(value, System.Object) else value for value in args)
        return cls.python_klass(*args)

    @classmethod
    def to_csharp(cls, value):
        """Convert the input Python value to C#."""
        clr_type = GetClrType(cls.klass)

        # Convert the subitems too.
        value = tuple(python_value_to_csharp(get_field_type(clr_type, field), value[field_i])
                      for field_i, field in enumerate(cls.python_klass._fields))

        return cls.klass(*value)


class ConvertPoint(ConvertNamedTuple):
    klass = System.Drawing.Point
    python_klass = Point


class ConvertPointF(ConvertNamedTuple):
    klass = System.Drawing.PointF
    python_klass = Point


class ConvertSize(ConvertNamedTuple):
    klass = System.Drawing.Size
    python_klass = Size


class ConvertSizeF(ConvertNamedTuple):
    klass = System.Drawing.SizeF
    python_klass = Size


class ConvertRectangle(ConvertNamedTuple):
    klass = System.Drawing.Rectangle
    python_klass = Rectangle


class ConvertInt32(CSharpPythonConverter):
    klass = System.Int32

    @classmethod
    def to_csharp(cls, value):
        return int(value)


class ConvertDouble(CSharpPythonConverter):
    klass = System.Double

    @classmethod
    def to_csharp(cls, value):
        return float(value)


class ConvertSingle(ConvertDouble):
    klass = System.Single


class ControlCollectionSet(object):
    def __init__(self, controls):
        self.controls = controls

    def __getattr__(self, name):
        if name.istitle():
            return getattr(self.controls, name)

        return getattr(self, python_name_to_csharp_name(name))

    def __setattr__(self, name, value):
        if name.istitle():
            setattr(self.controls, name, value)

        elif name not in ['controls']:
            setattr(self.controls, python_name_to_csharp_name(name), value)

        else:
            super(ControlCollectionSet, self).__setattr__(name, value)

    def __getitem__(self, item):
        return self.controls[item]

    def __iter__(self):
        return iter(self.controls)

    def __instancecheck__(self, instance):
        return isinstance(instance, ControlCollection)


class ConvertControlCollection(CSharpPythonConverter):
    klass = ControlCollection

    @classmethod
    def to_csharp(cls, value):
        raise TypeError("property is read-only")

    @classmethod
    def to_python(cls, value):
        return ControlCollectionSet(value)


def python_name_to_csharp_name(name):
    return name.title().replace('_', '')


def python_value_to_csharp(csharp_type, value):
    if csharp_type is not None:
        return CSharpPythonConverter(csharp_type).to_csharp(value)

    return value


def csharp_value_to_python(value):
    return CSharpPythonConverter.to_python(value)


def get_field_type(klass, field_name):
    """
    Returns the field type from the class.

    Args:
        klass (System.RuntimeType): The class to get the field type from.
        field_name (str): The field to get the type for.

    Returns:
        System.RuntimeType
    """
    prop_info = klass.GetProperty(field_name)
    return prop_info.PropertyType if prop_info else None


from . import controls
