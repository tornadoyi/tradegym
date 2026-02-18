from typing import Optional
from tradegym.engine import TradeInfo, TObject, Field
import gymnasium as gym


__all__ = ['Observation', 'ObservationSpace']


class Observation(TObject):
    error: Optional[str] = Field(None)
    trade_info: Optional[TradeInfo] = Field(None)

    @property
    def success(self) -> bool:
        return self.trade_info.success



class ObservationSpace(gym.spaces.Space):
    def __init__(self):
        super().__init__(shape=None, dtype=Observation)

    def sample(self) -> Observation:
        return Observation()

    def contains(self, x):
        return isinstance(x, Observation)