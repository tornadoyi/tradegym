from typing import Optional, List, ClassVar, Dict
from tradegym.engine.core import Plugin, Field
from .contract import Contract


__all__ = ["ContractManager"]



class ContractManager(Plugin):
    Name: ClassVar[str] = "contract"

    contracts: List[Contract] = Field(default_factory=list)
    contract_map: Dict[str, Contract] = Field(default_factory=dict, exclude=True)

    def __init__(self, contracts: Optional[List[Contract]] = None):
        super().__init__()
        if contracts is not None:
            for contract in contracts:
                self.add_contract(contract)

    
    def add_contract(self, contract: Contract) -> None:
        assert contract.code not in self.contract_map, ValueError(f"Contract code '{contract.code}' already exists")
        self.contracts.append(contract)
        self.contract_map[contract.code] = contract

    def get_contract(self, code: str) -> Contract:
        contract = self.contract_map.get(code)
        assert contract is not None, ValueError(f"Contract '{code}' not found")
        return contract

    