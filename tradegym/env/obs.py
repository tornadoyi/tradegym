from typing import Optional, Dict, Sequence
import gymnasium as gym


__all__ = ['Observation', 'ObservationSpace']


class Observation(object):
    def __init__(
        self,
        action: Optional[Dict] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        error: Optional[Exception] = None,
        effected_tasks: Optional[Sequence[str]] = None
    ):
        self._action = action
        self._stdout = stdout
        self._stderr = stderr
        self._error = error
        self._effected_tasks = effected_tasks

    @property
    def action(self) -> Optional[Dict]:
        return self._action

    @property
    def stdout(self) -> Optional[str]:
        return self._stdout

    @property
    def stderr(self) -> Optional[str]:
        return self._stderr

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    @property
    def effected_tasks(self) -> Optional[Sequence[str]]:
        return self._effected_tasks

    @property
    def output(self) -> str:
        outs = []
        if self._stdout is not None:
            outs.append(self.stdout)
        if self._stderr is not None:
            outs.append(self.stderr)
        return "\n".join(outs)



class ObservationSpace(gym.spaces.Space):
    def __init__(self):
        super().__init__(shape=None, dtype=Observation)

    def sample(self) -> Observation:
        return Observation()

    def contains(self, x):
        return isinstance(x, Observation)