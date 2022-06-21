
# XdMind
from pytools.decoratorBase import DecoratorBase


class _InPlaceOption(DecoratorBase):
    VALID_RETURN_TYPES = ['auto', 'AudioFile', 'ndarray', 'XdVideo']

    def __init__(self, fget, *args, returns='auto', inPlaceAttrs=None, **kwargs):
        super().__init__(fget, *args, **kwargs)

        if returns not in self.VALID_RETURN_TYPES:
            raise Exception(f"Unknown return type '{returns}'. Valid types are {self.VALID_RETURN_TYPES}")
        self._returns = returns
        # N.B. We need to use '_data' and not 'res' because when 'res' is accessed, volume gets applied
        self.inPlaceAttrs = inPlaceAttrs or ['_data', '_name']

        if 'inPlace' in self.params:
            self.defaultInPlace = self.params.get('inPlace').default
        else:
            raise Exception(f"{self.final_fget} must include the parameter 'inPlace' to be used with InPlaceOption")

    def getReturnType(self, instance=None):
        if self._returns == 'auto':
            return_type = next((r for r in self.VALID_RETURN_TYPES if r.lower() in instance.__class__.__name__.lower()), instance.__class__.__name__)
            return return_type
        else:
            return self._returns


    def decorator(self, instance, *args, **kwargs):
        if self.fget:
            res = self.fget(instance, *args, **kwargs)
            return_type = self.getReturnType(instance)
            if type(res).__name__ == return_type or return_type == 'unknown':
                use_inPlace = ('inPlace' in kwargs and kwargs.get('inPlace')
                               or ('inPlace' not in kwargs and self.defaultInPlace))
                if use_inPlace:
                    if return_type == 'AudioFile':
                        # For each requested attr (namely, 'res')
                        # Set the instance attr to the result
                        # i.e. instance.res = res.res
                        for attr in self.inPlaceAttrs:
                            if attr in dir(res):
                                val = getattr(res, attr)
                                setattr(instance, attr, val)
                            else:
                                raise AttributeError(f"{res} does not have attribute '{attr}'")
                    elif return_type == 'ndarray':
                        instance.res = res
                    else:
                        instance.__dict__ = res.__dict__
                return res
            else:
                raise Exception(f"{self.fget} returns an object of type {type(res).__name__}. "
                                f"{self} is expecting an object of type {return_type}")
        else:
            raise Exception(f"No fget")


def InPlaceOption(_function=None, returns='auto'):
    """ We wrap the class above so it can be used either with or without arguments"""
    if _function:
        return _InPlaceOption(_function)
    else:
        def decoratorWrapper(_function):
            return _InPlaceOption(_function, returns=returns)

        return decoratorWrapper


