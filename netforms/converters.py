"""Converters are responsible from translating types between Python and C#"""

from clr import System, GetClrType

from .utils import get_wrapper_class, Point, Size, Rectangle, get_class_from_name


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
            klass = get_class_from_name(klass.ToString())

        self.klass = klass

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

    def to_csharp(self, value):
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

    TODO: System.Reflection _might_ be able to be used to get the attributes (yes it can) and their ordering to the
        class creator (maybe?), preventing the need to define the above named tuples
        (since they could be spun up on the fly)
    """
    @classmethod
    def to_python(cls, value):
        """Convert the input C# value to Python."""
        args = (getattr(value, field) for field in cls.python_klass._fields)
        args = (ValueConverter.to_python(value) if isinstance(value, System.Object) else value for value in args)
        return cls.python_klass(*args)

    def to_csharp(self, value):
        """Convert the input Python value to C#."""
        if isinstance(value, self.klass):
            return value

        wrapper_class = get_wrapper_class(self.klass)

        # Convert the subitems too.
        value = tuple(ValueConverter(wrapper_class.attributes[field]).to_csharp(value[field_i])

                      for field_i, field in enumerate(self.python_klass._fields)

                      if field in wrapper_class.attributes)

        return self.klass(*value)


class PointConverter(NamedTupleConverter):
    klasses = {System.Drawing.Point, System.Drawing.PointF}
    python_klass = Point


class SizeConverter(NamedTupleConverter):
    klasses = {System.Drawing.Size, System.Drawing.SizeF}
    python_klass = Size


class RectangleConverter(NamedTupleConverter):
    klasses = {System.Drawing.Rectangle}
    python_klass = Rectangle


class StrConverter(NamedTupleConverter):
    klasses = {System.String}

    def to_csharp(self, value):
        if isinstance(value, self.klass):
            return value

        if not isinstance(value, str):
            raise ValueError(value)

        return self.klass(value)


class IntConverter(NamedTupleConverter):
    klasses = {System.Int32}

    def to_csharp(self, value):
        if isinstance(value, self.klass):
            return value

        if not isinstance(value, (int, float)):
            raise ValueError(value)

        return self.klass(int(value))


class FloatConverter(NamedTupleConverter):
    klasses = {System.Double, System.Single}

    def to_csharp(self, value):
        if isinstance(value, self.klass):
            return value

        if not isinstance(value, (int, float)):
            raise ValueError(value)

        return self.klass(float(value))


class WrappedConverter(ValueConverter):
    klasses = {System.Windows.Forms.Control.ControlCollection, System.Windows.Forms.Control}

    def to_csharp(self, value):
        return value.instance

    @classmethod
    def to_python(cls, value):
        return get_wrapper_class(value.GetType())(instance=value)
