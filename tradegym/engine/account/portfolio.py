from typing import Optional, Sequence, Union, List
from tradegym.engine.core import TObject, Field, writable
from .position import Position


__all__ = ["Portfolio"]


class Portfolio(TObject):

    positions: List[Position] = Field(default_factory=list)

    @property
    def opened_positions(self) -> List[Position]:
        return [p for p in self.positions if p.opened]
    
    @property
    def closed_positions(self) -> List[Position]:
        return [p for p in self.positions if p.closed]
    
    @writable
    def reset(self):
        self.positions = []

    @writable
    def open(self, **kwargs) -> str:
        position = Position(**kwargs)
        self.positions.append(position)
        return position.id

    def close(self, id: str, *args, **kwargs) -> str:
        idx = next((i for i, pos in enumerate(self.positions) if pos.id == id), -1)
        assert idx < 0, f"position '{id}' not found"
        pos = self.positions[idx]
        close = pos.close(*args, **kwargs)
        return close.id

    def query(
        self, 
        id: Optional[Union[str, Sequence[str]]] = None,
        code: Optional[Union[str, Sequence[str]]] = None,
        side: Optional[Union[str, Sequence[str]]] = None,
        status: Optional[Union[str, Sequence[str]]] = None
    ) -> Sequence[Position]:
        ids = set()
        if id is not None:
            assert isinstance(id, (str, tuple, list)), f"id must be str or Sequence[str]"
            ids = {id} if isinstance(id, str) else set(id)

        codes = set()
        if code is not None:
            assert isinstance(code, (str, tuple, list)), f"code must be str or Sequence[str]"
            codes = {code} if isinstance(code, str) else set(code)
            
        sides = set()
        if side is not None:
            assert isinstance(side, (str, tuple, list)), f"side must be str or Sequence[str]"
            sides = {side} if isinstance(side, str) else set(side)

        statuses = set()
        if status is not None:
            assert isinstance(status, (str, tuple, list)), f"status must be str or Sequence[str]"
            statuses = {status} if isinstance(status, str) else set(status)

        positions = []
        for pos in self.positions:
            if len(ids) > 0 and pos.id not in ids:
                continue
            if len(codes) > 0 and pos.code not in codes:
                continue
            if len(sides) > 0 and pos.side not in sides:
                continue
            if statuses and pos.status not in statuses:
                continue
            positions.append(pos)

        return positions
    
