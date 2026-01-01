from typing import Optional, Dict, Sequence, Union
from abc import abstractmethod, ABC



__all__ = ["TObject"]


class TObject(ABC):
    @classmethod
    def from_dict(cls, data: Union[Dict, Sequence]) -> str:
        if isinstance(data, (tuple, list)):
            return cls(*data)
        else:
            return cls(**data)

    @abstractmethod
    def to_dict(self) -> Dict:
        pass


    def copy(self) -> "TObject":
        return type(self).from_dict(self.to_dict())
