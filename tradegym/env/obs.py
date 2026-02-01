from typing import Optional, Dict, Sequence
from tradegym.engine import TradeInfo, TObject, computed_property, PrivateAttr
import gymnasium as gym


__all__ = ['Observation', 'ObservationSpace']


class Observation(TObject):
    _error: Optional[str] = PrivateAttr(None)
    _trade_info: Optional[TradeInfo] = PrivateAttr(None)

    @property
    def success(self) -> bool:
        return self._trade_info.success()

    @computed_property
    def error(self) -> Optional[str]:
        return self._error
    
    @computed_property
    def trade_info(self) -> Optional[TradeInfo]:
        return self._trade_info



class ObservationSpace(gym.spaces.Space):
    def __init__(self):
        super().__init__(shape=None, dtype=Observation)

    def sample(self) -> Observation:
        return Observation()

    def contains(self, x):
        return isinstance(x, Observation)