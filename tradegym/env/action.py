from typing import Optional, Dict, Type, List, ClassVar
import sys
from abc import ABC, abstractmethod
import gymnasium as gym
from tradegym.engine import TObject, TradeEngine, computed_property, PrivateAttr, TradeInfo


__all__ = ['Action', 'ActionSpace', 'ActionResult', 'OpenAction', 'CloseAction', 'NoOpAction']


class ActionResult(TObject):
    _error: Optional[str] = PrivateAttr(None)
    _trade_info: Optional[TradeInfo] = PrivateAttr(None)

    @property
    def success(self) -> bool:
        return self._error is None

    @computed_property
    def error(self) -> Optional[str]:
        return self._error
    
    @computed_property
    def trade_info(self) -> Optional[TradeInfo]:
        return self._trade_info



class Action(TObject, ABC):
    __ACTIONS__: Dict[str, Type["Action"]] = {}

    Name: ClassVar[str]

    @property
    def name(self) -> str:
        return self.Name

    def __call__(self, engine: TradeEngine) -> ActionResult:
        try:
            trade_info = self.execute(engine)
        except Exception as e:
            return ActionResult(error=str(e))

        return ActionResult(trade_info=trade_info)
    
    @abstractmethod
    def execute(self, engine: TradeEngine) -> Optional[TradeInfo]:
        pass


    @staticmethod
    def register(atype: Type["Action"]):
        if atype.Name in Action.__ACTIONS__:
            print(f"WARNNING action '{atype.Name}' has been overrided by '{atype}'", file=sys.stderr)
        Action.__ACTIONS__[atype.Name] = atype

    @staticmethod
    def list() -> List[str]:
        return list(Action.__ACTIONS__.values())



class TradeAction(Action):
    _code: str = PrivateAttr()
    _side: str = PrivateAttr()
    _price: float = PrivateAttr()
    _volume: Optional[int] = PrivateAttr(None)

    @computed_property
    def code(self) -> str:
        return self._code
    
    @computed_property
    def side(self) -> str:
        return self._side
    
    @computed_property
    def price(self) -> float:
        return self._price
    
    @computed_property
    def volume(self) -> Optional[int]:
        return self._volume
    

class OpenAction(TradeAction):
    Name: ClassVar[str] = 'open'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.volume is not None

    def execute(self, engine: TradeEngine) -> TradeInfo:
        return engine.open(self.code, self.side, self.price, self.volume)
    

class CloseAction(TradeAction):
    Name: ClassVar[str] = 'close'

    def execute(self, engine: TradeEngine) -> TradeInfo:
        return engine.close(self.code, self.side, self.price, self.volume)


class NoOpAction(Action):
    Name: ClassVar[str] = 'noop'

    def __call__(self, engine: TradeEngine):
        return


Action.register(NoOpAction)
Action.register(OpenAction)
Action.register(CloseAction)



class ActionSpace(gym.spaces.Space):
    def __init__(self):
        super().__init__(shape=None, dtype=Action)

    def sample(self) -> Action:
        return NoOpAction()

    def contains(self, x):
        return isinstance(x, tuple(Action, dict))

    @staticmethod
    def list_actions() -> List[str]:
        return Action.list()