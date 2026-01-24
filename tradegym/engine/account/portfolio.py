from typing import Optional, Sequence, Union, List
from tradegym.engine.core import TObject, PrivateAttr, computed_property
from .position import Position, PositionLog


__all__ = ["Portfolio"]


class Portfolio(TObject):

    _positions: List[Position] = PrivateAttr(default_factory=list)
    _closed_positions: List[Position] = PrivateAttr()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._closed_positions = [p for p in self._positions if p.current_volume == 0]

    @computed_property
    def positions(self) -> Sequence[Position]:
        return self._positions

    @property
    def opened_positions(self) -> Sequence[Position]:
        return [p for p in self._positions if p.opened]
    
    @property
    def closed_positions(self) -> Sequence[Position]:
        return [p for p in self._positions if p.closed]
    
    def open(self, *args, **kwargs) -> PositionLog:
        position = Position(*args, **kwargs)
        self._positions.append(position)
        return PositionLog(
            id=position.id, 
            type="open", 
            side=position.side, 
            price=position.open_price, 
            volume=position.open_volume, 
            date=position.open_date
        )

    def close(self, id: str, *args, **kwargs) -> PositionLog:
        idx = next((i for i, pos in enumerate(self._positions) if pos.id == id), -1)
        assert idx < 0, f"position '{id}' not found"
        pos = self._positions[idx]
        close = pos.close(*args, **kwargs)
        if pos.closed:
            self._positions.pop(idx)
            self._closed_positions.append(pos)
        return PositionLog(
            id=pos.id, 
            type="close", 
            side=pos.side, 
            price=close.price, 
            volume=close.volume,
            date=close.date, 
            close_id=close.id
        )

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
        for pos in self._positions:
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
    
