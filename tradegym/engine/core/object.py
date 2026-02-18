from typing import Dict, Any, Callable
from functools import wraps
from pydantic import BaseModel, field_validator, Field, PrivateAttr, computed_field, ConfigDict


__all__ = [
    "TObject", 
    "field_validator", 
    "Field", 
    "PrivateAttr", 
    "ConfigDict",
    "computed_field",
    "writable",
]



def writable(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self: "TObject", *args, **kwargs):
        with self.writable():
            return func(self, *args, **kwargs)
    return wrapper


class TObject(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _writable_: bool = PrivateAttr(default=False)


    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, key: str, value: Any):
        if key in type(self).model_fields and not self._writable_:
            raise AttributeError(f"Cannot modify read-only attribute '{key}'")
        super().__setattr__(key, value)

    def writable(self):
        class _Writable(object):
            def __enter__(inner_self):
                self._writable_ = True
                return self
            def __exit__(inner_self, *args):
                self._writable_ = False
        return _Writable()

    def serialize(self) -> Dict:
        return self.model_dump(exclude_unset=True, by_alias=True)
    
    @classmethod
    def deserialize(cls, data: Dict) -> "TObject":
        return cls.model_validate(data)
    
    def copy(self) -> "TObject":
        return self.deserialize(self.serialize())
        

        
        

