import logging

from collections import namedtuple, defaultdict
from functools import wraps

import clr

from clr import System, GetClrType

logger = logging.getLogger(__name__)
__WRAPPER_CLASSES = dict()


def python_name_to_csharp_name(name):
    if is_python_name(name):
        return name.title().replace('_', '')

    return name


def is_python_name(name):
    return '_' in name or name.islower()


def get_class_from_name(klass_name, base_module=clr):
    """Get the C# class from the string of the name."""
    splitted = klass_name.split('.', 1)
    attr = getattr(base_module, splitted[0], None)
    if attr and len(splitted) > 1:
        return get_class_from_name(splitted[1], attr)
    elif not attr:
        # Now we need to handle nested types.
        splitted = klass_name.split('+', 1)
        attr = getattr(base_module, splitted[0])
        if len(splitted) > 1:
            return get_class_from_name(splitted[1], attr)

    return attr


def wrap_csharp_method(method, arg_type_sets):
    """
    Wraps a C# method, ensuring the arguments are C# arguments the return type is a Python type.

    Args:
        method (callable): The C# method to wrap.
        arg_type_sets (list): A list of tuples, containing possible argument types. We will try to convert the
            arguments given to the method to one of the given sets of types. If successful, the C# method is called.
            If C# accepts the given types, the method is returned.
    """
    @wraps(method)
    def wrapper(*args):
        for arg_types in arg_type_sets:
            if len(args) != len(arg_types):
                continue

            try:
                # Since type matching is important, do not force here.
                args_ = tuple(converters.ValueConverter(arg_types[arg_i]).to_csharp(arg)
                              for arg_i, arg in enumerate(args))
                return converters.ValueConverter.to_python(method(*args_))
            except TypeError:
                # pythonnet raises a TypeError if the given type doesn't match
                pass
        else:
            raise ValueError("Could not convert all arguments {} for {}".format(args, method))

    return wrapper


def wrap_python_method(method, return_type=None):
    """
    Wraps a Python method, ensuring the arguments are Python arguments and the output is C#.
    """
    @wraps(method)
    def wrapper(*args):
        args_ = tuple(converters.ValueConverter.to_python(arg) for arg in args)

        try:
            ret = method(*args_)
        except:
            logger.error('Exception in wrapped method', exc_info=True)
            raise

        if return_type is not None:
            return converters.ValueConverter(return_type).to_csharp(ret, True)

    return wrapper


class MetaWrapper(type):
    def __getattr__(cls, item):
        csharp_name = python_name_to_csharp_name(item)
        return getattr(cls.klass, csharp_name)


