from typing import Optional, Dict, Any, Tuple, Union
import gymnasium as gym
from gymnasium.envs.registration import register
from tradegym.engine import TradeEngine, PrivateAttr, computed_property
from .action import Action, ActionSpace, ActionResult
from .obs import ObservationSpace, Observation


__all__ = ['TradeEnv']



class TradeEnv(gym.Env):

    observation_space = ObservationSpace()
    action_space = ActionSpace()

    def __init__(self, engine: Optional[TradeEngine] = None, **kwargs):
        super().__init__()
        if engine is not None:
            assert len(kwargs) == 0, f"Can not specify both engine and arguments of engine"
        self._engine = TradeEngine(**kwargs) if engine is None else engine

    @property
    def engine(self) -> TradeEngine:
        return self._engine

    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[Observation, Dict]:
        return Observation(), {}

    def step(self, action: Union[Action, Dict]):
        # wrap action
        if isinstance(action, dict):
            action = Action.from_dict(action)

        # run action
        result: ActionResult = action(self.engine)

        # return
        observation = Observation.from_dict(result.to_dict())
        return observation, 0.0, False, False, {}

    def copy(self) -> "TradeEnv":
        return type(self).from_dict(self.to_dict())

    def to_dict(self) -> Dict:
        return {'engine': self.engine.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict) -> "TradeEnv":
        return cls(engine=TradeEngine.from_dict(data['engine']))

    @staticmethod
    def make(name="TradeEnv-v0", **kwargs) -> "TradeEnv":
        return gym.make(name, **kwargs)



register(
    id='TradeEnv-v0',
    entry_point='tradegym.env.env:TradeEnv',
    order_enforce=False,
    disable_env_checker=True,
)