from typing import Optional, Sequence
from tradegym.engine.core import Plugin
from .contract import Contract


__all__ = ["ContractManager"]



class ContractManager(Plugin):
    def __init__(self, contracts: Optional[Sequence[Contract]] = None):
        self._contracts = []
        self._contract_map = {}
        if contracts is not None:
            for contract in contracts:
                self.add_contract(contract)

    @property
    def contracts(self) -> Sequence[Contract]:
        return self._contracts
    
    def add_contract(self, contract: Contract) -> None:
        assert contract.code not in self._contract_map, ValueError(f"Contract code '{contract.code}' already exists")
        self._contracts.append(contract)
        self._contract_map[contract.code] = contract

    def to_dict(self):
        d = super().to_dict()
        d.update(contracts = [c.to_dict() for c in self.contracts])
        return d
    

Plugin.register(ContractManager)