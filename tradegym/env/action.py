from typing import Optional, Dict, Any, Type, List
import sys
import traceback

from abc import ABC, abstractmethod
import gymnasium as gym


__all__ = ['Action', 'ActionSpace', 'ActionCallResult', 'NoOp']


@dataclass
class ActionCallResult(object):
    input: "Action"
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error: Optional[Exception] = None



class Action(ABC):
    __ACTIONS__: Dict[str, Type["Action"]] = {}

    Name: str
    Description: str

    @property
    def name(self) -> str:
        return self.Name

    @property
    def description(self) -> str:
        return self.Description

    def __call__(self, *args, **kwds) -> ActionCallResult:
        result = ActionCallResult(input=self)
        try:
            result.stdout = self.execute(*args, **kwds)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            result.stderr = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
            result.error = e
        return result

    @abstractmethod
    def execute(self, *args, **kwds) -> str:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {'name': self.Name}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Action":
        def make(name: str, **kwargs):
            return Action.__ACTIONS__[name](**kwargs)
        name = data.get('name', None)
        if name not in Action.__ACTIONS__:
            raise KeyError(f"action '{name}' not registered")
        return make(**data)

    @staticmethod
    def register(atype: Type["Action"]):
        if atype.Name in Action.__ACTIONS__:
            print(f"WARNNING action '{atype.Name}' has been overrided by '{atype}'", file=sys.stderr)
        Action.__ACTIONS__[atype.Name] = atype

    @staticmethod
    def list() -> List[str]:
        return list(Action.__ACTIONS__.values())



class NoOp(Action):
    Name = 'noop'
    Description = 'no operation'

    def execute(self, *args, **kwds):
        return


Action.register(NoOp)


class ActionSpace(gym.spaces.Space):
    def __init__(self):
        super().__init__(shape=None, dtype=Action)

    def sample(self) -> Action:
        return NoOp()

    def contains(self, x):
        return isinstance(x, tuple(Action, dict))

    @staticmethod
    def list_actions() -> List[str]:
        return Action.list()