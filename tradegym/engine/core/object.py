from typing import Optional, Dict
from pydantic import BaseModel, field_validator, Field, PrivateAttr, computed_field, ConfigDict


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
    def __init__(self, func=None, **kwargs):
        self.kwargs = kwargs
        super().__init__(func)

    def __call__(self, func):
        return computed_field(
            super().__call__(func),
            **self.kwargs
        )


class NotExist:
    pass


class TObject(BaseModel):

    def __init__(self, *args, **kwargs):
        mro = type(self).mro()
        arg_names = [
            k
            for cls in mro[mro.index(TObject)-1::-1]
            for k in cls.__annotations__
            if k in self.__private_attributes__ or k in self.__signature__.parameters
        ]

        arg_kwds = {k: v for k, v in zip(arg_names[:len(args)], args) if k not in self.__private_attributes__}
        arg_priv_kwds = {k: v for k, v in zip(arg_names[:len(args)], args) if k in self.__private_attributes__}

        for n in arg_names[len(args):]:
            if n in self.__private_attributes__:
                if v := kwargs.pop(n.lstrip("_"), NotExist) is not NotExist:
                    arg_priv_kwds[n] = v
            else:
                if v := kwargs.pop(n, NotExist) is not NotExist:
                    arg_kwds[n] = v

        arg_kwds.update(kwargs)
        super().__init__(**arg_kwds)
        for k, v in arg_priv_kwds.items():
            setattr(self, k, v)


    def to_dict(self) -> Dict:
        return self.model_dump(exclude_unset=True, by_alias=True)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TObject":
        return cls.model_validate(data)
    
    def copy(self) -> "TObject":
        return self.from_dict(self.to_dict())
