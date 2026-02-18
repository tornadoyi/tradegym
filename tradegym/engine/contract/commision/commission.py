from typing import Optional, Dict, ClassVar, Type
from abc import ABC, abstractmethod
from tradegym.engine.core import TObject, Field, computed_field


__all__ = [
    "Commission", 
    "FreeCommission", 
    "CommisionInfo"
]



class CommisionInfo(TObject):
    exchange_fee: Optional[float] = Field(None)
    broker_fee: Optional[float] = Field(None)

    @property
    def total_fee(self) -> float:
        return (self.exchange_fee or 0) + (self.broker_fee or 0)
    


class Commission(TObject, ABC):
    Name: ClassVar[str]

    __COMMISIONS__: ClassVar[Dict[str, Type["Commission"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Commission.__COMMISIONS__[cls.Name] = cls

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

    @computed_field
    @property
    def name(self) -> str:
        return self.Name

    @staticmethod
    def make(name: str, **kwargs) -> Optional["Commission"]:
        cls = Commission.__COMMISIONS__.get(name, None)
        assert cls is not None, ValueError(f"Commission type '{name}' is not found")
        return cls.deserialize(data=kwargs)



class FreeCommission(Commission):
    Name: ClassVar[str] = "free"

    def __call__(self, *args, **kwargs) -> CommisionInfo:
        return CommisionInfo(total_fee=0)
    



