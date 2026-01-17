from typing import Optional, Any, Dict
import pandas as pd
from tradegym.engine.core import ISerializer



__all__ = ["Quote"]



class Quote(dict, ISerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def datatime(self) -> pd.Timestamp:
        return self["datetime"]

    def __getattr__(self, name):
        return super().__getitem__(name)
    
    def __hasattr__(self, name):
        return name in self

    def __setattr__(self, name, value):
        attr = type(self).__dict__.get(name)
        if isinstance(attr, property) and attr.fset is not None:        # setter
            return super().__setattr__(name, value)

        if not hasattr(self, name):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        return super().__setitem__(name, value)
    
    def to_dict(self) -> Dict:
        return dict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Quote":
        return cls(**data)