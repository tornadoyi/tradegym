from typing import Optional, Dict, Any, Tuple, Union, ClassVar
import gymnasium as gym
from gymnasium.envs.registration import register, EnvSpec
from tradegym.engine import TradeEngine, TObject, Field
from .action import Action, ActionSpace, ActionResult
from .obs import ObservationSpace, Observation


__all__ = ['TradeEnv']



class TradeEnv(TObject, gym.Env):

    observation_space: ClassVar[ObservationSpace] = ObservationSpace()
    action_space: ClassVar[ActionSpace] = ActionSpace()
    spec: ClassVar[Optional[EnvSpec]] = None

    engine: TradeEngine = Field()

    def __init__(self, engine: Optional[TradeEngine] = None, **kwargs):
        engine = TradeEngine(**kwargs) if engine is None else engine
        TObject.__init__(self, engine=engine)
        gym.Env.__init__(self)
    
    @property
    def terminated(self) -> bool:
        return self.engine.terminated

    def activate(self, *args, **kwargs):
        self.engine.activate(*args, **kwargs)

    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[Observation, Dict]:
        # activate
        if options is not None:
            self.activate(**options)

        # reset
        self.engine.reset()

        return Observation(), {}

    def step(self, action: Union[Action, Dict]):
        if self.terminated:
            raise RuntimeError("Can not step a terminated environment")

        # wrap action
        if isinstance(action, dict):
            action = Action.make(**action)

        # run action
        result: ActionResult = action(self.engine)

        # tick
        self.engine.tick()

        # return
        observation = Observation.deserialize(result.serialize())
        return observation, 0.0, self.engine.terminated, False, {}

    @staticmethod
    def make(name="TradeEnv-v0", **kwargs) -> "TradeEnv":
        return gym.make(name, **kwargs)



register(
    id='TradeEnv-v0',
    entry_point='tradegym.env.env:TradeEnv',
    order_enforce=False,
    disable_env_checker=True,
)