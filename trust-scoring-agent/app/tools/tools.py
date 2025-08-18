from typing import Annotated, List
from langchain_core.tools import tool
from .contract import Contract

def get_tools(rpc_url: str, token_contract_address: str, scoring_contract_address: str, private_key: str) -> List[tool]:

    contract = Contract(
        rpc_url=rpc_url,
        token_contract_address=token_contract_address,
        scoring_contract_address=scoring_contract_address,
        private_key=private_key
    )

    @tool
    def regist_score(
        address: Annotated[str, "The address to register the score for"]
    ) -> None:
        """
        Register a score for a specific address.
        """
        return contract.regist_score(address)

    @tool
    def get_score(
        address: Annotated[str, "The address to get the score for"]
    ) -> int:
        """
        Get the score for a specific address.

        Returns:
            Score (int): The score for the specified address.
        """
        return contract.get_score(address)

    return [
        regist_score,
        get_score
    ]
