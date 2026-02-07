from typing import Optional, Tuple, List, Dict, Set, Any, get_origin, get_args, Callable
from pydantic import BaseModel, field_validator, Field, PrivateAttr, computed_field, ConfigDict, model_serializer, model_validator


__all__ = [
    "TObject", 
    "field_validator", 
    "Field", 
    "PrivateAttr", 
    "ConfigDict",
    "computed_field",
    "computed_property",
]



class computed_property(property):
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        super().__init__(fget, fset, fdel, doc)
        self._computed_kwargs = kwargs
        self._registered = False  

    def __set_name__(self, owner, name):
        if self._registered:
            return
        self._registered = True

        cf = computed_field(self.fget, **self._computed_kwargs)
        if self.fset is not None:
            def setter(obj, value):
                return self.fset(obj, value)
            cf = cf.setter(setter)
        setattr(owner, name, cf)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__, **self._computed_kwargs)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__, **self._computed_kwargs)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__, **self._computed_kwargs)


class NotExist:
    pass


class TObject(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args, **kwargs):
        mro = type(self).mro()
        arg_names = [
            k
            for cls in mro[mro.index(TObject)-1::-1]
            for k in cls.__annotations__
            if k in self.__private_attributes__ or k in type(self).__signature__.parameters
        ]

        arg_kwds = {k: v for k, v in zip(arg_names[:len(args)], args) if k not in self.__private_attributes__}
        arg_priv_kwds = {k: v for k, v in zip(arg_names[:len(args)], args) if k in self.__private_attributes__}

        for n in arg_names[len(args):]:
            if n in self.__private_attributes__:
                if (v := kwargs.pop(n.lstrip("_"), NotExist)) is not NotExist:
                    arg_priv_kwds[n] = v
            else:
                if (v := kwargs.pop(n, NotExist)) is not NotExist:
                    arg_kwds[n] = v

        arg_kwds.update(kwargs)
        super().__init__(**arg_kwds)
        for k, v in arg_priv_kwds.items():
            expected_type = self.__annotations__.get(k)
            if expected_type is not None:
                v = self._dfs_from_dict(v, expected_type)
            setattr(self, k, v)

    def to_dict(self) -> Dict:
        return self.model_dump(exclude_unset=True, by_alias=True)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TObject":
        return cls.model_validate(data)
    
    def copy(self) -> "TObject":
        return self.from_dict(self.to_dict())
    
    @model_serializer(mode="wrap")
    def _serialize(self, handler: Callable) -> Dict:
        return self.serialize(handler)
    
    @model_validator(mode="before")
    @classmethod
    def _deserialize(cls, data: Dict) -> Dict:
        return cls.deserialize(data)
    
    def serialize(self, handler: Callable) -> Dict:
        return handler(self)
    
    @classmethod
    def deserialize(cls, data: Dict) -> Dict:
        return data
    
    @classmethod
    def _dfs_from_dict(cls, value: Any, expected_type: Any) -> Any:
        origin = get_origin(expected_type)
        args = get_args(expected_type)

        if value is None:
            return None

        # TObject
        if isinstance(value, dict) and isinstance(expected_type, type) and issubclass(expected_type, TObject):
            return expected_type.from_dict(value)

        # List / Set
        if origin in (list, List):
            return [cls._dfs_from_dict(v, args[0] if args else Any) for v in value]
        if origin in (set, Set):
            return {cls._dfs_from_dict(v, args[0] if args else Any) for v in value}

        # Tuple
        if origin in (tuple, Tuple):
            if len(args) == 2 and args[1] is Ellipsis:  # Tuple[T, ...]
                return tuple(cls._dfs_from_dict(v, args[0]) for v in value)
            return tuple(cls._dfs_from_dict(v, t) for v, t in zip(value, args))

        # Dict
        if origin in (dict, Dict):
            return {cls._dfs_from_dict(k, args[0] if args else Any): cls._dfs_from_dict(v, args[1] if len(args) > 1 else Any) for k, v in value.items()}

        return value

