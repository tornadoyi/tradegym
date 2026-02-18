from typing import Optional, Sequence, List, Literal
from datetime import datetime
import secrets
from tradegym.engine.core import TObject, Field
from tradegym.engine.contract import Contract


__all__ = ["Position", "Close"]


class Position(TObject):
    code: str = Field()
    side: Literal["long", "short"] = Field()
    price: float = Field()
    volume: float = Field()
    commission: float = Field()
    margin: float = Field()
    date: datetime = Field()

    id: str = Field(default_factory=lambda: secrets.token_urlsafe(8))
    closes: List["Close"] = Field(default_factory=list)

    contract: Optional[Contract] = Field(None, exclude=True)

    @property
    def status(self) -> str:
        return "opened" if self.current_volume > 0 else "closed"
    
    @property
    def opened(self) -> bool:
        return self.status == "opened"
    
    @property
    def closed(self) -> bool:
        return self.status == "closed"
    
    @property
    def closes(self) -> Sequence["Close"]:
        return self.closes
    
    @property
    def closed_commission(self) -> float:
        return sum(close.commission for close in self.closes)

    @property
    def total_commission(self) -> float:
        return self.commission + self.closed_commission

    @property
    def closed_volume(self) -> int:
        return sum(close.volume for close in self.closes)

    @property
    def current_volume(self) -> int:
        return self.volume - self.closed_volume
    
    @property
    def released_margin(self) -> float:
        return sum(close.released_margin for close in self.closes)
    
    @property
    def position_margin(self) -> float:
        return self.margin - self.released_margin

    def close(self, price: float, volume: int, commission: float, realized_pnl: float, date: datetime) -> "Close":
        assert self.current_volume >= volume, f"cannot close more than current quantity {self.current_volume}"
        close = Close(price, volume, commission, realized_pnl, date)
        self.closes.append(close)
        return close
    
    

class Close(TObject):
    price: float = Field()
    volume: int = Field()
    commission: float = Field()
    released_margin: float = Field()
    realized_pnl: float = Field()
    date: datetime = Field()
    id: str = Field(default_factory=lambda: secrets.token_urlsafe(8))
    