

# Built-In Python
import shutil
import uuid
from functools import wraps
import inspect
from pathlib import Path



class DecoratorBase:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        if isinstance(fget, DecoratorBase):
            self.fget = fget.decorator
        else:
            self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

        # In the case of nested-decorators, find the "non-decorator" function to inspect the params
        # because decorator-level params will normally be *args, **kwargs
        final_fget = fget
        while isinstance(final_fget, DecoratorBase):
            final_fget = final_fget.fget
        self.final_fget = final_fget
        self.params = inspect.signature(self.final_fget).parameters

    def __repr__(self):
        return f"<{self.__class__.__name__} Decorator>"

    def __call__(self, instance):
        @wraps(self.fget)
        def wrapper(*args, **kwargs):
            return self.decorator(instance, *args, **kwargs)
        return wrapper

    def __get__(self, instance, owner):
        return self.__call__(instance)

    def __set__(self, obj, value):
        if self.fset:
            self.fset(obj, value)
        else:
            raise AttributeError("can't set attribute")

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset=None):
        if fset:
            return type(self)(self.fget, fset, self.fdel, self.__doc__)
        else:
            def wrapper(_function):
                return self.setter(_function)
            return wrapper

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

    def decorator(self, instance, *args, **kwargs):
        raise NotImplementedError(f'{self}.decorator() must be implemented')