def get_wrapper_class(klass):
    """
    Get the wrapper class for the given C# class (or instance).

    Args:
        klass (System.Type, System.Object): If an instance (System.Object), this just gets rerun with `type(klass)`.
            Should NOT be a System.RuntimeType.
    """
    global __WRAPPER_CLASSES
    klass_ = klass

    if isinstance(klass, clr.System.Type):
        return get_wrapper_class(get_class_from_name(klass.ToString()))

    if isinstance(klass, clr.System.Object):
        # This is an instance. Get the type and pass it back in.
        return get_wrapper_class(klass.GetType())

    if klass not in __WRAPPER_CLASSES:
        class WrapperClass(metaclass=MetaWrapper):
            """
            A wrapper class.

            Attributes:
                klass (System.Type): The original C# Type.
                clrtype (System.RuntimeType): The CLR type.
                methods (set): method name -> list of tuples, consisting of possible argument types.
                attributes (dict): attribute name -> attribute class
                events (set): A set of event names in this class.
                nested (set): A set of nested classes in this class.
            """
            klass = klass_
            clrtype = clr.GetClrType(klass_)
            methods = defaultdict(list)
            attributes = dict()
            events = set()
            nested = set()

            def __init__(self, *args, instance=None, **kwargs):
                self.instance = instance if instance is not None else self.klass(*args)

                for prop_name, val in kwargs.items():
                    csharp_name = python_name_to_csharp_name(prop_name)

                    if csharp_name in self.attributes:
                        setattr(self, prop_name, val)
                    elif csharp_name in self.events:
                        if callable(val):
                            val = [val]

                        for handler in val:
                            getattr(self, csharp_name).__iadd__(handler)
                    else:
                        raise TypeError(f"__init__() got an unexpected keyword argument {prop_name!r}")

            def __getattr__(self, name):
                csharp_name = python_name_to_csharp_name(name)

                if csharp_name in self.attributes:
                    return converters.ValueConverter.to_python(getattr(self.instance, csharp_name))
                elif csharp_name in self.methods:
                    method = getattr(self.instance, csharp_name)
                    arg_type_set = self.methods[csharp_name]

                    return wrap_csharp_method(method, arg_type_set)
                elif csharp_name in self.events:
                    return get_wrapper_class(System.EventHandler)(instance=getattr(self.instance, csharp_name))
                elif csharp_name in self.nested:
                    return WrapperClass(getattr(self.instance, csharp_name))

                raise AttributeError(name)

            def __setattr__(self, name, value):
                if not name.startswith('_'):
                    csharp_name = python_name_to_csharp_name(name)

                    if csharp_name in self.events:
                        value = converters.ValueConverter(System.EventHandler).to_csharp(value)
                        setattr(self.instance, csharp_name, value)
                    elif csharp_name in self.methods:
                        raise ValueError('property is read-only')
                    elif csharp_name in self.nested:
                        raise ValueError('property is read-only')
                    elif csharp_name in self.attributes:
                        if self.attributes[csharp_name] is None:
                            raise ValueError('property is read-only')

                        return setattr(self.instance, csharp_name,
                                       converters.ValueConverter(self.attributes[csharp_name]).to_csharp(value, True))

                return super(WrapperClass, self).__setattr__(name, value)

            def __instancecheck__(self, instance):
                return isinstance(instance, klass_)

            def __getitem__(self, item):
                return self.instance[item]

            def __setitem__(self, item, value):
                self.instance[item] = value

            def __iter__(self):
                return iter(self.instance)

            def __eq__(self, other):
                other_instance = getattr(other, 'instance', other)

                return self.instance.__eq__(other_instance)

        for field in WrapperClass.clrtype.GetMembers():
            field_name = field.Name
            if any(field_name.startswith(x) for x in ['get_', 'set_', 'add_', 'remove_', 'op_']):
                continue

            if isinstance(field, System.Reflection.MethodInfo):
                WrapperClass.methods[field_name].append(tuple(
                    param_info.ParameterType for param_info in field.GetParameters()
                ))
            elif isinstance(field, System.Reflection.EventInfo):
                WrapperClass.events.add(field_name)
            elif isinstance(field, System.Reflection.PropertyInfo):
                WrapperClass.attributes[field_name] = field.PropertyType
            elif isinstance(field, System.Reflection.FieldInfo):
                WrapperClass.attributes[field_name] = field.FieldType
            elif isinstance(field, System.Type):
                WrapperClass.nested.add(field_name)
            elif not isinstance(field, System.Reflection.ConstructorInfo):
                logger.warning('Unknown member type info %r for field %s on class %s',
                               field, field_name, WrapperClass.klass)

        WrapperClass.__name__ = WrapperClass.__qualname__ = klass.__name__
        WrapperClass.__module__ = __name__

        __WRAPPER_CLASSES[klass] = WrapperClass

    # Recursively look for subclasses, for the below special stuff...
    wrapper_class_subclasses = __WRAPPER_CLASSES[klass].__subclasses__()
    while wrapper_class_subclasses:
        __WRAPPER_CLASSES[klass] = wrapper_class_subclasses[0]
        wrapper_class_subclasses = __WRAPPER_CLASSES[klass].__subclasses__()

    return __WRAPPER_CLASSES[klass]


class EventHandler(get_wrapper_class(System.EventHandler)):
    def __iadd__(self, other):
        if callable(other):
            other = wrap_python_method(other)

        return get_wrapper_class(System.EventHandler)(instance=self.instance.__iadd__(other))


class MenuStrip(get_wrapper_class(System.Windows.Forms.MenuStrip)):
    def __init__(self, *args, items=None, **kwargs):
        super(MenuStrip, self).__init__(*args, **kwargs)

        if items is not None:
            self.items.add_range(items)


class ToolStripMenuItem(get_wrapper_class(System.Windows.Forms.ToolStripMenuItem)):
    def __init__(self, *args, drop_down_items=None, **kwargs):
        super(ToolStripMenuItem, self).__init__(*args, **kwargs)

        if drop_down_items is not None:
            self.drop_down_items.add_range(drop_down_items)


def csharp_namedtuple(*args, **kwargs):
    """Allow for CSharp names and python names."""
    klass = namedtuple(*args, **kwargs)

    class Subclass(klass):
        def __getattr__(self, name):
            return super(Subclass, self).__getattr__(python_name_to_csharp_name(name))

        def __setattr__(self, name, value):
            return super(Subclass, self).__setattr__(python_name_to_csharp_name(name), value)

    Subclass.__name__ = Subclass.__qualname__ = klass.__name__
    return Subclass


Point = csharp_namedtuple('Point', 'X Y')
Size = csharp_namedtuple('Size', 'Width Height')
Rectangle = csharp_namedtuple('Rectangle', 'Location Size')

from . import converters
