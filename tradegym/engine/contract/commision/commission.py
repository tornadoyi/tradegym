from typing import Optional, Dict, ClassVar, Type
from abc import ABC, abstractmethod
from tradegym.engine.core import TObject, PrivateAttr, computed_property


__all__ = [
    "Commission", 
    "FreeCommission", 
    "CommisionInfo"
]



class CommisionInfo(TObject):
    _exchange_fee: Optional[float] = PrivateAttr(None)
    _broker_fee: Optional[float] = PrivateAttr(None)

    @computed_property
    def total_fee(self) -> float:
        return (self._exchange_fee or 0) + (self._broker_fee or 0)
    
    @computed_property
    def exchange_fee(self) -> Optional[float]:
        return self._exchange_fee
    
    @computed_property
    def broker_fee(self) -> Optional[float]:
        return self._broker_fee
    


class Commission(TObject, ABC):
    Name: ClassVar[str]

    __COMMISIONS__: ClassVar[Dict[str, Type["Commission"]]] = {}

    @abstractmethod
    def __call__(
        self,
        engine: "TradeEngine",
        contract: "Contract",
        price: float,
        volume: int,
        type: str,        # open/close
        side: str,
        position: Optional["Position"] = None,
    ) -> CommisionInfo:
        pass

    @computed_property
    def name(self) -> str:
        return self.Name
    
    @staticmethod
    def register(type: Type["Commission"]):
        assert type.Name is not None, ValueError(f"Register plugin type '{type}' have no name field")
        if type.Name in Commission.__COMMISIONS__:
            print(f"Override register commision type '{type.name}'")
        Commission.__COMMISIONS__[type.Name] = type

    @staticmethod
    def make(name: str, **kwargs) -> Optional["Commission"]:
        cls = Commission.__COMMISIONS__.get(name, None)
        assert cls is not None, ValueError(f"Commission type '{name}' is not found")
        return cls.from_dict(data=kwargs)



class FreeCommission(Commission):
    Name: ClassVar[str] = "free_commission"

    def __call__(self, *args, **kwargs) -> CommisionInfo:
        return CommisionInfo(total_fee=0)
    

Commission.register(FreeCommission)



