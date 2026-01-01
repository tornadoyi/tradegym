from typing import Optional, Dict, Type
import sys
from abc import ABC, abstractmethod


__all__ = ["Rule"]



class Rule(ABC):
    Name: str

    __RULES__: Dict[str, Type["Rule"]] = {}


    @abstractmethod
    def __call__(self, *args, **kwds):
        pass


    @staticmethod
    def register(rtype: Type["Rule"]):
        if rtype.Name in Rule.__RULES__:
            print(f"WARNNING rule '{rtype.Name}' has been overrided by '{rtype}'", file=sys.stderr)
        Rule.__RULES__[rtype.Name] = rtype