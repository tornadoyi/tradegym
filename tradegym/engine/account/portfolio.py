from typing import Optional, Sequence, Union
from tradegym.engine.core import ISerializer
from .position import Position


__all__ = ["Portfolio"]


class Portfolio(ISerializer):
    def __init__(self, positions: Optional[Sequence[Position]] = None):
        self._positions = [] if positions is None else positions
        self._closed_positions = [p for p in positions if p.quantity == 0]

    @property
    def positions(self) -> Sequence[Position]:
        return self._positions

    @property
    def opened_positions(self) -> Sequence[Position]:
        return [p for p in self._positions if p.opened]
    
    @property
    def closed_positions(self) -> Sequence[Position]:
        return [p for p in self._positions if p.closed]
    
    def query(
        self, 
        contract_code: Optional[Union[str, Sequence[str]]] = None,
        position_type: Optional[Union[str, Sequence[str]]] = None,
        status: Optional[Union[str, Sequence[str]]] = None
    ):
        contract_codes = set()
        if contract_code is not None:
            assert isinstance(contract_code, (str, tuple, list)), f"contract_code must be str or Sequence[str]"
            contract_codes = {contract_code} if isinstance(contract_code, str) else set(contract_code)
            
        position_types = set()
        if position_type is not None:
            assert isinstance(position_type, (str, tuple, list)), f"position_type must be str or Sequence[str]"
            position_types = {position_type} if isinstance(position_type, str) else set(position_type)

        statuses = set()
        if status is not None:
            assert isinstance(status, (str, tuple, list)), f"status must be str or Sequence[str]"
            statuses = {status} if isinstance(status, str) else set(status)

        positions = []
        for pos in self._positions:
            if len(contract_codes) > 0 and pos.contract_code not in contract_codes:
                continue
            if len(position_types) > 0 and pos.position_type not in position_types:
                continue
            if statuses and pos.status not in statuses:
                continue
            positions.append(pos)

        return positions
    
    def to_dict(self) -> dict:
        return {
            "positions": [p.to_dict() for p in self._positions],
        }