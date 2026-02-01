from typing import Optional, List, ClassVar, Dict
from tradegym.engine.core import Plugin, PrivateAttr, computed_property
from .contract import Contract


__all__ = ["ContractManager"]



class ContractManager(Plugin):
    Name: ClassVar[str] = "contract"

    _contracts: List[Contract] = PrivateAttr(default_factory=list)
    _contract_map: Dict[str, Contract] = PrivateAttr(default_factory=dict)

    def __init__(self, contracts: Optional[List[Contract]] = None):
        super().__init__()
        if contracts is not None:
            for arg in contracts:
                contract = arg if isinstance(arg, Contract) else Contract.from_dict(arg)
                self.add_contract(contract)

    @computed_property
    def contracts(self) -> List[Contract]:
        return self._contracts
    
    def add_contract(self, contract: Contract) -> None:
        assert contract.code not in self._contract_map, ValueError(f"Contract code '{contract.code}' already exists")
        self._contracts.append(contract)
        self._contract_map[contract.code] = contract

    def get_contract(self, code: str) -> Contract:
        contract = self._contract_map.get(code)
        assert contract is not None, ValueError(f"Contract '{code}' not found")
        return contract

    

Plugin.register(ContractManager)