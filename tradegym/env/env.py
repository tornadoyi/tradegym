from typing import Optional, Dict, Any, Tuple, Union, ClassVar
import gymnasium as gym
from gymnasium.envs.registration import register, EnvSpec
from tradegym.engine import TradeEngine, TObject, Field, Formula
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
        
        # update unrealized pnl
        self.update_unrealized_pnls()

        # return
        observation = Observation.deserialize(result.serialize())
        return observation, 0.0, self.engine.terminated, False, {}

    def update_unrealized_pnls(self):
        # calculate unrealized pnls
        unrealized_pnls = {}
        for position in self.engine.account.portfolio.opened_positions:
            contract = self.engine.contract.get_contract(position.code)
            last_price = self.engine.kline.get_kline(position.code).quote.last_price
            unrealized_pnls.setdefault(position.code, 0.0)
            unrealized_pnls[position.code] += Formula.position_unrealized_pnl(position.price, position.volume, position.side, contract.multiplier, last_price)
        
        # update
        for code, pnl in unrealized_pnls.items():
            self.engine.account.wallet.update_unrealized_pnl(code, pnl)

    @staticmethod
    def make(name="TradeEnv-v0", **kwargs) -> "TradeEnv":
        return gym.make(name, **kwargs)



register(
    id='TradeEnv-v0',
    entry_point='tradegym.env.env:TradeEnv',
    order_enforce=False,
    disable_env_checker=True,
)