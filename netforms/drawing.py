from clr import System

from .converters import NamedTupleConverter
from .utils import csharp_namedtuple, get_wrapper_class


Point = csharp_namedtuple('Point', 'X Y')
Size = csharp_namedtuple('Size', 'Width Height')
Rectangle = csharp_namedtuple('Rectangle', 'Location Size')
Font = get_wrapper_class(System.Drawing.Font)
FontStyle = get_wrapper_class(System.Drawing.FontStyle)
GraphicsUnit = get_wrapper_class(System.Drawing.GraphicsUnit)
Icon = get_wrapper_class(System.Drawing.Icon)
Bitmap = get_wrapper_class(System.Drawing.Bitmap)
Color = get_wrapper_class(System.Drawing.Color)
ContentAlignment = get_wrapper_class(System.Drawing.ContentAlignment)


# Note, these converters need to go here instead of in converters.py because of circular import foo
class PointConverter(NamedTupleConverter):
    klasses = {System.Drawing.Point, System.Drawing.PointF}
    python_klass = Point


class SizeConverter(NamedTupleConverter):
    klasses = {System.Drawing.Size, System.Drawing.SizeF}
    python_klass = Size


class RectangleConverter(NamedTupleConverter):
    klasses = {System.Drawing.Rectangle}
    python_klass = Rectangle
