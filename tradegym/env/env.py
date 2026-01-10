from typing import Optional, Dict, Any, Tuple, Union
import gymnasium as gym
from gymnasium.envs.registration import register
from tradegym.engine import TradeEngine
from .action import Action, ActionSpace
from .obs import ObservationSpace, Observation


__all__ = ['HomeEnv']



class TradeEnv(gym.Env):

    observation_space = ObservationSpace()
    action_space = ActionSpace()

    def __init__(self, engine: Optional[HomeEngine] = None, **kwargs):
        super().__init__()
        if engine is not None:
            assert len(kwargs) == 0, f"can not specify both engine and arguments of engine"
        self._engine = HomeEngine(**kwargs) if engine is None else engine

    @property
    def engine(self) -> HomeEngine:
        return self._engine

    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[Observation, Dict]:
        return Observation(), {}

    def step(self, action: Union[Action, Dict]):
        # wrap action
        if isinstance(action, dict):
            action = Action.from_dict(action)

        # run action
        result = action(self.engine)

        # check task
        effected_tasks = []
        _add_effect_task = lambda _, task: effected_tasks.append(task.id)
        with self._engine.task.make_sniffer(_add_effect_task):
            self._engine.task.verify_all()

        # return
        observation = Observation(
            action=action.to_dict(),
            stdout=result.stdout,
            stderr=result.stderr,
            error=result.error,
            effected_tasks = None if len(effected_tasks) == 0 else effected_tasks
        )
        return observation, 0.0, False, False, {}

    def copy(self) -> "HomeEnv":
        return type(self).from_dict(self.to_dict())

    def to_dict(self) -> Dict:
        return {'engine': self.engine.to_dict()}

    @classmethod
    def from_dict(cls, data: Dict) -> "HomeEnv":
        return cls(engine=HomeEngine.from_dict(data['engine']))

    @staticmethod
    def make(name="HomeEnv-v0", **kwargs) -> "HomeEnv":
        return gym.make(name, **kwargs)



register(
    id='TradeEnv-v0',
    entry_point='tradegym.env.env:TradeEnv',
    order_enforce=False,
    disable_env_checker=True,
)