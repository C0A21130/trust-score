from typing import Annotated, List, Tuple
from langchain_core.tools import tool
from tools.contract import Contract
from tools.engine import Engine

def get_tools(rpc_url: str, url: str, token_contract_address: str, scoring_contract_address: str, private_key: str) -> List[tool]:

    contract = Contract(
        rpc_url=rpc_url,
        token_contract_address=token_contract_address,
        scoring_contract_address=scoring_contract_address,
        private_key=private_key
    )

    engine = Engine(url=url)

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
    
    @tool
    def predict_score(
        address: Annotated[str, "The user address to predict the score for"],
        contract_address: Annotated[str, "The contract address for collection"]
    ) -> Tuple[float, float]:
        """
        Original score and predict score for a specific address.

        Returns:
            float: The trust score,
            float: The predicted trust score
        """
        centrality, predict_centrality =  engine.predict_score(contract_address=contract_address)
        try:
            return centrality[address], predict_centrality[address]
        except KeyError:
            return 0.0, 0.0

    return [ regist_score, get_score, predict_score]
