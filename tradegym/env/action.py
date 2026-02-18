from typing import Optional, Dict, Type, List, ClassVar
import gymnasium as gym
from tradegym.engine import TObject, TradeEngine, Field, TradeInfo


__all__ = ['Action', 'ActionSpace', 'ActionResult', 'OpenAction', 'CloseAction', 'NoOpAction']


class ActionResult(TObject):
    error: Optional[str] = Field(None)
    trade_info: Optional[TradeInfo] = Field(None)

    @property
    def success(self) -> bool:
        return self._error is None



class Action(TObject):
    __ACTIONS__: Dict[str, Type["Action"]] = {}

    Name: ClassVar[str] = None

    @property
    def name(self) -> str:
        return self.Name
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.Name is None:
            return
        Action.__ACTIONS__[cls.Name] = cls

    def __call__(self, engine: TradeEngine) -> ActionResult:
        try:
            trade_info = self.execute(engine)
        except Exception as e:
            return ActionResult(error=str(e))

        return ActionResult(trade_info=trade_info)
    
    def execute(self, engine: TradeEngine) -> Optional[TradeInfo]:
        pass

    @staticmethod
    def list() -> List[str]:
        return list(Action.__ACTIONS__.values())
    
    @staticmethod
    def make(name: str, **kwargs):
        act_cls = Action.__ACTIONS__[name]
        if act_cls is None:
            raise ValueError(f"action '{name}' not found")
        return act_cls.deserialize(kwargs)



class TradeAction(Action):
    code: str = Field()
    side: str = Field()
    price: float = Field()
    volume: Optional[int] = Field(None)
    


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

    def execute(self, engine: TradeEngine) -> Optional[TradeInfo]:
        return None



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